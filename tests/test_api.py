from httpx import AsyncClient


async def test_list_todos_empty(client: AsyncClient) -> None:
    response = await client.get("/api/todos")
    assert response.status_code == 200
    assert response.json() == []


async def test_create_and_list_todo(client: AsyncClient) -> None:
    response = await client.post("/api/todos", json={"title": "Buy milk"})
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Buy milk"
    assert created["completed"] is False

    response = await client.get("/api/todos")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["id"] == created["id"]


async def test_complete_todo(client: AsyncClient) -> None:
    created = (await client.post("/api/todos", json={"title": "Walk the dog"})).json()

    response = await client.post(f"/api/todos/{created['id']}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True


async def test_complete_unknown_todo_404s(client: AsyncClient) -> None:
    response = await client.post("/api/todos/999999/complete")
    assert response.status_code == 404


async def test_create_todo_rejects_blank_title(client: AsyncClient) -> None:
    response = await client.post("/api/todos", json={"title": ""})
    assert response.status_code == 422
