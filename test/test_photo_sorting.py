
import pytest
from flaskr import app

app.testing = True
client = app.test_client()

# /photos/<db>/ alpha
def test_photos_db_alpha():
    """"""
    landing = client.get("/photos/kindgirls/?sort=alpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/ ralpha
def test_photos_db_ralpha():
    """"""
    landing = client.get("/photos/kindgirls/?sort=ralpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/ id
def test_photos_db_id():
    """"""
    landing = client.get("/photos/kindgirls/?sort=id")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/ rid
def test_photos_db_rid():
    """"""
    landing = client.get("/photos/kindgirls/?sort=rid")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/ date
def test_photos_db_date():
    """"""
    landing = client.get("/photos/kindgirls/?sort=date")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/ rdate
def test_photos_db_rdate():
    """"""
    landing = client.get("/photos/kindgirls/?sort=rdate")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/?page=2
def test_photos_db_page2():
    """"""
    landing = client.get("/photos/kindgirls/?page=2")
    html = landing.data.decode()
    assert landing.status_code == 200
