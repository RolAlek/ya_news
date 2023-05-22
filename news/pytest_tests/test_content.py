import pytest

from django.urls import reverse
from django.conf import settings

HOME_PAGE_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(news_list, client):
    """Тестирование пагинации."""
    response = client.get(HOME_PAGE_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(news_list, client):
    """Тестирование сортировки новостей на главной странице."""
    response = client.get(HOME_PAGE_URL)
    object_list = response.context['object_list']
    first_news_date = object_list[0].date
    all_dates = [news.date for news in object_list]
    assert first_news_date == max(all_dates)


def test_comments_order(comment_list, client, pk_for_news):
    """Тестирование сортировки комментариев."""
    url = reverse('news:detail', args=pk_for_news)
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created <= all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_create_comment_form_for_auth_user(parametrized_client, pk_for_news, form_in_context):
    url = reverse('news:detail', args=pk_for_news)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
