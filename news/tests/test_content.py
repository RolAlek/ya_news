from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from news.models import News, Comment

User = get_user_model()


class TestContent(TestCase):
    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls) -> None:
        today = datetime.today()
        all_news = []
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
            news = News(
                title=f'Новость {index}',
                text='Текст новости.',
                date=today - timedelta(days=index))
            all_news.append(news)
        News.objects.bulk_create(all_news)

    def test_new_count(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = len(object_list)
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_new_order(self):
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        first_news_date = object_list[0].date
        all_dates = [news.date for news in object_list]
        self.assertEqual(first_news_date, max(all_dates))


class TestDetailPage(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.news = News.objects.create(
            title='Тестовая новость',
            text='Тестовый текст.'
        )
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.author = User.objects.create(username='Коментатор')
        now = timezone.now()
        for index in range(2):
            comment = Comment.objects.create(
                news=cls.news,
                author=cls.author,
                text=f'Тестовый комментарий {index}'
            )
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comment_order(self):
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comment = news.comment_set.all()
        self.assertLess(all_comment[0].created, all_comment[1].created)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
