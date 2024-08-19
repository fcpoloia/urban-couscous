
import pytest
from flaskr import app

app.testing = True
client = app.test_client()

def test_invalid_db():
    """"""
    landing = client.get("/models/invalid/")
    html = landing.data.decode()
    assert "Database [invalid] cannot be found" in html
    assert landing.status_code == 500

#def test_invalid_db_2():
#    """"""
#    landing = client.get("/models/invalid")
#    html = landing.data.decode()
#    assert "You should be redirected" in html
#    assert landing.status_code == 200

def test_error_404():
    """"""
    landing = client.get("/error/invalid/")
    html = landing.data.decode()
    assert "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again." in html
    assert landing.status_code == 404

def test_invalid_model():
    """"""
    landing = client.get("/models/kindgirls/-1")
    html = landing.data.decode()
    assert landing.status_code == 200

def test_test_path():
    """"""
    landing = client.get("/path/to/file/")
    html = landing.data.decode()
    assert landing.status_code == 200

