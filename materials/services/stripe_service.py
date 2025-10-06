import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

# Настройка Stripe
stripe.api_key = settings.STRIPE_API_KEY


class StripeService:
    """
    Сервис для работы с Stripe API
    """

    @staticmethod
    def create_product(name, description=None):
        """
        Создание продукта в Stripe
        """
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
            )
            return product
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка создания продукта в Stripe: {str(e)}")

    @staticmethod
    def create_price(product_id, amount, currency='usd'):
        """
        Создание цены в Stripe
        amount: сумма в центах (например, $10.00 = 1000)
        """
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount,  # сумма в центах
                currency=currency,
            )
            return price
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка создания цены в Stripe: {str(e)}")

    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url, metadata=None):
        """
        Создание сессии для оплаты
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            return session
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка создания сессии оплаты в Stripe: {str(e)}")

    @staticmethod
    def retrieve_session(session_id):
        """
        Получение информации о сессии
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка получения сессии из Stripe: {str(e)}")

    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """
        Получение информации о платеже
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка получения платежа из Stripe: {str(e)}")
