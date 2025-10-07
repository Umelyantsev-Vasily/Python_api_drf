# from django.contrib import admin
# from materials.models import Course, Lesson
# from .models import User, Payment
# from django import forms
#
#
# class PaymentForm(forms.ModelForm):
#     class Meta:
#         model = Payment
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Явно указываем queryset для полей
#         self.fields['user'].queryset = User.objects.all()
#         self.fields['paid_course'].queryset = Course.objects.all()
#         self.fields['paid_lesson'].queryset = Lesson.objects.all()
#
#
# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     form = PaymentForm
#     list_display = ('user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method')
#     list_filter = ('payment_method', 'payment_date')
#     search_fields = ('user__email', 'paid_course__title', 'paid_lesson__title')
