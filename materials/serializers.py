from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('owner',)

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

    def validate_title(self, value):
        """Валидация названия урока"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value

    def validate_video_link(self, value):
        if value and 'youtube.com' not in value:
            raise serializers.ValidationError("Допускаются только ссылки на YouTube")
        return value
