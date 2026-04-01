from django.db import models
from django.core.validators import MaxLengthValidator


class Test(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Test title',
    )
    description = models.TextField(
        null=True,
        blank=True,
        validators=[MaxLengthValidator(2000)],
        verbose_name='Description',
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

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name='Question')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ('order', 'id')

    def __str__(self):
        return f'{self.test.title} - {self.text[:50]}'


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
