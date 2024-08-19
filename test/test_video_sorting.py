
import pytest
from flaskr import app

app.testing = True
client = app.test_client()

# /videos/<db>/ alpha
def test_videos_db_alpha():
    """"""
    landing = client.get("/videos/kindgirls/?sort=alpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/ ralpha
def test_videos_db_ralpha():
    """"""
    landing = client.get("/videos/kindgirls/?sort=ralpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/ id
def test_videos_db_id():
    """"""
    landing = client.get("/videos/kindgirls/?sort=id")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/ rid
def test_videos_db_rid():
    """"""
    landing = client.get("/videos/kindgirls/?sort=rid")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/ date
def test_videos_db_date():
    """"""
    landing = client.get("/videos/kindgirls/?sort=date")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/ rdate
def test_videos_db_rdate():
    """"""
    landing = client.get("/videos/kindgirls/?sort=rdate")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/?page=2
def test_videos_db_page2():
    """"""
    landing = client.get("/videos/kindgirls/?page=2")
    html = landing.data.decode()
    assert landing.status_code == 200
