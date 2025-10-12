from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from rest_framework.decorators import action

from .models import Course, Lesson, Subscription, Payment
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer, PaymentCreateSerializer
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator
from .paginators import MaterialsPaginator
from .services.stripe_service import StripeService
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    """
    API для управления курсами

    - **Создание курса**: Только аутентифицированные пользователи (не модераторы)
    - **Просмотр курсов**: Аутентифицированные пользователи видят только свои курсы, модераторы видят все
    - **Обновление курса**: Владелец курса или модератор
    - **Удаление курса**: Только владелец курса
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = MaterialsPaginator

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Course.objects.none()

        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def update(self, request, *args, **kwargs):
        """
        Переопределяем метод update для отправки уведомлений
        """
        response = super().update(request, *args, **kwargs)

        # Если обновление прошло успешно, отправляем уведомления
        if response.status_code == status.HTTP_200_OK:
            course_id = kwargs.get('pk')
            # Запускаем асинхронную задачу
            send_course_update_notification.delay(course_id)

        return response

    def partial_update(self, request, *args, **kwargs):
        """
        Переопределяем метод partial_update для отправки уведомлений
        """
        response = super().partial_update(request, *args, **kwargs)

        # Если обновление прошло успешно, отправляем уведомления
        if response.status_code == status.HTTP_200_OK:
            course_id = kwargs.get('pk')
            # Запускаем асинхронную задачу
            send_course_update_notification.delay(course_id)

        return response


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Создание нового урока

    - Только аутентифицированные пользователи (не модераторы)
    - Владелец автоматически устанавливается как текущий пользователь
    - Ссылка на видео должна быть только с YouTube
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """
    Получение списка уроков

    - Аутентифицированные пользователи видят только свои уроки
    - Модераторы видят все уроки
    - Доступна фильтрация по курсу: ?course=<course_id>
    - Доступна пагинация: ?page=<page_number>&page_size=<size>
    """
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']
    pagination_class = MaterialsPaginator  # используем один пагинатор

    def get_queryset(self):
        # Проверка для генерации схемы Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()

        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение детальной информации об уроке

    - Владелец урока или модератор
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Обновление урока

    - Владелец урока или модератор
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление урока

    - Только владелец урока
    - Модераторы не могут удалять уроки
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class SubscriptionAPIView(APIView):
    """
    Управление подписками на курсы

    - **POST**: Добавление или удаление подписки
    - Требуется аутентификация
    - Если подписка существует - она удаляется
    - Если подписки нет - она создается
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'

        # Возвращаем ответ в API
        return Response({"message": message}, status=status.HTTP_200_OK)


class PaymentViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    ViewSet для управления платежами
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    pagination_class = MaterialsPaginator

    def get_queryset(self):
        # Проверка для генерации схемы Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

    @swagger_auto_schema(
        operation_description="Создать платеж для курса",
        request_body=PaymentCreateSerializer,
        responses={
            201: openapi.Response(
                description="Платеж создан",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'payment_url': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='URL для оплаты'
                        ),
                        'payment_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='ID платежа в системе'
                        ),
                        'session_id': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='ID сессии Stripe'
                        )
                    }
                )
            ),
            400: openapi.Response(description="Неверные данные"),
            404: openapi.Response(description="Курс не найден")
        }
    )
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Создание платежа для курса"""
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            success_url = serializer.validated_data.get('success_url', settings.FRONTEND_SUCCESS_URL)
            cancel_url = serializer.validated_data.get('cancel_url', settings.FRONTEND_CANCEL_URL)

            # Получаем курс
            course = get_object_or_404(Course, id=course_id)

            # Проверяем, не купил ли пользователь уже этот курс
            existing_payment = Payment.objects.filter(
                user=request.user,
                course=course,
                status='succeeded'
            ).exists()

            if existing_payment:
                return Response(
                    {"error": "Вы уже приобрели этот курс"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Создаем или получаем продукт и цену в Stripe
            if not course.stripe_product_id:
                # Создаем продукт в Stripe
                product = StripeService.create_product(
                    name=course.title,
                    description=course.description
                )
                course.stripe_product_id = product.id

            if not course.stripe_price_id:
                # Создаем цену в Stripe (умножаем на 100 для перевода в центы)
                price_amount = int(course.price * 100)
                price = StripeService.create_price(
                    product_id=course.stripe_product_id,
                    amount=price_amount
                )
                course.stripe_price_id = price.id
                course.save()

            # Создаем сессию оплаты в Stripe
            metadata = {
                'course_id': str(course.id),
                'user_id': str(request.user.id)
            }

            session = StripeService.create_checkout_session(
                price_id=course.stripe_price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )

            # Создаем запись о платеже в базе данных
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                stripe_session_id=session.id,
                status='pending'
            )

            return Response({
                'payment_url': session.url,
                'payment_id': payment.id,
                'session_id': session.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Проверить статус платежа",
        responses={
            200: openapi.Response(
                description="Статус платежа",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'course_title': openapi.Schema(type=openapi.TYPE_STRING),
                        'stripe_session_id': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response(description="Платеж не найден")
        }
    )
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Проверка статуса платежа"""
        payment = self.get_object()

        # Обновляем статус из Stripe
        if payment.stripe_session_id:
            try:
                session = StripeService.retrieve_session(payment.stripe_session_id)

                if session.payment_status == 'paid' and payment.status != 'succeeded':
                    payment.status = 'succeeded'
                    if session.payment_intent:
                        payment.stripe_payment_intent_id = session.payment_intent
                    payment.save()

            except Exception as e:
                # Логируем ошибку, но не прерываем выполнение
                print(f"Ошибка при обновлении статуса платежа: {str(e)}")

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
