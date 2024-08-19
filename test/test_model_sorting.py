
import pytest
from flaskr import app

app.testing = True
client = app.test_client()

# /models/<db>/ alpha
def test_models_db_alpha():
    """"""
    #landing = client.get("/models/kindgirls?order=alpha")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=alpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/ ralpha
def test_models_db_ralpha():
    """"""
    #landing = client.get("/models/kindgirls?order=ralpha")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=ralpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/ id
def test_models_db_id():
    """"""
    #landing = client.get("/models/kindgirls?order=id")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=id")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/ rid
def test_models_db_rid():
    """"""
    #landing = client.get("/models/kindgirls?order=rid")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=rid")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/ date
def test_models_db_date():
    """"""
    #landing = client.get("/models/kindgirls?order=date")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=date")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/ rdate
def test_models_db_rdate():
    """"""
    #landing = client.get("/models/kindgirls?order=rdate")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=rdate")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/ most
def test_models_db_most():
    """"""
    #landing = client.get("/models/kindgirls?order=most")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=most")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/ least
def test_models_db_least():
    """"""
    #landing = client.get("/models/kindgirls?order=least")
    #assert landing.status_code == 200
    #html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=least")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/?page=2
def test_models_db_page2():
    """"""
    #landing = client.get("/models/kindgirls?page=2")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?page=2")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/id?order=alpha
def test_models_db_id_alpha():
    """"""
    #landing = client.get("/models/kindgirls/7/?order=alpha")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/7?order=alpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/id?order=ralpha
def test_models_db_id_ralpha():
    """"""
    #landing = client.get("/models/kindgirls/7/?order=ralpha")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/7?order=ralpha")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/id?order=date
def test_models_db_id_date_excp():
    """"""
    #landing = client.get("/models/kindgirls/7/?order=date")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/7?order=date")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/id?order=rdate
def test_models_db_id_rdate_excp():
    """"""
    #landing = client.get("/models/kindgirls/7/?order=rdate")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/7?order=rdate")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/id?order=date
def test_models_db_id_date():
    """"""
    #landing = client.get("/models/playboyplus/7/?order=date")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/playboyplus/7?order=date")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/id?order=rdate
def test_models_db_id_rdate():
    """"""
    landing = client.get("/models/playboyplus/7?order=rdate")
    html = landing.data.decode()
    assert landing.status_code == 200
    #landing = client.get("/models/playboyplus/7/?order=rdate")
    #html = landing.data.decode()
    #assert landing.status_code == 200

# /models/<db>/order=platest
def test_models_db_platest():
    """"""
    #landing = client.get("/models/kindgirls?order=platest")
    #assert landing.status_code == 200
    #html = landing.data.decode()
    landing = client.get("/models/kindgirls/?order=platest")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/order=rplatest
def test_models_db_rplatest():
    """"""
    #landing = client.get("/models/kindgirls?order=rplatest")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=rplatest")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/order=vlatest
def test_models_db_vlatest():
    """"""
    #landing = client.get("/models/kindgirls?order=vlatest")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=vlatest")
    html = landing.data.decode()
    assert landing.status_code == 200

# /models/<db>/order=rvlatest
def test_models_db_rvlatest():
    """"""
    #landing = client.get("/models/kindgirls?order=rvlatest")
    #html = landing.data.decode()
    #assert landing.status_code == 200
    landing = client.get("/models/kindgirls/?order=rvlatest")
    html = landing.data.decode()
    assert landing.status_code == 200
