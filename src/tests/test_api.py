import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_books_endpoint():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/books", headers={"X-API-KEY": "your_api_key_here"})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

@pytest.mark.asyncio
async def test_get_book_endpoint():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # First, get a book id from the list
        response = await client.get("/books", headers={"X-API-KEY": "your_api_key_here"})
        assert response.status_code == 200
        items = response.json().get("items", [])
        if not items:
            pytest.skip("No books found to test get_book endpoint.")
        book_id = items[0]["id"]
        # Now, get the book details
        response = await client.get(f"/books/{book_id}", headers={"X-API-KEY": "your_api_key_here"})
        assert response.status_code == 200
        book = response.json()
        assert book["id"] == book_id

@pytest.mark.asyncio
async def test_list_changes_endpoint():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/changes", headers={"X-API-KEY": "your_api_key_here"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
