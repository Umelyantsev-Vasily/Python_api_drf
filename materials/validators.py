from django.core.exceptions import ValidationError
from urllib.parse import urlparse


def validate_youtube_only(value):
    """
    Валидатор, который проверяет, что ссылка ведет только на youtube.com
    """
    if value:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()

        # Разрешаем только youtube.com и youtu.be (короткие ссылки YouTube)
        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']

        if not any(domain.endswith(allowed_domain) for allowed_domain in allowed_domains):
            raise ValidationError('Допускаются только ссылки на YouTube')

    return value
