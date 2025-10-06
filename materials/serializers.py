from rest_framework import serializers
from .models import Course, Lesson, Subscription, Payment
from .validators import YouTubeUrlValidator, validate_youtube_only


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курсов

    Поля:
    - id: ID курса
    - title: Название курса (минимум 3 символа)
    - description: Описание курса (минимум 10 символов)
    - preview: Превью изображение
    - owner: Владелец курса (только для чтения)
    - owner_email: Email владельца (только для чтения)
    - is_subscribed: Подписан ли текущий пользователь на курс (только для чтения)
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner',)
        # Добавляем валидатор для проверки ссылок в описании
        validators = [
            YouTubeUrlValidator(field=['description'])
        ]

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        user = self.context['request'].user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, course=obj).exists()
        return False

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value

    def validate_description(self, value):
        """Валидация описания"""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Описание должно содержать минимум 10 символов")
        return value


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для уроков

    Поля:
    - id: ID урока
    - title: Название урока (минимум 3 символа)
    - description: Описание урока
    - preview: Превью изображение
    - video_link: Ссылка на видео (только YouTube)
    - course: Связанный курс
    - owner: Владелец урока (только для чтения)
    - owner_email: Email владельца (только для чтения)
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner',)
        # Добавляем оба валидатора
        validators = [
            YouTubeUrlValidator(field=['video_link', 'description']),
            serializers.UniqueTogetherValidator(
                queryset=Lesson.objects.all(),
                fields=['title', 'course'],
                message='Урок с таким названием уже существует в этом курсе'
            )
        ]

    def validate_title(self, value):
        """Валидация названия урока"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value

    def validate_video_link(self, value):
        """Валидация ссылки на видео (дополнительная проверка)"""
        validate_youtube_only(value)  # используем функцию для обратной совместимости
        return value

class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для платежей
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('user', 'status', 'stripe_session_id', 'stripe_payment_intent_id', 'created_at', 'updated_at')


class PaymentCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания платежа
    """
    course_id = serializers.IntegerField()
    success_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)

    def validate_course_id(self, value):
        """Проверяем, что курс существует"""
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Курс не найден")
        return value
