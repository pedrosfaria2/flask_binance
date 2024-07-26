import pytest
from app import create_app, socketio


@pytest.fixture
def app():
    app = create_app()
    return app


def test_app_creation(app):
    assert app is not None
    assert app.config['TESTING'] is False
    assert 'main' in app.blueprints


def test_socketio_integration(app):
    assert socketio.server is not None
    assert socketio.server.async_mode == 'threading'
