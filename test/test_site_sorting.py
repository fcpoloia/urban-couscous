
import pytest
from flaskr import app

app.testing = True
client = app.test_client()

# /sites/<db>/ alpha
def test_sites_db_alpha():
    """"""
    landing = client.get("/sites/kindgirls/?sort=alpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/ ralpha
def test_sites_db_ralpha():
    """"""
    landing = client.get("/sites/kindgirls/?sort=ralpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/ id
def test_sites_db_id():
    """"""
    landing = client.get("/sites/kindgirls/?sort=id")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/ rid
def test_sites_db_rid():
    """"""
    landing = client.get("/sites/kindgirls/?sort=rid")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/ date
def test_sites_db_date():
    """"""
    landing = client.get("/sites/kindgirls/?sort=date")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/ rdate
def test_sites_db_rdate():
    """"""
    landing = client.get("/sites/kindgirls/?sort=rdate")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/?page=2
def test_sites_db_page2():
    """"""
    landing = client.get("/sites/kindgirls/?page=2")
    html = landing.data.decode()
    assert landing.status_code == 200
