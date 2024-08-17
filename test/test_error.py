
import pytest
from flaskr import app


def test_invalid_db():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/invalid/")
    html = landing.data.decode()
    landing = client.get("/models/invalid")
    html = landing.data.decode()

def test_error_404():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/error/invalid/")
    html = landing.data.decode()

def test_invalid_model():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls/-1")
    html = landing.data.decode()

def test_test_path():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/path/to/file/")
    html = landing.data.decode()

