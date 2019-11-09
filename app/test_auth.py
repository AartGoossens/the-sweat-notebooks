import pytest

import auth
from config import ADMIN_IDS


def test_jwt_cookie_authentication():
    jwt_token = auth.create_jwt_token('some sub')
    response = auth.jwt_cookie_authentication(jwt_token=jwt_token)

    assert response['sub'] == 'some sub'
    assert response['is_authenticated'] == True
    assert response['is_admin'] == False


def test_jwt_cookie_authentication_admin():
    jwt_token = auth.create_jwt_token(ADMIN_IDS[0])
    response = auth.jwt_cookie_authentication(jwt_token=jwt_token)

    assert response['sub'] == ADMIN_IDS[0]
    assert response['is_authenticated'] == True
    assert response['is_admin'] == True

def test_jwt_cookie_authentication_invalid():
    jwt_token = auth.create_jwt_token(ADMIN_IDS[0])
    header, payload, signature = jwt_token.split('.')
    payload += 'let\'s make it invalid'
    jwt_token = '.'.join([header, payload, signature])

    response = auth.jwt_cookie_authentication(jwt_token=jwt_token)

    assert response['sub'] == None
    assert response['is_authenticated'] == False
    assert response['is_admin'] == False
