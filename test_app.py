"""
Pruebas unitarias para la aplicación FastAPI usando pytest.
"""

import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """
    Fixture que proporciona un cliente de prueba para la aplicación FastAPI.
    
    Yields:
        TestClient: Cliente para hacer peticiones a la aplicación
    """
    return TestClient(app)


class TestHomeRoute:
    """Pruebas para la ruta raíz (/) de la aplicación."""
    
    def test_home_status_code(self, client):
        """
        Verifica que la ruta raíz responde con código 200.
        
        Args:
            client: Cliente de prueba fixture
        """
        response = client.get('/')
        assert response.status_code == 200
    
    def test_home_message_content(self, client):
        """
        Verifica que el mensaje de respuesta contiene los endpoints esperados.
        
        Args:
            client: Cliente de prueba fixture
        """
        response = client.get('/')
        data = response.get_json()
        
        assert data is not None
        assert 'message' in data
        assert 'endpoints' in data
        assert isinstance(data['endpoints'], dict)


class TestDocumentationRoute:
    """Pruebas para la documentación OpenAPI."""
    
    def test_openapi_docs_status_code(self, client):
        """Verifica que la documentación OpenAPI está disponible."""
        response = client.get('/docs')
        assert response.status_code == 200
    
    def test_openapi_schema_status_code(self, client):
        """Verifica que el esquema OpenAPI está disponible."""
        response = client.get('/openapi.json')
        assert response.status_code == 200


class TestHealthRoute:
    """Pruebas para la ruta de salud (si existe en la aplicación)."""
    
    def test_app_initialization(self, client):
        """Verifica que la aplicación se inicializa correctamente."""
        # Este test asegura que la BD se puede inicializar sin errores
        response = client.get('/')
        assert response.status_code == 200
