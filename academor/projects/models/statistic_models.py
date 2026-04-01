from django.db import models
from django.core.validators import MaxLengthValidator

class AcademyStatistic(models.Model):
    value_one = models.PositiveIntegerField(
        verbose_name='Client count'
    )
    value_two = models.PositiveIntegerField(
        verbose_name='Project count'
    )
    value_three = models.PositiveIntegerField(
        verbose_name='Partner count'
    )

    class Meta:
        verbose_name = 'Statistic'
        verbose_name_plural = 'Statistics'

    def __str__(self):
        return 'Statistics'

   
    
   
