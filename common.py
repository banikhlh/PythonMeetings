import random
import re
import string

REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


def generate_session_token(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def valid_email(email: str) -> bool:
    return re.fullmatch(REGEX, email) is not None
