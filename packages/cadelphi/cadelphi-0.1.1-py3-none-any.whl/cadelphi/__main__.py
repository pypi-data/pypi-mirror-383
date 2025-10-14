from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run("cadelphi.app:app", host="0.0.0.0", port=7882, reload=False)


if __name__ == "__main__":
    main()
