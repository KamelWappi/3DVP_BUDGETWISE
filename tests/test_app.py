import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import app



def test_home():
    tester = app.test_client()
    response = tester.get("/")
    assert response.status_code == 200


def test_revenus():
    tester = app.test_client()
    response = tester.get("/revenus")
    assert response.status_code == 200
