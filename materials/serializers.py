from rest_framework import serializers
from .models import Course, Lesson, Subscription  # добавляем Subscription
from .validators import validate_youtube_only


class CourseSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    is_subscribed = serializers.SerializerMethodField()  # добавляем поле подписки

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner',)

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
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner',)
        validators = [
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
        """Валидация ссылки на видео"""
        validate_youtube_only(value)
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок"""
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user', 'subscribed_at')
