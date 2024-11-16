import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


FORM_DATA = {
    'text': 'Новый текст'
}


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def news_all():
    return News.objects.bulk_create(
        News(
            title=f'Заголовок {i}',
            text=f'Текст новости {i}',
            date=datetime.today() + timedelta(days=1)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment_all(news, author):
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment(
            news=news,
            text=f'Текст комментария {i}',
            author=author,
        )
        comment.save()
        comment.created = timezone.now() - timedelta(seconds=i)
        comment.save(update_fields=['created'])


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_login():
    return reverse('users:login')


@pytest.fixture
def url_logout():
    return reverse('users:logout')


@pytest.fixture
def url_signup():
    return reverse('users:signup')


@pytest.fixture
def url_detail(news):
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def url_edit(comment):
    return reverse('news:edit', args=[comment.id])


@pytest.fixture
def url_delete(comment):
    return reverse('news:delete', args=[comment.id])
