import io

import flask
import pytest

from marvin_acme.app import app


@pytest.fixture
def client():
    app.config["SERVER_NAME"] = "testserver"
    with app.app_context():
        yield app.test_client()


@pytest.fixture
def good_test_data():
    return {"img": (io.BytesIO(b"123"), "goodfile.png")}


@pytest.fixture
def test_data_no_filename():
    return {"img": (io.BytesIO(b"123"), "")}


@pytest.fixture
def test_data_unsupported_extension():
    return {"img": (io.BytesIO(b"123"), "badfile.xml")}


def test_status_route(client):
    response = client.get(flask.url_for("status"))
    assert 200 == response.status_code
    assert "UP" == response.json.get("status")


def test_upload_without_file_responds_with_400(client):
    response = client.post(
        flask.url_for("img"), data={}, content_type="multipart/form-data"
    )
    assert 400 == response.status_code
    assert 1 == len(response.json)
    assert "required" == response.json.get("img", "").lower()


def test_upload_correct_data_responds_with_200(client, good_test_data):
    response = client.post(
        flask.url_for("img"), data=good_test_data, content_type="multipart/form-data"
    )
    assert 200 == response.status_code


def test_upload_with_png_file_responds_correct_mimetype(client, good_test_data):
    response = client.post(
        flask.url_for("img"), data=good_test_data, content_type="multipart/form-data"
    )
    assert "image/png" == response.mimetype


def test_upload_returns_same_data(client, good_test_data):
    response = client.post(
        flask.url_for("img"), data=good_test_data, content_type="multipart/form-data"
    )
    assert b"123" == response.data


def test_upload_with_no_filename_responds_with_400(client, test_data_no_filename):
    response = client.post(
        flask.url_for("img"),
        data=test_data_no_filename,
        content_type="multipart/form-data",
    )
    assert 400 == response.status_code
    assert 1 == len(response.json)
    assert "select" in response.json.get("img", "").lower()


def test_upload_with_unsupported_extension_responds_with_400(
    client, test_data_unsupported_extension
):
    response = client.post(
        flask.url_for("img"),
        data=test_data_unsupported_extension,
        content_type="multipart/form-data",
    )
    assert 400 == response.status_code
    assert 1 == len(response.json)
    assert "unsupported" in response.json.get("img", "").lower()
