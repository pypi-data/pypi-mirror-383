from __future__ import annotations

import os
from pathlib import Path
from collections.abc import MutableMapping
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from starlette.middleware.sessions import SessionMiddleware

from .database import get_session, init_db, session_scope
from .models import (
    AdminSettings,
    Argument,
    Participant,
    SelectionSession,
    SelectionStrategy,
    Topic,
    Vote,
)
from .i18n import (
    LANGUAGE_OPTIONS,
    get_language,
    get_strategy_labels,
    get_translations,
    set_language,
)
from .sample_data import load_sample_data
from .security import ensure_csrf_token, hash_password, validate_csrf_token, verify_password
from .utils import generate_argument_sequence

FLASH_SESSION_KEY = "flash_messages"

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="cadelphi", description="Computerized Argument Delphi experimentation toolkit")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("CADELPHI_SECRET_KEY", "change-this-secret"),
    same_site="lax",
    https_only=False,
    session_cookie="cadelphi_session",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals["now"] = datetime.utcnow


def _path_for(request: Request, name: str, **params: Any) -> str:
    """Return an application-relative URL path."""
    return request.app.url_path_for(name, **params)


REMOTE_IMAGE_BASE = "https://cadelphi.optiwisdom.com/static/img/"


def _asset_url(request: Request, asset_path: str) -> str:
    """Return a static asset URL, delegating images to the CDN host."""
    normalized = asset_path.lstrip("/")
    if normalized.startswith("img/"):
        return f"{REMOTE_IMAGE_BASE}{normalized.split('/', 1)[1]}"
    return request.app.url_path_for("static", path=normalized)


def _add_flash_message(request: Request, level: str, text: str) -> None:
    messages = list(request.session.get(FLASH_SESSION_KEY, []))
    messages.append({"level": level, "text": text})
    request.session[FLASH_SESSION_KEY] = messages


def _redirect_see_other(request: Request, name: str, **params: Any) -> RedirectResponse:
    return RedirectResponse(_path_for(request, name, **params), status_code=status.HTTP_303_SEE_OTHER)


def _build_context(request: Request, **kwargs: Any) -> Dict[str, Any]:
    language = get_language(request.session)
    translations = get_translations(language)
    context: Dict[str, Any] = {
        "request": request,
        "language": language,
        "texts": translations,
        "language_options": LANGUAGE_OPTIONS,
        "strategy_labels": get_strategy_labels(language),
        "path_for": lambda name, **params: _path_for(request, name, **params),
        "asset_url": lambda asset_path: _asset_url(request, asset_path),
    }
    if request.session.get(FLASH_SESSION_KEY):
        context["messages"] = list(request.session.get(FLASH_SESSION_KEY, []))
        request.session[FLASH_SESSION_KEY] = []
    else:
        context["messages"] = []
    context.update(kwargs)
    return context


def render(
    request: Request, template_name: str, *, status_code: int = status.HTTP_200_OK, **kwargs: Any
) -> HTMLResponse:
    return templates.TemplateResponse(
        template_name,
        _build_context(request, **kwargs),
        status_code=status_code,
    )


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with session_scope() as session:
        load_sample_data(session)


@app.middleware("http")
async def set_csrf_token(request: Request, call_next):
    session_data = request.scope.get("session")
    if isinstance(session_data, MutableMapping):
        ensure_csrf_token(session_data)
    response = await call_next(request)
    return response


def _safe_redirect_target(target: Optional[str], request: Request) -> str:
    if target:
        parsed = urlparse(target)
        if not parsed.netloc and parsed.path:
            path = parsed.path if parsed.path.startswith("/") else f"/{parsed.path}"
            if parsed.query:
                path = f"{path}?{parsed.query}"
            if parsed.fragment:
                path = f"{path}#{parsed.fragment}"
            return path
    referer = request.headers.get("referer")
    if referer:
        parsed = urlparse(referer)
        current_host = request.url.hostname
        if (not parsed.netloc or parsed.hostname == current_host) and parsed.path:
            path = parsed.path
            if parsed.query:
                path = f"{path}?{parsed.query}"
            if parsed.fragment:
                path = f"{path}#{parsed.fragment}"
            return path
    return _path_for(request, "index")


@app.get("/set-language")
async def change_language(request: Request, lang: str = "en", next: Optional[str] = None):
    set_language(request.session, lang.lower())
    redirect_target = _safe_redirect_target(next, request)
    return RedirectResponse(redirect_target, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: Session = Depends(get_session)):
    topics = session.execute(select(Topic)).scalars().all()
    return render(request, "index.html", topics=topics)


@app.get("/participate", response_class=HTMLResponse)
async def participate_start(request: Request, session: Session = Depends(get_session)):
    topics = session.execute(select(Topic)).scalars().all()
    csrf_token = ensure_csrf_token(request.session)
    return render(request, "participate_start.html", topics=topics, csrf_token=csrf_token)


@app.post("/participate")
async def participate_create(
    request: Request,
    name: str = Form(""),
    topic_id: int = Form(...),
    argument_text: str = Form(""),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    if not validate_csrf_token(request.session, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    topic = session.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    participant = Participant(name=name.strip() or None)
    session.add(participant)
    session.flush()

    content = argument_text.strip()
    if content:
        session.add(Argument(topic_id=topic.id, author_id=participant.id, content=content))

    settings = session.execute(select(AdminSettings)).scalars().first()
    strategy = settings.selection_strategy if settings else SelectionStrategy.RANDOM

    sequence = generate_argument_sequence(session, topic.id, strategy, participant_id=participant.id)
    if len(sequence) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No arguments available for voting")

    selection_session = SelectionSession(
        participant_id=participant.id,
        topic_id=topic.id,
        assigned_argument_ids=sequence,
        current_step=0,
    )
    session.add(selection_session)
    session.commit()

    request.session["participant_session_id"] = selection_session.id

    return _redirect_see_other(request, "participation_session", session_id=selection_session.id)


def _get_participant_session(session: Session, session_id: int) -> SelectionSession:
    selection_session = session.execute(
        select(SelectionSession)
        .where(SelectionSession.id == session_id)
        .options(selectinload(SelectionSession.topic))
    ).scalar_one_or_none()
    if not selection_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return selection_session


@app.get("/participate/session/{session_id}", response_class=HTMLResponse)
async def participation_session(request: Request, session_id: int, session: Session = Depends(get_session)):
    stored_session_id = request.session.get("participant_session_id")
    if stored_session_id != session_id:
        return _redirect_see_other(request, "participate_start")

    selection_session = _get_participant_session(session, session_id)
    assignments: List[int] = selection_session.assigned_argument_ids or []
    total_steps = len(assignments)

    if selection_session.current_step >= total_steps:
        return render(
            request,
            "participate_complete.html",
            session=selection_session,
            topic=selection_session.topic,
        )

    argument_id = assignments[selection_session.current_step]
    argument = session.get(Argument, argument_id)
    if not argument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Argument not found")

    csrf_token = ensure_csrf_token(request.session)
    progress = f"{selection_session.current_step + 1}/{total_steps}"

    is_last = selection_session.current_step == (total_steps - 1)

    return render(
        request,
        "participate_session.html",
        argument=argument,
        selection_session=selection_session,
        progress=progress,
        csrf_token=csrf_token,
        is_last=is_last,
    )


@app.post("/participate/session/{session_id}")
async def participation_vote(
    request: Request,
    session_id: int,
    score: int = Form(...),
    comment: str = Form(""),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    if not validate_csrf_token(request.session, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    if score < 1 or score > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid score")

    stored_session_id = request.session.get("participant_session_id")
    if stored_session_id != session_id:
        return _redirect_see_other(request, "participate_start")

    selection_session = _get_participant_session(session, session_id)
    assignments: List[int] = selection_session.assigned_argument_ids or []
    total_steps = len(assignments)

    if selection_session.current_step >= total_steps:
        return _redirect_see_other(request, "participation_session", session_id=session_id)

    argument_id = assignments[selection_session.current_step]
    argument = session.get(Argument, argument_id)
    if not argument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Argument not found")

    vote = Vote(
        argument_id=argument.id,
        participant_id=selection_session.participant_id,
        score=score,
        comment=comment.strip() or None,
    )
    session.add(vote)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        return _redirect_see_other(request, "participation_session", session_id=session_id)

    selection_session.current_step += 1
    session.add(selection_session)
    session.commit()

    if selection_session.current_step >= total_steps:
        return _redirect_see_other(request, "participation_session", session_id=session_id)

    return _redirect_see_other(request, "participation_session", session_id=session_id)


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    csrf_token = ensure_csrf_token(request.session)
    return render(request, "admin_login.html", csrf_token=csrf_token, error_message=None)


@app.post("/admin/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    if not validate_csrf_token(request.session, csrf_token):
        texts = get_translations(get_language(request.session))
        return render(
            request,
            "admin_login.html",
            csrf_token=ensure_csrf_token(request.session),
            error_message=texts["error_invalid_csrf"],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    settings = session.execute(select(AdminSettings).where(AdminSettings.admin_username == username)).scalars().first()
    if not settings or not verify_password(password, settings.password_hash):
        texts = get_translations(get_language(request.session))
        return render(
            request,
            "admin_login.html",
            csrf_token=ensure_csrf_token(request.session),
            error_message=texts["error_invalid_credentials"],
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["admin_authenticated"] = True
    return _redirect_see_other(request, "admin_dashboard")


@app.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.pop("admin_authenticated", None)
    return _redirect_see_other(request, "admin_login_page")


def _require_admin(request: Request) -> Optional[RedirectResponse]:
    if not request.session.get("admin_authenticated"):
        return _redirect_see_other(request, "admin_login_page")
    return None


def _topic_hierarchy(session: Session) -> List[Dict[str, Any]]:
    topics = (
        session.execute(
            select(Topic)
            .options(
                selectinload(Topic.arguments).selectinload(Argument.votes),
                selectinload(Topic.arguments).selectinload(Argument.author),
            )
            .order_by(Topic.title)
        )
        .scalars()
        .all()
    )
    data: List[Dict[str, Any]] = []
    for topic in topics:
        arguments_data = []
        for argument in topic.arguments:
            vote_scores = [vote.score for vote in argument.votes]
            arguments_data.append(
                {
                    "argument": argument,
                    "average_score": (sum(vote_scores) / len(vote_scores)) if vote_scores else None,
                    "max_score": max(vote_scores) if vote_scores else None,
                    "min_score": min(vote_scores) if vote_scores else None,
                    "vote_count": len(vote_scores),
                }
            )
        data.append({"topic": topic, "arguments": arguments_data})
    return data


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, session: Session = Depends(get_session)):
    redirect = _require_admin(request)
    if redirect:
        return redirect

    topics_data = _topic_hierarchy(session)
    settings = session.execute(select(AdminSettings)).scalars().first()
    csrf_token = ensure_csrf_token(request.session)

    return render(
        request,
        "admin_dashboard.html",
        topics_data=topics_data,
        settings=settings,
        csrf_token=csrf_token,
    )


@app.post("/admin/topics")
async def admin_create_topic(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    redirect = _require_admin(request)
    if redirect:
        return redirect

    if not validate_csrf_token(request.session, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    language = get_language(request.session)
    texts = get_translations(language)

    cleaned_title = title.strip()
    cleaned_description = description.strip() or None

    if not cleaned_title:
        _add_flash_message(request, "error", texts["flash_invalid_topic_title"])
        return _redirect_see_other(request, "admin_dashboard")

    topic = Topic(title=cleaned_title, description=cleaned_description)
    session.add(topic)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        _add_flash_message(request, "error", texts["flash_topic_exists"].format(title=cleaned_title))
        return _redirect_see_other(request, "admin_dashboard")

    _add_flash_message(request, "success", texts["flash_topic_created"].format(title=cleaned_title))
    return _redirect_see_other(request, "admin_dashboard")


@app.post("/admin/topics/{topic_id}/delete")
async def admin_delete_topic(
    request: Request,
    topic_id: int,
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    redirect = _require_admin(request)
    if redirect:
        return redirect

    if not validate_csrf_token(request.session, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    language = get_language(request.session)
    texts = get_translations(language)

    topic = session.get(Topic, topic_id)
    if not topic:
        _add_flash_message(request, "error", texts["flash_topic_missing"])
        return _redirect_see_other(request, "admin_dashboard")

    title = topic.title
    session.delete(topic)
    session.commit()

    _add_flash_message(request, "success", texts["flash_topic_deleted"].format(title=title))
    return _redirect_see_other(request, "admin_dashboard")


@app.post("/admin/topics/{topic_id}/arguments")
async def admin_create_argument(
    request: Request,
    topic_id: int,
    content: str = Form(...),
    author_name: str = Form(""),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    redirect = _require_admin(request)
    if redirect:
        return redirect

    if not validate_csrf_token(request.session, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    language = get_language(request.session)
    texts = get_translations(language)

    topic = session.get(Topic, topic_id)
    if not topic:
        _add_flash_message(request, "error", texts["flash_topic_missing"])
        return _redirect_see_other(request, "admin_dashboard")

    cleaned_content = content.strip()
    if not cleaned_content:
        _add_flash_message(request, "error", texts["flash_invalid_argument_content"])
        return _redirect_see_other(request, "admin_dashboard")

    participant = Participant(name=author_name.strip() or None)
    session.add(participant)
    session.flush()

    argument = Argument(topic_id=topic.id, author_id=participant.id, content=cleaned_content)
    session.add(argument)
    session.commit()

    _add_flash_message(request, "success", texts["flash_argument_created"])
    return _redirect_see_other(request, "admin_dashboard")


@app.post("/admin/arguments/{argument_id}/delete")
async def admin_delete_argument(
    request: Request,
    argument_id: int,
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    redirect = _require_admin(request)
    if redirect:
        return redirect

    if not validate_csrf_token(request.session, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    language = get_language(request.session)
    texts = get_translations(language)

    argument = session.execute(
        select(Argument)
        .where(Argument.id == argument_id)
        .options(selectinload(Argument.author))
    ).scalar_one_or_none()

    if not argument:
        _add_flash_message(request, "error", texts["flash_argument_missing"])
        return _redirect_see_other(request, "admin_dashboard")

    author_id = argument.author_id
    session.delete(argument)
    session.flush()

    if author_id:
        session.execute(delete(Vote).where(Vote.participant_id == author_id))

    session.commit()

    _add_flash_message(request, "success", texts["flash_argument_deleted"])
    return _redirect_see_other(request, "admin_dashboard")


@app.get("/admin/graph", response_class=HTMLResponse)
async def admin_graph(request: Request):
    redirect = _require_admin(request)
    if redirect:
        return redirect
    csrf_token = ensure_csrf_token(request.session)
    return render(request, "admin_graph.html", csrf_token=csrf_token)


@app.get("/admin/graph/data")
async def admin_graph_data(request: Request, metric: str = "average", session: Session = Depends(get_session)):
    if not request.session.get("admin_authenticated"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    metric = metric.lower()
    if metric not in {"average", "max", "min"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid metric")

    arguments = session.execute(select(Argument).options(selectinload(Argument.topic))).scalars().all()
    participants = session.execute(select(Participant).options(selectinload(Participant.arguments))).scalars().all()
    votes = session.execute(select(Vote)).scalars().all()

    nodes = [
        {
            "id": argument.id,
            "label": f"{argument.topic.title}: {argument.content[:60]}" + ("..." if len(argument.content) > 60 else ""),
        }
        for argument in arguments
    ]

    edges_map: Dict[tuple[int, int], List[int]] = {}
    participant_arguments: Dict[int, List[int]] = {
        participant.id: [argument.id for argument in participant.arguments]
        for participant in participants
    }

    for vote in votes:
        author_arguments = participant_arguments.get(vote.participant_id, [])
        for origin_argument_id in author_arguments:
            if origin_argument_id == vote.argument_id:
                continue
            edges_map.setdefault((origin_argument_id, vote.argument_id), []).append(vote.score)

    edges: List[Dict[str, Any]] = []
    for (source_id, target_id), scores in edges_map.items():
        edges.append(
            {
                "source": source_id,
                "target": target_id,
                "average": sum(scores) / len(scores),
                "max": max(scores),
                "min": min(scores),
            }
        )

    return JSONResponse({"nodes": nodes, "edges": edges, "metric": metric})


@app.get("/admin/graph/table-data")
async def admin_graph_table_data(request: Request, session: Session = Depends(get_session)):
    if not request.session.get("admin_authenticated"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    language = get_language(request.session)
    texts = get_translations(language)

    arguments = (
        session.execute(
            select(Argument)
            .options(
                selectinload(Argument.topic),
                selectinload(Argument.votes).selectinload(Vote.participant),
                selectinload(Argument.author),
            )
            .order_by(Argument.created_at)
        )
        .scalars()
        .all()
    )

    items: List[Dict[str, Any]] = []
    for argument in arguments:
        vote_scores = [vote.score for vote in argument.votes]
        vote_count = len(vote_scores)
        votes_payload = []
        for vote in argument.votes:
            participant_name = (
                vote.participant.name if vote.participant and vote.participant.name else texts["anonymous_label"]
            )
            votes_payload.append(
                {
                    "score": vote.score,
                    "comment": vote.comment or "",
                    "participant": participant_name,
                }
            )

        items.append(
            {
                "id": argument.id,
                "topic": argument.topic.title if argument.topic else "",
                "content": argument.content,
                "average": (sum(vote_scores) / vote_count) if vote_scores else None,
                "max": max(vote_scores) if vote_scores else None,
                "min": min(vote_scores) if vote_scores else None,
                "vote_count": vote_count,
                "votes": votes_payload,
            }
        )

    return JSONResponse({"items": items})


@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings_page(request: Request, session: Session = Depends(get_session)):
    redirect = _require_admin(request)
    if redirect:
        return redirect
    settings = session.execute(select(AdminSettings)).scalars().first()
    csrf_token = ensure_csrf_token(request.session)
    return render(
        request,
        "admin_settings.html",
        settings=settings,
        strategies=list(SelectionStrategy),
        csrf_token=csrf_token,
    )


@app.post("/admin/settings")
async def admin_settings_update(
    request: Request,
    selection_strategy: str = Form(...),
    new_password: str = Form(""),
    csrf_token: str = Form(...),
    session: Session = Depends(get_session),
):
    redirect = _require_admin(request)
    if redirect:
        return redirect

    if not validate_csrf_token(request.session, csrf_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSRF token")

    try:
        strategy = SelectionStrategy(selection_strategy)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid strategy") from exc
    settings = session.execute(select(AdminSettings)).scalars().first()
    if not settings:
        settings = AdminSettings(admin_username="admin", password_hash=hash_password("password"))
        session.add(settings)
        session.flush()

    settings.selection_strategy = strategy
    if new_password.strip():
        settings.password_hash = hash_password(new_password.strip())
    session.add(settings)
    session.commit()

    return _redirect_see_other(request, "admin_settings_page")


@app.get("/admin/graph/summary")
async def admin_graph_summary(request: Request, session: Session = Depends(get_session)):
    if not request.session.get("admin_authenticated"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    language = get_language(request.session)
    texts = get_translations(language)

    stats = session.execute(
        select(
            Argument.id,
            Argument.content,
            func.avg(Vote.score).label("avg"),
            func.max(Vote.score).label("max"),
            func.min(Vote.score).label("min"),
            func.count(Vote.id).label("count"),
        )
        .join(Vote, Vote.argument_id == Argument.id, isouter=True)
        .group_by(Argument.id)
    ).all()

    if not stats:
        return JSONResponse({"items": []})

    highest_avg = max((item for item in stats if item.avg is not None), key=lambda x: x.avg, default=None)
    highest_score = max((item for item in stats if item.max is not None), key=lambda x: x.max, default=None)
    lowest_score = min((item for item in stats if item.min is not None), key=lambda x: x.min, default=None)

    summary_items = []
    if highest_score:
        summary_items.append(
            {
                "title": texts["graph_summary_highest_vote"],
                "content": highest_score.content,
                "value": highest_score.max,
            }
        )
    if lowest_score:
        summary_items.append(
            {
                "title": texts["graph_summary_lowest_vote"],
                "content": lowest_score.content,
                "value": lowest_score.min,
            }
        )
    if highest_avg:
        summary_items.append(
            {
                "title": texts["graph_summary_best_average"],
                "content": highest_avg.content,
                "value": round(highest_avg.avg, 2),
            }
        )

    return JSONResponse({"items": summary_items})
