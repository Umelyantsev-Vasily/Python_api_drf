# create_sample_data.py
from django.core.management.base import BaseCommand
from users.models import User, Payment
from materials.models import Course, Lesson
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Создаем пользователей
        user1, created = User.objects.get_or_create(
            email='student@example.com',
            defaults={
                'phone': '+79991234567',
                'city': 'Москва',
                'is_active': True
            }
        )
        if created:
            user1.set_password('student123')
            user1.save()
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {user1.email}'))

        user2, created = User.objects.get_or_create(
            email='moderator@example.com',
            defaults={
                'phone': '+79997654321',
                'city': 'Санкт-Петербург',
                'is_active': True
            }
        )
        if created:
            user2.set_password('moderator123')
            user2.save()
            # Добавляем в группу модераторов
            moderators_group, _ = Group.objects.get_or_create(name='moderators')
            user2.groups.add(moderators_group)
            self.stdout.write(self.style.SUCCESS(f'Создан модератор: {user2.email}'))

        # Создаем курсы
        course1, created = Course.objects.get_or_create(
            title='Python для начинающих',
            defaults={
                'description': 'Изучаем основы программирования на Python',
                'owner': user1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан курс: {course1.title}'))

        course2, created = Course.objects.get_or_create(
            title='Django REST Framework',
            defaults={
                'description': 'Создание API с помощью Django REST Framework',
                'owner': user1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан курс: {course2.title}'))

        # Создаем уроки
        lesson1, created = Lesson.objects.get_or_create(
            title='Введение в Python',
            defaults={
                'description': 'Основные концепции языка Python',
                'course': course1,
                'video_link': 'https://youtube.com/watch?v=python_intro',
                'owner': user1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson1.title}'))

        lesson2, created = Lesson.objects.get_or_create(
            title='Модели Django',
            defaults={
                'description': 'Работа с моделями в Django',
                'course': course2,
                'video_link': 'https://youtube.com/watch?v=django_models',
                'owner': user1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson2.title}'))

        lesson3, created = Lesson.objects.get_or_create(
            title='Серииализаторы DRF',
            defaults={
                'description': 'Создание сериализаторов в Django REST Framework',
                'course': course2,
                'video_link': 'https://youtube.com/watch?v=drf_serializers',
                'owner': user1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создан урок: {lesson3.title}'))

        # Создаем платежи
        payments_data = [
            {
                'user': user1,
                'paid_course': course1,
                'paid_lesson': None,
                'amount': 1000.00,
                'payment_method': 'transfer'
            },
            {
                'user': user1,
                'paid_course': None,
                'paid_lesson': lesson1,
                'amount': 500.00,
                'payment_method': 'cash'
            },
            {
                'user': user1,
                'paid_course': course2,
                'paid_lesson': None,
                'amount': 1500.00,
                'payment_method': 'transfer'
            },
            {
                'user': user2,
                'paid_course': course1,
                'paid_lesson': None,
                'amount': 1000.00,
                'payment_method': 'transfer'
            },
        ]

        created_count = 0
        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(
                user=payment_data['user'],
                paid_course=payment_data['paid_course'],
                paid_lesson=payment_data['paid_lesson'],
                defaults={
                    'amount': payment_data['amount'],
                    'payment_method': payment_data['payment_method']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Создано {created_count} платежей'))
        self.stdout.write(self.style.SUCCESS('Все тестовые данные успешно созданы!'))
