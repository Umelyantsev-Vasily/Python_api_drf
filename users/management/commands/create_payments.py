from django.core.management.base import BaseCommand
from users.models import Payment, User
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Create sample payments data'

    def handle(self, *args, **options):
        # Получаем объекты
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user or not course or not lesson:
            self.stdout.write(self.style.ERROR('Необходимо сначала создать пользователя, курс и урок'))
            return

        # Создаем платежи
        payments = [
            Payment(
                user=user,
                paid_course=course,
                paid_lesson=None,
                amount=1000.00,
                payment_method='transfer'
            ),
            Payment(
                user=user,
                paid_course=None,
                paid_lesson=lesson,
                amount=500.00,
                payment_method='cash'
            ),
            Payment(
                user=user,
                paid_course=course,
                paid_lesson=None,
                amount=1500.00,
                payment_method='transfer'
            ),
        ]

        Payment.objects.bulk_create(payments)
        self.stdout.write(self.style.SUCCESS('Успешно создано 3 платежа'))
