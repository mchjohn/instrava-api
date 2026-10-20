import uvicorn

from instrava_api.main import app


def main() -> None:
    uvicorn.run("instrava_api.main:app", host="0.0.0.0", port=8000, reload=True)


__all__ = ["app", "main"]
