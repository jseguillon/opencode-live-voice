import os

import uvicorn

from .api import create_app
from .config import settings


def main() -> None:
    mock = os.getenv("OLV_MOCK", "0") == "1"
    uvicorn.run(create_app(settings, mock=mock), host=settings.bind_host, port=settings.bind_port)


if __name__ == "__main__":
    main()
