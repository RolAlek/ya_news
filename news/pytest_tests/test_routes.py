# План тестирования:
# 1. Главная страница доступна анонимному пользователю. [Done!]

# 2. Страница отдельной новости доступна анонимному пользователю. [Done!]

# 3. Страницы удаления и редактирования комментария доступны автору
#  комментария. [Done!]

# 4. При попытке перейти на страницу редактирования или удаления комментария
#  анонимный пользователь перенаправляется на страницу авторизации.[Done!]

# 5. Авторизованный пользователь не может зайти на страницу редактирования или
#  удаления чужих комментариев (возвращается ошибка 404).[Done!]

# 6. Страницы регистрации пользователей, входа в учётную запись и выхода из
#  неё доступны анонимным пользователям. [Done!]
import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name, args',
        (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('pk_for_news')),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None)
        ),
)
def test_pages_avaliability_for_anonymous_user(client, name, args):
    """Тестирование публичных страниц."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        ),
)
@pytest.mark.parametrize(
        'name',
        ('news:edit', 'news:delete')
)
def test_author_can_create_and_delete_comment(
    parametrized_client, name, comment, expected_status
):
    """
    Тестирование доступности редактирования и удалнеия коментария автором.
    """
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name',
        ('news:edit', 'news:delete'),
)
def test_redirects(client, name, comment):
    """Тестирование редиректа анонимного пользователя. """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
