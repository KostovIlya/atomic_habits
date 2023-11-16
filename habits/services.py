import json
import os
from datetime import timedelta

import requests
from django.conf import settings
from django_celery_beat.models import PeriodicTask, IntervalSchedule


def send_message_bot(text):
    chat_id = os.getenv('TG_CHAT_ID')
    params = {'chat_id': chat_id, 'text': text}

    response = requests.get(f'{settings.TG_URL}{settings.TG_BOT_TOKEN}/sendMessage', params=params)
    # print(response)
    # response_decode = response.content.decode('utf-8')
    # print(response_decode)

    # print(response_decode.json())


def create_periodic_task(habit):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=habit.frequency,
        period=IntervalSchedule.DAYS,
    )

    task = PeriodicTask.objects.create(
        interval=schedule,
        name=f'Sending messages - Habit {habit.id}',
        task='habits.tasks.send_telegram_message',
        kwargs=json.dumps({
            'habit_id': habit.id,
        }),
        start_time=habit.time - timedelta(minutes=10)
    )

    habit.task_id = task.id
    habit.save()


def update_periodic_task(habit):
    task = PeriodicTask.objects.get(id=habit.task_id)
    task.interval.every = habit.frequency
    task.start_time = habit.time - timedelta(minutes=10)
    task.save()


def delete_periodic_task(habit):
    task = PeriodicTask.objects.get(id=habit.task_id)
    task.delete()


# def get_updates(offset=0):
#     result = requests.get(f'{TG_URL}{TG_BOT_TOKEN}/getUpdates?offset={offset}').json()
#     return result['result']
#
#
# def send_message(chat_id, text):
#     requests.get(f'{TG_URL}{TG_BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={text}')
#
#
# def check_message(chat_id, message):
#     for mes in message.lower().replace(',', '').split():
#         if mes in ['привет', 'ку']:
#             send_message(chat_id, 'Привет :)')
#         if mes in ['дела?', 'успехи?']:
#             send_message(chat_id, 'Спасибо, хорошо!')
#
#
# def run():
#     update_id = get_updates()[-1]['update_id'] # Присваиваем ID последнего отправленного сообщения боту
#     while True:
#         # time.sleep(2)
#         messages = get_updates(update_id) # Получаем обновления
#         for message in messages:
#             # Если в обновлении есть ID больше чем ID последнего сообщения, значит пришло новое сообщение
#             if update_id < message['update_id']:
#                 update_id = message['update_id'] # Присваиваем ID последнего отправленного сообщения боту
#                 # Отвечаем тому кто прислал сообщение боту
#                 check_message(message['message']['chat']['id'], message['message']['text'])
