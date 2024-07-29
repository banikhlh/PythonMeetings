from fastapi import Cookie, FastAPI, Response
from pydantic import BaseModel
import random
import string


def generate_session_token(length):
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )


app = FastAPI()


class UserCreate(BaseModel):
    username: str
    password: str


@app.get("/login")
async def login(response: Response):
    response.set_cookie(key="session_token", value=generate_session_token(10))
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)