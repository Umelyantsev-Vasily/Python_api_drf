import re
from urllib.parse import urlparse
from rest_framework import serializers


class YouTubeUrlValidator:
    """Проверка содержания материалов на наличие сторонних ссылок"""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'

        # Если field - это строка (одно поле), преобразуем в список
        if isinstance(self.field, str):
            fields_to_check = [self.field]
        else:
            fields_to_check = self.field

        for field_name in fields_to_check:
            field_value = dict(value).get(field_name)
            if field_value:
                urls = re.findall(url_pattern, field_value)

                for url in urls:
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc.lower()

                    # Разрешаем только YouTube
                    allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']

                    if not any(allowed_domain in domain for allowed_domain in allowed_domains):
                        raise serializers.ValidationError("Разрешены только ссылки на YouTube")


# Оставляем и функцию для обратной совместимости, если где-то используется
def validate_youtube_only(value):
    """
    Функция-валидатор для обратной совместимости
    """
    if value:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()

        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']

        if not any(allowed_domain in domain for allowed_domain in allowed_domains):
            raise serializers.ValidationError('Допускаются только ссылки на YouTube')

    return value
