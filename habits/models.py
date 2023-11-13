from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


NULLABLE = {'null': True, 'blank': True}


class Habit(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='пользователь')
    place = models.CharField(max_length=200, verbose_name='место')
    time = models.TimeField(verbose_name='время')
    action = models.CharField(max_length=250, verbose_name='действие')
    is_pleasurable = models.BooleanField(default=False, verbose_name='признак приятной привычки')
    related_habit = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='связанная привычка', **NULLABLE)
    frequency = models.PositiveSmallIntegerField(default=1, verbose_name='Периодичность',
                                                 validators=[MinValueValidator(1), MaxValueValidator(7)])
    reward = models.CharField(max_length=200, verbose_name='вознаграждение', **NULLABLE)
    duration = models.PositiveSmallIntegerField(verbose_name='время на выполнение', validators=[MaxValueValidator(120)])
    is_public = models.BooleanField(default=False, verbose_name='признак публичности')

    def __str__(self):
        return f'{self.action} {self.time} - {self.place}'

    class Meta:
        verbose_name = 'привычка'
        verbose_name_plural = 'привычки'
        ordering = ('-id',)
