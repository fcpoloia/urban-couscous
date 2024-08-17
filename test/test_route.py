
import pytest
from flaskr import app


# /
def test_root():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/")
    html = landing.data.decode()
    #landing = client.get("")
    #html = landing.data.decode()

    # check some content

    assert "<h3>Old Sets</h3>" in html
    assert "<h3>New Sets</h3>" in html

    # We can also check that the request was successful (indicated by a response code of 200):

    assert landing.status_code == 200


# "/favicon.ico")
# "/android-chrome-512x512.png")
# "/android-chrome-192x192.png")
def test_favicon():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/favicon.ico")
    html = landing.data.decode()

    landing = client.get("/android-chrome-512x512.png")
    html = landing.data.decode()

    landing = client.get("/android-chrome-192x192.png")
    html = landing.data.decode()


# /models/<db>/
def test_models_db():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls/")
    html = landing.data.decode()

# /models/<db>/<id>
def test_models_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls/7")
    html = landing.data.decode()

# /sites/<db>/
def test_sites_db():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls/")
    html = landing.data.decode()

# /sites/<db>/<id>
def test_sites_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/sites/kindgirls/13")
    html = landing.data.decode()

# /videos/<db>/
def test_videos_db():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls/")
    html = landing.data.decode()

# /videos/<db>/<id>
def test_videos_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls/218")
    html = landing.data.decode()

# /photos/<db>/
def test_photos_db():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls/")
    html = landing.data.decode()

# /photos/<db>/<id>
def test_photos_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls/4502")
    html = landing.data.decode()

# /photos/<db>/model/<mid>/<pid>
def test_photos_db_model_mid_pid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls/model/7/4502")
    html = landing.data.decode()

# /photos/<db>/site/<sid>/<pid>
def test_photos_db_site_sid_pid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/photos/kindgirls/site/13/2584")
    html = landing.data.decode()

# /videos/<db>/model/<mid>/<pid>
def test_videos_db_model_mid_pid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls/model/7/218")
    html = landing.data.decode()

# /videos/<db>/site/<sid>/<pid>
def test_videos_db_site_sid_pid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/videos/kindgirls/site/16/329")
    html = landing.data.decode()

# /random/<db>
def test_random_db():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/random/kindgirls/")
    html = landing.data.decode()
    landing = client.get("/random/kindgirls")
    html = landing.data.decode()

# /search/<db>?search=<term>
def test_search_db():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/search/kindgirls?search=scan")
    html = landing.data.decode()
    landing = client.get("/search/kindgirls/?search=scan")
    html = landing.data.decode()

# /random
def test_random_all():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/random")
    html = landing.data.decode()
    landing = client.get("/random/")
    html = landing.data.decode()

# /search/<term>
def test_search_all():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/search?search=scan")
    html = landing.data.decode()
    landing = client.get("/search/?search=scan")
    html = landing.data.decode()

# "/fs/<path:subpath>"
def test_fs_subpath():
    """"""
    import os
    home = os.environ["HOME"]
    app.testing = True
    client = app.test_client()
    landing = client.get(f"/fs{home}")
    html = landing.data.decode()

# "/fs"
# "/fs/"
def test_fs():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/fs")
    html = landing.data.decode()

    landing = client.get("/fs/")
    html = landing.data.decode()
