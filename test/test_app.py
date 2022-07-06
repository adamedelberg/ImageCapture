import sys
sys.path.insert(0, './')
from app import app

def test_index():
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert b"<title>Image Capture WebApp - Index</title>" in response.data

def test_viewer():
    response = app.test_client().get('/image/first')
    assert response.status_code == 200
    assert b"<title>Image Capture WebApp - Viewer</title>" in response.data

def test_upload():
    response = app.test_client().get('/upload_image')
    assert response.status_code == 200
    assert b"<title>Image Capture WebApp - Upload</title>" in response.data

def test_upload_complete():
    response = app.test_client().post('/upload_image')
    assert response.status_code == 200
    assert b"<title>Image Capture WebApp - Upload Complete</title>" in response.data
