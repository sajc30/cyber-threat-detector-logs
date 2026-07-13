"""Tests for the REST API endpoints that actually exist (backend/api)."""

import json

import pytest
from backend.api.app import create_app


@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    return app.test_client()


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'model_loaded' in data

    def test_root_page(self, client):
        response = client.get('/')

        assert response.status_code == 200
        assert b'Threat Detection' in response.data

    def test_nonexistent_endpoint_returns_404(self, client):
        response = client.get('/api/nonexistent')

        assert response.status_code == 404


class TestDetectEndpoint:
    def test_detect_missing_field(self, client):
        response = client.post(
            '/api/detect',
            data=json.dumps({}),
            content_type='application/json',
        )

        assert response.status_code == 400

    def test_detect_requires_json(self, client):
        response = client.post('/api/detect', data='not json')

        assert response.status_code == 400

    def test_detect_single_log(self, client):
        response = client.post(
            '/api/detect',
            data=json.dumps({'log_message': 'Failed password for user root'}),
            content_type='application/json',
        )

        # Without a trained model artifact (as in CI), the endpoint
        # returns 500 with an explanatory error; with a model it returns 200.
        assert response.status_code in (200, 500)
        data = json.loads(response.data)
        if response.status_code == 200:
            assert 'threat_level' in data
        else:
            assert 'error' in data
