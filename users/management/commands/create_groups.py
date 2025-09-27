from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Create moderator group'

    def handle(self, *args, **options):
        moderators, created = Group.objects.get_or_create(name='moderators')

        # Права для курсов
        course_content_type = ContentType.objects.get_for_model(Course)
        course_permissions = Permission.objects.filter(
            content_type=course_content_type,
            codename__in=['view_course', 'change_course']
        )
        moderators.permissions.add(*course_permissions)

        # Права для уроков
        lesson_content_type = ContentType.objects.get_for_model(Lesson)
        lesson_permissions = Permission.objects.filter(
            content_type=lesson_content_type,
            codename__in=['view_lesson', 'change_lesson']
        )
        moderators.permissions.add(*lesson_permissions)

        self.stdout.write('Группа модераторов создана')
