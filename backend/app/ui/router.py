from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/ui/templates")


@router.get("/ui", response_class=HTMLResponse)
def ui_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/ui/ai", response_class=HTMLResponse)
def ui_ai(request: Request):
    return templates.TemplateResponse("ai.html", {"request": request})