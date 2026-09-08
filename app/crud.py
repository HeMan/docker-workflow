from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Todo


async def list_todos(db: AsyncSession) -> list[Todo]:
    result = await db.execute(select(Todo).order_by(Todo.created_at))
    return list(result.scalars().all())


async def create_todo(db: AsyncSession, title: str) -> Todo:
    todo = Todo(title=title)
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


async def complete_todo(db: AsyncSession, todo_id: int) -> Todo | None:
    todo = await db.get(Todo, todo_id)
    if todo is None:
        return None
    todo.completed = True
    await db.commit()
    await db.refresh(todo)
    return todo
