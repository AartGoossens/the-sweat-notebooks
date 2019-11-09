from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from .config import templates
from .main import app


@app.get('/')
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        context={"request": request})


@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        context={"request": request})


@app.get('/logout')
def logout():
    response = RedirectResponse('/login')
    response.delete_cookie('jwt_token')
    return response


app.mount("/static", StaticFiles(directory="/static"), name="static")
