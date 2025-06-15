import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import app


def test_home():
    tester = app.test_client()
    response = tester.get("/")
    assert response.status_code == 200


def test_revenus():
    tester = app.test_client()
    response = tester.get("/revenus")
    assert response.status_code == 200
