
import pytest
from flaskr import app


# /models/<db>/ alpha
def test_models_db_alpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=alpha")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=alpha")
    html = landing.data.decode()

# /models/<db>/ ralpha
def test_models_db_ralpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=ralpha")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=ralpha")
    html = landing.data.decode()

# /models/<db>/ id
def test_models_db_id():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=id")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=id")
    html = landing.data.decode()

# /models/<db>/ rid
def test_models_db_rid():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=rid")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=rid")
    html = landing.data.decode()

# /models/<db>/ date
def test_models_db_date():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=date")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=date")
    html = landing.data.decode()

# /models/<db>/ rdate
def test_models_db_rdate():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=rdate")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=rdate")
    html = landing.data.decode()

# /models/<db>/ most
def test_models_db_most():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=most")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=most")
    html = landing.data.decode()

# /models/<db>/ least
def test_models_db_least():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=least")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=least")
    html = landing.data.decode()

# /models/<db>/?page=2
def test_models_db_page2():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?page=2")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?page=2")
    html = landing.data.decode()

# /models/<db>/id?order=alpha
def test_models_db_id_alpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls/7?order=alpha")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/7/?order=alpha")
    html = landing.data.decode()

# /models/<db>/id?order=ralpha
def test_models_db_id_ralpha():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls/7?order=ralpha")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/7/?order=ralpha")
    html = landing.data.decode()

# /models/<db>/id?order=date
def test_models_db_id_date_excp():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls/7?order=date")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/7/?order=date")
    html = landing.data.decode()

# /models/<db>/id?order=rdate
def test_models_db_id_rdate_excp():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls/7?order=rdate")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/7/?order=rdate")
    html = landing.data.decode()

# /models/<db>/id?order=date
def test_models_db_id_date():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/playboyplus/7?order=date")
    html = landing.data.decode()
    landing = client.get("/models/playboyplus/7/?order=date")
    html = landing.data.decode()

# /models/<db>/id?order=rdate
def test_models_db_id_rdate():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/playboyplus/7?order=rdate")
    html = landing.data.decode()
    landing = client.get("/models/playboyplus/7/?order=rdate")
    html = landing.data.decode()

# /models/<db>/order=platest
def test_models_db_platest():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=platest")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=platest")
    html = landing.data.decode()

# /models/<db>/order=rplatest
def test_models_db_rplatest():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=rplatest")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=rplatest")
    html = landing.data.decode()

# /models/<db>/order=vlatest
def test_models_db_vlatest():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=vlatest")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=vlatest")
    html = landing.data.decode()

# /models/<db>/order=rvlatest
def test_models_db_rvlatest():
    """"""
    app.testing = True
    client = app.test_client()
    landing = client.get("/models/kindgirls?order=rvlatest")
    html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=rvlatest")
    html = landing.data.decode()
