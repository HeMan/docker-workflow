from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app import crud
from app.database import DbSession

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


@router.get("/")
async def index(request: Request, db: DbSession):
    todos = await crud.list_todos(db)
    return templates.TemplateResponse(request, "index.html", {"todos": todos})


@router.post("/todos")
async def add_todo(db: DbSession, title: str = Form(min_length=1, max_length=200)):
    await crud.create_todo(db, title)
    return RedirectResponse(url="/", status_code=303)


@router.post("/todos/{todo_id}/complete")
async def complete_todo(todo_id: int, db: DbSession):
    todo = await crud.complete_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return RedirectResponse(url="/", status_code=303)
