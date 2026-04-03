from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxLengthValidator


class Test(models.Model):
    title_az = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Test title (AZ)',
    )
    title_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Test title (EN)',
    )
    title_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Test title (RU)',
    )
    description_az = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Description (AZ)',
    )
    description_en = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Description (EN)',
    )
    description_ru = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Description (RU)',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'
        ordering = ('-created_at',)

    def clean(self):
        super().clean()
        if not (self.title_az or self.title_en or self.title_ru):
            raise ValidationError(
                'At least one of AZ / EN / RU titles must be filled in.'
            )

    def display_title(self):
        return (self.title_en or self.title_az or self.title_ru or '').strip()

    def __str__(self):
        return self.display_title() or f'Test #{self.pk}'


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name='Question')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ('order', 'id')

    def __str__(self):
        head = self.test.display_title() if self.test_id else ''
        return f'{head} - {self.text[:50]}'


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255, verbose_name='Option')
    is_correct = models.BooleanField(default=False, verbose_name='Correct answer')

    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
        ordering = ('id',)

    def __str__(self):
        return self.text


class UserResult(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='First name')
    last_name = models.CharField(max_length=100, verbose_name='Last name')
    number = models.CharField(max_length=30, verbose_name='Phone number')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField(verbose_name='Score')
    level = models.CharField(max_length=50, verbose_name='Level')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    class Meta:
        verbose_name = 'Result'
        verbose_name_plural = 'Results'
        ordering = ('-created_at',)

    def __str__(self):
        name = f'{self.first_name} {self.last_name}'.strip()
        return f'{name} - {self.test} ({self.level})'
