from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING, BAD_WORDS
from news.models import Comment
from .conftest import FORM_DATA

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, url_detail, url_login):
    count = Comment.objects.count()
    response = client.post(url_detail, FORM_DATA)
    expected_url = f"{url_login}?next={url_detail}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == count


def test_create_comment_authorized_user(
        author_client, author, news, url_detail):
    Comment.objects.all().delete()
    count = Comment.objects.count()
    response = author_client.post(url_detail, FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_detail + '#comments')
    assert Comment.objects.count() == count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, url_detail, bad_word):
    count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(url_detail, data=bad_words_data)
    assert Comment.objects.count() == count
    assert response.status_code == HTTPStatus.OK
    assertFormError(response, 'form', 'text', WARNING)


def test_edit_comment_author_client(
        author_client, comment, url_edit, url_detail):
    response = author_client.post(url_edit, FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_detail + '#comments')
    updated_comment = Comment.objects.get(pk=comment.id)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_edit_comment_not_author_client(not_author_client, comment, url_edit):
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news
    response = not_author_client.post(url_edit, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
    assert comment.author == original_author
    assert comment.news == original_news


def test_delete_comment_author_client(author_client, comment, url_delete):
    count = Comment.objects.count()
    response = author_client.post(url_delete)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == count - 1
    with pytest.raises(Comment.DoesNotExist):
        Comment.objects.get(pk=comment.id)


def test_delete_comment_not_author_client(
        not_author_client, comment, news, url_delete):
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news
    count = Comment.objects.count()
    response = not_author_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count
    comment = Comment.objects.get(pk=comment.id)
    assert comment.text == original_text
    assert comment.author == original_author
    assert comment.news == original_news
