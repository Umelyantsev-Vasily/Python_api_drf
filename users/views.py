from .permissions import IsOwnerOrStaff
from .serializers import UserProfileSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Разные разрешения для разных действий
        if self.action == 'create' or self.action == 'register':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrStaff()]
        else:
            # Для list, retrieve - только аутентифицированные
            return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return User.objects.all()
        elif self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        else:
            return User.objects.none()

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if int(kwargs['pk']) != request.user.id and not request.user.is_staff:
            return Response(
                {"detail": "Нет прав для редактирования этого профиля"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'register':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserSerializer
        else:
            return UserProfileSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Регистрация нового пользователя"""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Пользователь успешно зарегистрирован',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)

