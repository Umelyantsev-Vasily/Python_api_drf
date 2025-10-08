from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer, UserProfileSerializer
from .permissions import IsOwnerOrStaff

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Разрешаем доступ без аутентификации только для создания (регистрации)
        if self.action == 'create':
            return [AllowAny()]
        # Для всех остальных действий требуем аутентификацию
        return [IsAuthenticated(), IsOwnerOrStaff()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        if int(kwargs['pk']) != request.user.id and not request.user.is_staff:
            return Response({"detail": "Нет прав для редактирования этого профиля"},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserSerializer
        else:
            return UserProfileSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Эндпоинт для регистрации (можно удалить, если используете стандартный create)"""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

