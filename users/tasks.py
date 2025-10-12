# users/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Периодическая задача для блокировки пользователей,
    которые не заходили более месяца
    """
    try:
        # Вычисляем дату, которая была 30 дней назад
        cutoff_date = timezone.now() - timedelta(days=30)

        # Находим пользователей, которые не заходили более 30 дней и активны
        inactive_users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True
        )

        count_before = inactive_users.count()

        # Деактивируем пользователей
        for user in inactive_users:
            user.is_active = False
            user.save(update_fields=['is_active'])

        return f"Deactivated {count_before} inactive users"

    except Exception as e:
        return f"Error deactivating inactive users: {str(e)}"
