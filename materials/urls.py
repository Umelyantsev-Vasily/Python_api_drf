from django.urls import path
from materials.views import (
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionAPIView,
    PaymentViewSet,
)

create_payment_view = PaymentViewSet.as_view({'post': 'create_payment'})
payment_status_view = PaymentViewSet.as_view({'get': 'status'})

urlpatterns = [
    # Уроки
    path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),

    # Добавляем эндпоинт для подписок
    path('subscription/', SubscriptionAPIView.as_view(), name='subscription'),

    # Платежи
    path('payments/create_payment/', create_payment_view, name='payment-create-payment'),
    path('payments/<int:pk>/status/', payment_status_view, name='payment-status'),
]
