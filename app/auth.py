import jwt
from fastapi import Cookie
from jwt.exceptions import PyJWTError
from starlette.requests import Request

from config import ADMIN_IDS, JWT_SECRET


def create_jwt_token(sub):
    payload = dict(
        sub=sub,
        is_admin=str(sub) in set(ADMIN_IDS),
        is_authenticated=True
    )
    return jwt.encode(payload, str(JWT_SECRET), algorithm='HS256').decode('utf-8')


def get_payload(jwt_token):
    try:
        payload = jwt.decode(str.encode(jwt_token), str(JWT_SECRET), algorithms=['HS256'])
    except PyJWTError:
        return anonymous_payload()
    return payload


def anonymous_payload():
    return dict(
        sub=None,
        is_authenticated=False,
        is_admin=False
    )


def jwt_cookie_authentication(jwt_token: str = Cookie(None)):
    if jwt_token is None:
        payload = anonymous_payload()
    else:
        payload = get_payload(jwt_token)

    return payload
