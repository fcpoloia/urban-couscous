
import pytest
from flaskr import app


# /sites/<db>/ alpha
def test_sites_db_alpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls?sort=alpha")
    html = landing.data.decode()

# /sites/<db>/ ralpha
def test_sites_db_ralpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls?sort=ralpha")
    html = landing.data.decode()

# /sites/<db>/ id
def test_sites_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls?sort=id")
    html = landing.data.decode()

# /sites/<db>/ rid
def test_sites_db_rid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls?sort=rid")
    html = landing.data.decode()

# /sites/<db>/ date
def test_sites_db_date():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls?sort=date")
    html = landing.data.decode()

# /sites/<db>/ rdate
def test_sites_db_rdate():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls?sort=rdate")
    html = landing.data.decode()

# /sites/<db>/?page=2
def test_sites_db_page2():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls?page=2")
    html = landing.data.decode()
