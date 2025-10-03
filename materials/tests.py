from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    """Тесты для CRUD операций с уроками"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователей
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='testpass123',
            first_name='Owner',
            last_name='Test'
        )

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123',
            first_name='Moderator',
            last_name='Test'
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )

        # Добавляем модератора в группу модераторов
        from django.contrib.auth.models import Group
        moderator_group, created = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            owner=self.owner
        )

        # Создаем урок
        self.lesson_data = {
            'title': 'Test Lesson',
            'description': 'Test Lesson Description',
            'video_link': 'https://www.youtube.com/watch?v=test123',
            'course': self.course.id
        }

        self.lesson = Lesson.objects.create(
            title='Existing Lesson',
            description='Existing Lesson Description',
            video_link='https://www.youtube.com/watch?v=existing',
            course=self.course,
            owner=self.owner
        )

        # URL для тестов
        self.lesson_list_url = reverse('lesson-list')
        self.lesson_detail_url = reverse('lesson-detail', kwargs={'pk': self.lesson.pk})
        self.lesson_create_url = reverse('lesson-create')
        self.lesson_update_url = reverse('lesson-update', kwargs={'pk': self.lesson.pk})
        self.lesson_delete_url = reverse('lesson-delete', kwargs={'pk': self.lesson.pk})

    def test_create_lesson_authenticated_owner(self):
        """Тест создания урока аутентифицированным владельцем"""
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.lesson_create_url, self.lesson_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().title, 'Test Lesson')
        self.assertEqual(Lesson.objects.last().owner, self.owner)

    def test_create_lesson_authenticated_moderator_denied(self):
        """Тест запрета создания урока модератором"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.post(self.lesson_create_url, self.lesson_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_create_lesson_unauthenticated_denied(self):
        """Тест запрета создания урока неаутентифицированным пользователем"""
        response = self.client.post(self.lesson_create_url, self.lesson_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_invalid_youtube_link(self):
        """Тест создания урока с невалидной ссылкой (не YouTube)"""
        self.client.force_authenticate(user=self.owner)

        invalid_data = self.lesson_data.copy()
        invalid_data['video_link'] = 'https://vimeo.com/test123'

        response = self.client.post(self.lesson_create_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_list_lessons_owner(self):
        """Тест получения списка уроков владельцем"""
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.lesson_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Используем results из-за пагинации
        self.assertEqual(response.data['results'][0]['title'], 'Existing Lesson')

    def test_list_lessons_moderator(self):
        """Тест получения списка уроков модератором"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(self.lesson_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Модератор видит все уроки
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_lesson_owner(self):
        """Тест получения деталей урока владельцем"""
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Existing Lesson')

    def test_retrieve_lesson_moderator(self):
        """Тест получения деталей урока модератором"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Existing Lesson')

    def test_retrieve_lesson_other_user_denied(self):
        """Тест запрета получения деталей урока другим пользователем"""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.owner)

        update_data = {'title': 'Updated Lesson Title'}
        response = self.client.patch(self.lesson_update_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson Title')

    def test_update_lesson_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator)

        update_data = {'title': 'Updated by Moderator'}
        response = self.client.patch(self.lesson_update_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated by Moderator')

    def test_update_lesson_other_user_denied(self):
        """Тест запрета обновления урока другим пользователем"""
        self.client.force_authenticate(user=self.other_user)

        update_data = {'title': 'Unauthorized Update'}
        response = self.client.patch(self.lesson_update_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.lesson_delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator_denied(self):
        """Тест запрета удаления урока модератором"""
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(self.lesson_delete_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_delete_lesson_other_user_denied(self):
        """Тест запрета удаления урока другим пользователем"""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.lesson_delete_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)


class SubscriptionTestCase(APITestCase):
    """Тесты для функционала подписок"""

    def setUp(self):
        """Настройка тестовых данных для подписок"""
        # Создаем пользователя
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course for Subscription',
            description='Test Course Description',
            owner=self.user
        )

        # URL для тестов подписок
        self.subscription_url = reverse('subscription')

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.subscription_url, {'course_id': self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        self.client.force_authenticate(user=self.user)

        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        # Затем отписываемся
        response = self.client.post(self.subscription_url, {'course_id': self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    # def test_subscription_without_course_id(self):
    #     """Тест подписки без указания course_id"""
    #     self.client.force_authenticate(user=self.user)
    #
    #     response = self.client.post(self.subscription_url, {})
    #
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('error', response.data)

    def test_subscription_invalid_course_id(self):
        """Тест подписки с несуществующим course_id"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.subscription_url, {'course_id': 999})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_unauthenticated(self):
        """Тест подписки неаутентифицированным пользователем"""
        response = self.client.post(self.subscription_url, {'course_id': self.course.id})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_is_subscribed_field_in_course_serializer(self):
        """Тест поля is_subscribed в сериализаторе курса"""
        self.client.force_authenticate(user=self.user)

        # Подписываемся на курс
        Subscription.objects.create(user=self.user, course=self.course)

        # Получаем детали курса
        course_detail_url = reverse('course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(course_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_is_not_subscribed_field_in_course_serializer(self):
        """Тест поля is_subscribed когда пользователь не подписан"""
        self.client.force_authenticate(user=self.user)

        # Получаем детали курса без подписки
        course_detail_url = reverse('course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(course_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])


class PaginationTestCase(APITestCase):
    """Тесты для пагинации"""

    def setUp(self):
        """Настройка тестовых данных для пагинации"""
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

        # Создаем несколько уроков для тестирования пагинации
        for i in range(15):
            Lesson.objects.create(
                title=f'Lesson {i}',
                description=f'Description {i}',
                course=self.course,
                owner=self.user
            )

        self.lesson_list_url = reverse('lesson-list')

    def test_pagination_default_page_size(self):
        """Тест пагинации с размером страницы по умолчанию"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lesson_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

        # Проверяем размер страницы по умолчанию (10)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 15)

    def test_pagination_custom_page_size(self):
        """Тест пагинации с кастомным размером страницы"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"{self.lesson_list_url}?page_size=5")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_pagination_max_page_size(self):
        """Тест максимального размера страницы"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"{self.lesson_list_url}?page_size=100")  # Больше max_page_size

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен ограничиться max_page_size (50)
        self.assertEqual(len(response.data['results']), 15)  # Всего 15 уроков


class ValidatorTestCase(TestCase):
    """Тесты для валидаторов"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

    def test_youtube_validator_valid_links(self):
        """Тест валидатора YouTube с валидными ссылками"""
        from .validators import validate_youtube_only

        valid_links = [
            'https://www.youtube.com/watch?v=test123',
            'https://youtube.com/watch?v=test123',
            'https://youtu.be/test123',
            'https://www.youtu.be/test123',
            ''
        ]

        for link in valid_links:
            try:
                validate_youtube_only(link)
            except Exception as e:
                self.fail(f"Валидная ссылка {link} вызвала ошибку: {e}")

    def test_youtube_validator_invalid_links(self):
        """Тест валидатора YouTube с невалидными ссылками"""
        from .validators import validate_youtube_only
        from django.core.exceptions import ValidationError

        invalid_links = [
            'https://vimeo.com/test123',
            'https://rutube.ru/watch/test123',
            'https://example.com/video',
            'http://mywebsite.com/youtube'  # Обманчивая ссылка
        ]

        for link in invalid_links:
            with self.assertRaises(ValidationError):
                validate_youtube_only(link)
