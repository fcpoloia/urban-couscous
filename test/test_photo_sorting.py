
import pytest
from flaskr import app


# /photos/<db>/ alpha
def test_photos_db_alpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls?sort=alpha")
    html = landing.data.decode()

# /photos/<db>/ ralpha
def test_photos_db_ralpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls?sort=ralpha")
    html = landing.data.decode()

# /photos/<db>/ id
def test_photos_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls?sort=id")
    html = landing.data.decode()

# /photos/<db>/ rid
def test_photos_db_rid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls?sort=rid")
    html = landing.data.decode()

# /photos/<db>/ date
def test_photos_db_date():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls?sort=date")
    html = landing.data.decode()

# /photos/<db>/ rdate
def test_photos_db_rdate():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls?sort=rdate")
    html = landing.data.decode()

# /photos/<db>/?page=2
def test_photos_db_page2():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls?page=2")
    html = landing.data.decode()
