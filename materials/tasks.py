# materials/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscription, Course


@shared_task
def send_course_update_notification(course_id):
    """
    Асинхронная рассылка писем об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)

        if not subscriptions.exists():
            return f"No subscribers for course {course.title}"

        emails = [subscription.user.email for subscription in subscriptions]

        subject = f'Обновление курса: {course.title}'
        message = f'''
        Здравствуйте!

        Курс "{course.title}" был обновлен. 
        Проверьте новые материалы в вашем личном кабинете.

        С уважением,
        Команда образовательной платформы
        '''

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )

        return f"Sent update notifications to {len(emails)} subscribers for course {course.title}"

    except Course.DoesNotExist:
        return f"Course with id {course_id} does not exist"
    except Exception as e:
        return f"Error sending notifications: {str(e)}"
