import pytest
from fastapi.testclient import TestClient
from src.main import app # Assuming your FastAPI app instance is in main.py
from src.api import template_router
from unittest.mock import AsyncMock, patch, MagicMock

# Mock the SupabaseManager
@pytest.fixture(autouse=True)
def mock_supabase_manager():
    with patch('src.supabase_api.SupabaseManager') as MockSupabaseManager:
        mock_instance = MockSupabaseManager.return_value
        mock_instance.get_templates = AsyncMock()
        mock_instance.create_template = AsyncMock()
        mock_instance.get_template_by_id = AsyncMock()
        mock_instance.update_template_by_id = AsyncMock()
        mock_instance.delete_template_by_id = AsyncMock()
        mock_instance.get_template_versions_by_template_id = AsyncMock()
        mock_instance.create_template_version = AsyncMock()
        mock_instance.activate_template_version = AsyncMock()
        mock_instance.add_favorite_template = AsyncMock()
        mock_instance.remove_favorite_template = AsyncMock()
        mock_instance.get_user_favorite_templates = AsyncMock()
        
        # Set the mock instance in the app state
        app.state.supabase_manager = mock_instance
        
        yield mock_instance

client = TestClient(app)

# Mock the get_current_user dependency
@pytest.fixture
def mock_current_user():
    # Create a more complete mock user similar to what Supabase would return
    mock_user = MagicMock()
    mock_user.id = "test_user_id"
    mock_user.email = "test@example.com"
    mock_user.user_metadata = {"username": "testuser"}
    mock_user.created_at = "2023-01-01T00:00:00+00:00"
    
    # For dictionary access compatibility
    mock_user.__getitem__ = lambda self, key: {
        "id": self.id,
        "email": self.email,
        "username": self.user_metadata.get("username")
    }.get(key)
    
    # Override the dependency in the app
    app.dependency_overrides[template_router.get_current_user] = lambda: mock_user
    yield mock_user
    # Clear the override after the test
    app.dependency_overrides.clear()

# Apply the fixture to all tests
@pytest.fixture(autouse=True)
def setup_auth(mock_current_user):
    yield

def test_get_templates(mock_supabase_manager):
    mock_supabase_manager.get_templates.return_value = [{"id": "1", "title": "Test Template"}]
    response = client.get("/v1/templates/")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "title": "Test Template"}]
    mock_supabase_manager.get_templates.assert_called_once_with(search_term=None, tags=None, limit=20, offset=0)

def test_create_template(mock_supabase_manager):
    template_data = {"title": "New Template", "description": "A new template"}
    mock_supabase_manager.create_template.return_value = {"id": "2", **template_data}
    response = client.post("/v1/templates/", json=template_data)
    assert response.status_code == 200
    assert response.json() == {"id": "2", **template_data}
    mock_supabase_manager.create_template.assert_called_once_with(template_data)

def test_get_template(mock_supabase_manager):
    template_id = "3"
    mock_supabase_manager.get_template_by_id.return_value = {"id": template_id, "title": "Template 3"}
    response = client.get(f"/v1/templates/{template_id}")
    assert response.status_code == 200
    assert response.json() == {"id": template_id, "title": "Template 3"}
    mock_supabase_manager.get_template_by_id.assert_called_once_with(template_id)

def test_get_template_not_found(mock_supabase_manager):
    template_id = "nonexistent_id"
    mock_supabase_manager.get_template_by_id.return_value = None
    response = client.get(f"/v1/templates/{template_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Template not found"}
    mock_supabase_manager.get_template_by_id.assert_called_once_with(template_id)

def test_update_template(mock_supabase_manager):
    template_id = "4"
    update_data = {"title": "Updated Template"}
    mock_supabase_manager.update_template_by_id.return_value = {"id": template_id, "title": "Updated Template"}
    response = client.put(f"/v1/templates/{template_id}", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"id": template_id, "title": "Updated Template"}
    mock_supabase_manager.update_template_by_id.assert_called_once_with(template_id, update_data)

def test_update_template_not_found(mock_supabase_manager):
    template_id = "nonexistent_id"
    update_data = {"title": "Updated Template"}
    mock_supabase_manager.update_template_by_id.return_value = None
    response = client.put(f"/v1/templates/{template_id}", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Template not found or failed to update"}
    mock_supabase_manager.update_template_by_id.assert_called_once_with(template_id, update_data)

def test_delete_template(mock_supabase_manager):
    template_id = "5"
    mock_supabase_manager.delete_template_by_id.return_value = True
    response = client.delete(f"/v1/templates/{template_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Template deleted successfully"}
    mock_supabase_manager.delete_template_by_id.assert_called_once_with(template_id)

def test_delete_template_not_found(mock_supabase_manager):
    template_id = "nonexistent_id"
    mock_supabase_manager.delete_template_by_id.return_value = False
    response = client.delete(f"/v1/templates/{template_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Template not found or failed to delete"}
    mock_supabase_manager.delete_template_by_id.assert_called_once_with(template_id)

def test_get_template_versions(mock_supabase_manager):
    template_id = "6"
    mock_supabase_manager.get_template_versions_by_template_id.return_value = [{"id": "v1", "template_id": template_id}]
    response = client.get(f"/v1/templates/{template_id}/versions")
    assert response.status_code == 200
    assert response.json() == [{"id": "v1", "template_id": template_id}]
    mock_supabase_manager.get_template_versions_by_template_id.assert_called_once_with(template_id)

def test_create_template_version(mock_supabase_manager):
    template_id = "7"
    version_data = {"content": "Version 1 content"}
    mock_supabase_manager.create_template_version.return_value = {"id": "v2", "template_id": template_id, **version_data}
    response = client.post(f"/v1/templates/{template_id}/versions", json=version_data)
    assert response.status_code == 200
    assert response.json() == {"id": "v2", "template_id": template_id, **version_data}
    mock_supabase_manager.create_template_version.assert_called_once_with({"template_id": template_id, **version_data})

def test_activate_template_version(mock_supabase_manager):
    template_id = "8"
    version_id = "v3"
    mock_supabase_manager.activate_template_version.return_value = {"id": version_id, "template_id": template_id, "is_active": True}
    response = client.put(f"/v1/templates/{template_id}/versions/{version_id}/activate")
    assert response.status_code == 200
    assert response.json() == {"id": version_id, "template_id": template_id, "is_active": True}
    mock_supabase_manager.activate_template_version.assert_called_once_with(version_id, template_id)

def test_like_template(mock_supabase_manager):
    template_id = "9"
    user_id = "test_user_id"
    mock_supabase_manager.add_favorite_template.return_value = {"user_id": user_id, "template_id": template_id}
    response = client.post(f"/v1/templates/{template_id}/favorite")
    assert response.status_code == 200
    assert response.json() == {"user_id": user_id, "template_id": template_id}
    mock_supabase_manager.add_favorite_template.assert_called_once_with(user_id, template_id)

def test_unlike_template(mock_supabase_manager):
    template_id = "10"
    user_id = "test_user_id"
    mock_supabase_manager.remove_favorite_template.return_value = True
    response = client.delete(f"/v1/templates/{template_id}/favorite")
    assert response.status_code == 200
    assert response.json() == {"message": "Template removed from favorites successfully"}
    mock_supabase_manager.remove_favorite_template.assert_called_once_with(user_id, template_id)

def test_get_user_favorites(mock_supabase_manager):
    user_id = "test_user_id"
    mock_supabase_manager.get_user_favorite_templates.return_value = [{"id": "11", "title": "Favorite Template"}]
    response = client.get("/v1/templates/users/me/favorites")
    assert response.status_code == 200
    assert response.json() == [{"id": "11", "title": "Favorite Template"}]
    mock_supabase_manager.get_user_favorite_templates.assert_called_once_with(user_id)