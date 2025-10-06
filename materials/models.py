from django.conf import settings
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/previews/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Владелец')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена')
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID продукта в Stripe')
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID цены в Stripe')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/previews/', blank=True, null=True, verbose_name='Превью')
    video_link = models.URLField(blank=True, null=True, verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Владелец')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions', verbose_name='Курс')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']  # Одна подписка на пользователя и курс

    def __str__(self):
        return f'{self.user.email} подписан на {self.course.title}'


class Payment(models.Model):
    """
    Модель платежа за курс
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'В обработке'),
        ('succeeded', 'Оплачено'),
        ('canceled', 'Отменено'),
        ('failed', 'Ошибка оплаты'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    stripe_session_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID сессии Stripe')
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID платежа Stripe')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']

    def __str__(self):
        return f'Платеж {self.id} - {self.user.email} - {self.course.title}'
