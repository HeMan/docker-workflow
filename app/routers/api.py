from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.database import get_db
from app.schemas import TodoCreate, TodoRead

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("", response_model=list[TodoRead])
async def get_todos(db: AsyncSession = Depends(get_db)):
    return await crud.list_todos(db)


@router.post("", response_model=TodoRead, status_code=201)
async def post_todo(todo: TodoCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_todo(db, todo.title)


@router.post("/{todo_id}/complete", response_model=TodoRead)
async def post_complete(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await crud.complete_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
