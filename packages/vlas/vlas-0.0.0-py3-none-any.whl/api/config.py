import os
from typing import Optional
import dotenv

dotenv.load_dotenv()

ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")


def get_admin_api_key() -> str | None:
    return ADMIN_API_KEY
