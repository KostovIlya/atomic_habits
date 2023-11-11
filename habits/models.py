from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.


class Habit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='пользователь')
    place = models.CharField(max_length=200, verbose_name='место')
    time = models.TimeField(verbose_name='время')
    action = models.CharField(max_length=250, verbose_name='действие')
    is_pleasurable = models.BooleanField(verbose_name='признак приятной привычки')
    related_habit = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='связанная привычка')
    frequency = models.PositiveSmallIntegerField(default=1, verbose_name='Периодичность')
    reward = models.CharField(max_length=200, verbose_name='вознаграждение')
    duration = models.TimeField(verbose_name='время на выполнение')
    is_public = models.BooleanField(default=False, verbose_name='признак публичности')

    def __str__(self):
        return f'{self.action}'
