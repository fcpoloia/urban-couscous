
import pytest
from flaskr import app


# /videos/<db>/ alpha
def test_videos_db_alpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls?sort=alpha")
    html = landing.data.decode()

# /videos/<db>/ ralpha
def test_videos_db_ralpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls?sort=ralpha")
    html = landing.data.decode()

# /videos/<db>/ id
def test_videos_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls?sort=id")
    html = landing.data.decode()

# /videos/<db>/ rid
def test_videos_db_rid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls?sort=rid")
    html = landing.data.decode()

# /videos/<db>/ date
def test_videos_db_date():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls?sort=date")
    html = landing.data.decode()

# /videos/<db>/ rdate
def test_videos_db_rdate():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls?sort=rdate")
    html = landing.data.decode()

# /videos/<db>/?page=2
def test_videos_db_page2():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls?page=2")
    html = landing.data.decode()
