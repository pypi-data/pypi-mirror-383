"""Simple translation helpers for the cadelphi web interface."""
from __future__ import annotations

from typing import Dict, Mapping, MutableMapping

from .models import SelectionStrategy

LANGUAGE_OPTIONS: Mapping[str, str] = {"en": "English", "tr": "Türkçe"}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "title_base": "cadelphi",
        "title_home": "cadelphi | Computerized Argument Delphi",
        "title_participate_start": "Start participation | cadelphi",
        "title_participate_session": "Argument voting | cadelphi",
        "title_participate_complete": "Thank you | cadelphi",
        "title_admin_login": "Admin sign-in | cadelphi",
        "title_admin_dashboard": "Admin dashboard | cadelphi",
        "title_admin_settings": "Settings | cadelphi",
        "title_admin_graph": "Argument graph | cadelphi",
        "hero_heading": "Experimental platform for the Computerized Argument Delphi method",
        "hero_paragraph": (
            "cadelphi helps you collect arguments from participants and rate them with a three-step "
            "Likert-scale flow inspired by CAD research published on IEEE Xplore. The system runs locally "
            "with minimal setup."
        ),
        "hero_button": "Start a participant session",
        "features_heading": "Highlights",
        "feature_adaptive_selection": "Adaptive three-step voting with random, positive affinity, or negative affinity argument sequencing.",
        "feature_storage": "Persistent SQLite storage backed by SQLAlchemy models and multilingual seed data for a quick start.",
        "feature_admin": "Admin console with hierarchical discussion views, graph visualisation, and reporting tools.",
        "feature_rating": "Star-based Likert scale, comment field, and session progress indicator.",
        "active_topics": "Active discussion topics",
        "no_topics": "No discussion topics are available yet.",
        "participation_form_heading": "Participation form",
        "participation_form_intro": "Choose a topic, optionally add a new argument, and join the three-step voting round.",
        "label_name_optional": "Your name (optional)",
        "label_topic": "Discussion topic",
        "label_argument_optional": "Your new argument (optional)",
        "argument_placeholder": "Share your perspective here",
        "start_session_button": "Begin session",
        "progress_status": "Progress: {progress}",
        "rating_heading": "Argument voting",
        "argument_heading": "Argument",
        "rating_legend": "How many stars would you give this argument?",
        "star_title": "{value} stars",
        "comment_label": "Your comment (optional)",
        "comment_placeholder": "Share your thoughts",
        "button_next_argument": "Next argument",
        "button_finish_vote": "Finish voting",
        "complete_heading": "Thank you for contributing!",
        "complete_paragraph": "You have completed the three-step voting tour. Start another round any time from the participation form.",
        "start_new_session": "Start a new session",
        "language_label": "Language",
        "nav_participant": "Participant",
        "nav_admin": "Admin",
        "admin_login_heading": "Admin sign-in",
        "username_label": "Username",
        "password_label": "Password",
        "button_sign_in": "Sign in",
        "error_invalid_credentials": "Invalid username or password.",
        "error_invalid_csrf": "Security check failed. Please refresh the page and try again.",
        "admin_dashboard_heading": "Admin dashboard",
        "button_view_graph": "Argument graph",
        "button_settings": "Settings",
        "button_logout": "Sign out",
        "active_strategy": "Active argument selection strategy: {strategy}",
        "topics_heading": "Discussion topics",
        "author_label": "Author",
        "anonymous_label": "Anonymous",
        "average_label": "Average",
        "max_label": "Highest",
        "min_label": "Lowest",
        "no_votes_label": "No votes yet",
        "vote_details_summary": "Votes and comments",
        "no_arguments_topic": "This topic has no arguments yet.",
        "no_topics_admin": "No discussion topics have been added yet.",
        "settings_heading": "System settings",
        "button_back_to_dashboard": "Back to dashboard",
        "selection_strategy_label": "Argument selection strategy",
        "new_admin_password_label": "New admin password (optional)",
        "password_hint": "Password must be at least 8 characters long.",
        "button_save_changes": "Save changes",
        "graph_heading": "Argument graph",
        "graph_metric_label": "Edge thickness metric",
        "graph_metric_average": "Average score",
        "graph_metric_max": "Highest score",
        "graph_metric_min": "Lowest score",
        "graph_summary_heading": "Summary report",
        "graph_summary_column_title": "Title",
        "graph_summary_column_argument": "Argument",
        "graph_summary_column_value": "Value",
        "graph_summary_highest_vote": "Highest vote",
        "graph_summary_lowest_vote": "Lowest vote",
        "graph_summary_best_average": "Best average",
        "graph_error_fetch": "Unable to fetch data from the server.",
        "graph_summary_error": "Unable to load summary data.",
    },
    "tr": {
        "title_base": "cadelphi",
        "title_home": "cadelphi | Bilgisayarlı Argüman Delphi",
        "title_participate_start": "Katılım Başlat | cadelphi",
        "title_participate_session": "Argüman Oylama | cadelphi",
        "title_participate_complete": "Teşekkürler | cadelphi",
        "title_admin_login": "Yönetici Girişi | cadelphi",
        "title_admin_dashboard": "Yönetici Paneli | cadelphi",
        "title_admin_settings": "Ayarlar | cadelphi",
        "title_admin_graph": "Argüman Grafiği | cadelphi",
        "hero_heading": "Bilgisayarlı Argüman Delphi yöntemi için deneysel platform",
        "hero_paragraph": (
            "cadelphi, katılımcılardan argüman toplayıp bu argümanları üç adımlı Likert ölçeğiyle oylayarak, "
            "IEEE Xplore'da yayımlanan CAD araştırmalarındaki tasarım ilkelerini yerel ortamınıza taşır."
        ),
        "hero_button": "Katılımcı oturumu başlat",
        "features_heading": "Öne çıkan özellikler",
        "feature_adaptive_selection": "Rastgele, pozitif ve negatif odaklı argüman seçim stratejileriyle uyarlanabilir üç aşamalı oylama.",
        "feature_storage": "SQLAlchemy modelleri ve çok dilli örnek verilerle desteklenen kalıcı SQLite depolama.",
        "feature_admin": "Çok kırılımlı tartışma görünümü, graf görselleştirmesi ve raporlama araçları sunan yönetici konsolu.",
        "feature_rating": "Yıldız tabanlı Likert ölçeği, yorum alanı ve oturum ilerleme göstergesi.",
        "active_topics": "Aktif tartışma konuları",
        "no_topics": "Henüz tanımlı tartışma konusu yok.",
        "participation_form_heading": "Katılım formu",
        "participation_form_intro": "Bir tartışma konusu seçin, isteğe bağlı olarak yeni bir argüman ekleyin ve üç aşamalı oylamaya katılın.",
        "label_name_optional": "Adınız (isteğe bağlı)",
        "label_topic": "Tartışma konusu",
        "label_argument_optional": "Yeni argümanınız (isteğe bağlı)",
        "argument_placeholder": "Görüşünüzü buraya yazın",
        "start_session_button": "Oturumu başlat",
        "progress_status": "İlerleme: {progress}",
        "rating_heading": "Argüman oylaması",
        "argument_heading": "Argüman",
        "rating_legend": "Bu argümana kaç yıldız verirsiniz?",
        "star_title": "{value} yıldız",
        "comment_label": "Yorumunuz (isteğe bağlı)",
        "comment_placeholder": "Düşüncelerinizi paylaşın",
        "button_next_argument": "Sonraki argümana geç",
        "button_finish_vote": "Oylamayı tamamla",
        "complete_heading": "Katkınız için teşekkürler!",
        "complete_paragraph": "Üç adımlı oylamayı tamamladınız. İstediğiniz zaman katılım formundan yeni bir tur başlatabilirsiniz.",
        "start_new_session": "Yeni oturum başlat",
        "language_label": "Dil",
        "nav_participant": "Katılımcı",
        "nav_admin": "Yönetici",
        "admin_login_heading": "Yönetici girişi",
        "username_label": "Kullanıcı adı",
        "password_label": "Şifre",
        "button_sign_in": "Giriş yap",
        "error_invalid_credentials": "Kullanıcı adı veya şifre hatalı.",
        "error_invalid_csrf": "Güvenlik doğrulaması başarısız oldu. Lütfen sayfayı yenileyip tekrar deneyin.",
        "admin_dashboard_heading": "Yönetici paneli",
        "button_view_graph": "Argüman grafiği",
        "button_settings": "Ayarlar",
        "button_logout": "Çıkış yap",
        "active_strategy": "Aktif argüman seçim algoritması: {strategy}",
        "topics_heading": "Tartışma konuları",
        "author_label": "Yazar",
        "anonymous_label": "Anonim",
        "average_label": "Ortalama",
        "max_label": "En yüksek",
        "min_label": "En düşük",
        "no_votes_label": "Henüz oy yok",
        "vote_details_summary": "Oy ve yorumlar",
        "no_arguments_topic": "Bu konuda henüz argüman bulunmuyor.",
        "no_topics_admin": "Henüz tartışma konusu eklenmedi.",
        "settings_heading": "Sistem ayarları",
        "button_back_to_dashboard": "Panele dön",
        "selection_strategy_label": "Argüman seçim algoritması",
        "new_admin_password_label": "Yeni yönetici şifresi (isteğe bağlı)",
        "password_hint": "Şifre en az 8 karakter olmalıdır.",
        "button_save_changes": "Değişiklikleri kaydet",
        "graph_heading": "Argüman grafiği",
        "graph_metric_label": "Kenar kalınlığı metriği",
        "graph_metric_average": "Ortalama puan",
        "graph_metric_max": "En yüksek puan",
        "graph_metric_min": "En düşük puan",
        "graph_summary_heading": "Özet rapor",
        "graph_summary_column_title": "Başlık",
        "graph_summary_column_argument": "Argüman",
        "graph_summary_column_value": "Değer",
        "graph_summary_highest_vote": "En yüksek oy",
        "graph_summary_lowest_vote": "En düşük oy",
        "graph_summary_best_average": "En yüksek ortalama",
        "graph_error_fetch": "Sunucudan veri alınamadı.",
        "graph_summary_error": "Özet veriler yüklenemedi.",
    },
}

STRATEGY_LABELS: Dict[str, Dict[str, str]] = {
    "en": {
        SelectionStrategy.RANDOM.value: "Random",
        SelectionStrategy.POSITIVE.value: "Positive affinity",
        SelectionStrategy.NEGATIVE.value: "Negative affinity",
    },
    "tr": {
        SelectionStrategy.RANDOM.value: "Rastgele",
        SelectionStrategy.POSITIVE.value: "Pozitif odaklı",
        SelectionStrategy.NEGATIVE.value: "Negatif odaklı",
    },
}

DEFAULT_LANGUAGE = "en"


def get_language(session: Mapping[str, object]) -> str:
    """Return the persisted language code or default to English."""
    lang = session.get("language") if session else None
    if isinstance(lang, str) and lang in LANGUAGE_OPTIONS:
        return lang
    return DEFAULT_LANGUAGE


def set_language(session: MutableMapping[str, object], language: str) -> None:
    """Persist a supported language in the session."""
    if language in LANGUAGE_OPTIONS:
        session["language"] = language


def get_translations(language: str) -> Dict[str, str]:
    """Fetch the translation table for a language, falling back to English."""
    return TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE])


def get_strategy_labels(language: str) -> Dict[str, str]:
    """Return localized labels for selection strategies."""
    base = STRATEGY_LABELS[DEFAULT_LANGUAGE]
    selected = STRATEGY_LABELS.get(language, base)
    return {key: selected.get(key, base.get(key, key)) for key in base}
