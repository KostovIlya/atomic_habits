import time

import pytz
from celery import shared_task

from habits.models import Habit
from habits.services import send_message_bot


@shared_task
def send_telegram_message(habit_id):
    habit = Habit.objects.get(id=habit_id)

    moscow_tz = pytz.timezone('Europe/Moscow')
    time_moscow = habit.time.astimezone(moscow_tz).time()

    message = f'Я буду делать {habit.action} в {time_moscow.strftime("%H:%M")} в {habit.place} {habit.user.email}'
    send_message_bot(message)

    time.sleep(habit.duration)

    if habit.related_habit:
        message_2 = f'Твоя награда за выполнение полезной привычки, выполни приятную привычку {habit.related_habit.action}'
    else:
        message_2 = f'Твоя награда за выполнение полезной привычки, получи награду {habit.reward}'
    send_message_bot(message_2)
