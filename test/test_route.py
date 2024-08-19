
import pytest
from flaskr import app

app.testing = True
client = app.test_client()

# /
def test_root():
    """"""
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
    landing = client.get("/favicon.ico")
    html = landing.data.decode()
    assert landing.status_code == 200

    landing = client.get("/android-chrome-512x512.png")
    html = landing.data.decode()
    print(f"test_favicon {html}")
    assert landing.status_code == 200

    landing = client.get("/android-chrome-192x192.png")
    html = landing.data.decode()
    assert landing.status_code == 200


# /models/<db>/
def test_models_db():
    """"""
    landing = client.get("/models/kindgirls/")
    html = landing.data.decode()
    assert "arse" in html
    assert landing.status_code == 200

# /models/<db>/<id>
def test_models_db_id():
    """"""
    landing = client.get("/models/kindgirls/7")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/
def test_sites_db():
    """"""
    landing = client.get("/sites/kindgirls/")
    html = landing.data.decode()
    assert landing.status_code == 200

# /sites/<db>/<id>
def test_sites_db_id():
    """"""
    landing = client.get("/sites/kindgirls/13")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/
def test_videos_db():
    """"""
    landing = client.get("/videos/kindgirls/")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/<id>
def test_videos_db_id():
    """"""
    landing = client.get("/videos/kindgirls/218")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/
def test_photos_db():
    """"""
    landing = client.get("/photos/kindgirls/")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/<id>
def test_photos_db_id():
    """"""
    landing = client.get("/photos/kindgirls/4502")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/model/<mid>/<pid>
def test_photos_db_model_mid_pid():
    """"""
    landing = client.get("/photos/kindgirls/model/7/4502")
    html = landing.data.decode()
    assert landing.status_code == 200

# /photos/<db>/site/<sid>/<pid>
def test_photos_db_site_sid_pid():
    """"""
    landing = client.get("/photos/kindgirls/site/13/2584")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/model/<mid>/<pid>
def test_videos_db_model_mid_pid():
    """"""
    landing = client.get("/videos/kindgirls/model/7/218")
    html = landing.data.decode()
    assert landing.status_code == 200

# /videos/<db>/site/<sid>/<pid>
def test_videos_db_site_sid_pid():
    """"""
    landing = client.get("/videos/kindgirls/site/16/329")
    html = landing.data.decode()
    assert landing.status_code == 200

# /random/<db>
def test_random_db():
    """"""
    landing = client.get("/random/kindgirls/")
    html = landing.data.decode()
    assert landing.status_code == 200

    landing = client.get("/random/kindgirls")
    html = landing.data.decode()
    assert landing.status_code == 308

# /search/<db>?search=<term>
def test_search_db():
    """"""
    landing = client.get("/search/kindgirls/?search=scan")
    html = landing.data.decode()
    assert landing.status_code == 200

    landing = client.get("/search/kindgirls?search=scan")
    html = landing.data.decode()
    assert landing.status_code == 308

# /random
def test_random_all():
    """"""
    landing = client.get("/random")
    html = landing.data.decode()
    assert landing.status_code == 200

    landing = client.get("/random/")
    html = landing.data.decode()
    assert "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again." in html
    assert landing.status_code == 404

# /search/<term>
def test_search_all():
    """"""
    landing = client.get("/search?search=scan")
    html = landing.data.decode()
    assert landing.status_code == 200

    landing = client.get("/search/?search=scan")
    html = landing.data.decode()
    assert "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again." in html
    assert landing.status_code == 404

# "/fs/<path:subpath>"
def test_fs_subpath():
    """"""
    import os
    home = os.environ["HOME"]
    landing = client.get(f"/fs{home}")
    html = landing.data.decode()
    assert landing.status_code == 200

# "/fs"
# "/fs/"
def test_fs():
    """"""
    landing = client.get("/fs")
    html = landing.data.decode()
    assert landing.status_code == 200

    landing = client.get("/fs/")
    html = landing.data.decode()
    assert landing.status_code == 200
