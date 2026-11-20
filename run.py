"""Entrypoint to launch AI-901 Study Studio locally."""

from __future__ import annotations

import uvicorn

from backend.config import Settings


def main() -> None:
    settings = Settings.load()
    print(
        f"Starting AI-901 Study Studio in [{settings.overall_mode.upper()}] mode "
        f"on http://{settings.host}:{settings.port}"
    )
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
