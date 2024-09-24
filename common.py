import random
import string
import re
from datetime import datetime


REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def generate_session_token(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def valid_email(email: str) -> bool:
    return re.fullmatch(REGEX, email) is not None


def validate_datetime_format(datetime_str: str, format_str: str = '%Y-%m-%dT%H:%M') -> bool:
    if datetime.strptime(datetime_str, format_str):
        return False
    else:
        return True