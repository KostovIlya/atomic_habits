import time

import pytz
from celery import shared_task

from habits.management.commands.bot import bot
from habits.models import Habit
# from habits.services import disable_tasks


@shared_task
def send_telegram_message(habit_id):
    habit = Habit.objects.get(id=habit_id)

    moscow_tz = pytz.timezone('Europe/Moscow')
    time_moscow = habit.time.astimezone(moscow_tz).time()

    if habit.user.is_active and habit.user.chat_id:
        message = f'Я буду делать {habit.action} в {time_moscow.strftime("%H:%M")} в {habit.place}'
        bot.send_message(habit.user.chat_id, message)

        time.sleep(habit.duration)

        if habit.related_habit:
            message_2 = f'Твоя награда за выполнение полезной привычки, выполни приятную привычку {habit.related_habit.action}'
        else:
            message_2 = f'Твоя награда за выполнение полезной привычки, получи награду {habit.reward}'
        bot.send_message(habit.user.chat_id, message_2)

    # elif not habit.user.is_active:
    #     disable_tasks(habit.user.id)

    else:
        return f'Пользователь {habit.user} не подключен к боту уведомлений'
