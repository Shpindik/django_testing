import pytest
from pytest_lazyfixture import lazy_fixture as lf
from http import HTTPStatus

from pytest_django.asserts import assertRedirects

HTTP_OK = HTTPStatus.OK
HTTP_NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client_, code',
    (
        (lf('url_home'), lf('client'), HTTP_OK),
        (lf('url_login'), lf('client'), HTTP_OK),
        (lf('url_logout'), lf('client'), HTTP_OK),
        (lf('url_signup'), lf('client'), HTTP_OK),
        (lf('url_detail'), lf('client'), HTTP_OK),
        (lf('url_edit'), lf('author_client'), HTTP_OK),
        (lf('url_delete'), lf('author_client'), HTTP_OK),
        (lf('url_edit'), lf('not_author_client'), HTTP_NOT_FOUND),
        (lf('url_delete'), lf('not_author_client'), HTTP_NOT_FOUND),
    )
)
def test_status_codes(url, client_, code):
    assert client_.get(url).status_code == code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, expected_url',
    (
        (lf('url_edit'),),
        (lf('url_delete'),),
    ),
)
def test_anonymous_redirects(url, expected_url, client, url_login):
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
