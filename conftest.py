import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок новости', text='Текст новости')
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def pk_for_news(news):
    return news.pk,


@pytest.fixture
def news_list(news):
    today = datetime.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    news_list = News.objects.bulk_create(all_news)
    return news_list


@pytest.fixture
def comment_list(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
