from httpx import AsyncClient


async def test_index_shows_empty_state(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert "No todos yet" in response.text


async def test_add_todo_via_form(client: AsyncClient) -> None:
    response = await client.post(
        "/todos", data={"title": "Buy milk"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Buy milk" in response.text


async def test_complete_todo_via_form(client: AsyncClient) -> None:
    created = (await client.post("/api/todos", json={"title": "Walk the dog"})).json()

    response = await client.post(
        f"/todos/{created['id']}/complete", follow_redirects=True
    )
    assert response.status_code == 200
    assert 'class="completed"' in response.text


async def test_complete_unknown_todo_via_form_404s(client: AsyncClient) -> None:
    response = await client.post("/todos/999999/complete")
    assert response.status_code == 404
