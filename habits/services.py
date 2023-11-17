import json
from datetime import timedelta

from django_celery_beat.models import PeriodicTask, IntervalSchedule
from telebot import types

from habits.management.commands.bot import bot
from habits.models import Habit
from users.models import User


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


# def disable_tasks(user_id):
#     habits = Habit.objects.filter(id=user_id)
#     for habit in habits:
#         PeriodicTask.objects.filter(id=habit.task_id).update(enabled=False)


# TG BOT
@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Авторизоваться", "Сменить пользователя")
    bot.send_message(message.chat.id,
                     f'Привет {message.from_user.first_name}\n'
                     f'Для активации сервиса уведомлений необходимо авторизоваться',
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Авторизоваться")
def authorization(message):
    user = User.objects.filter(chat_id=message.chat.id)
    if user.exists():
        bot.send_message(message.chat.id, "Вы уже авторизованы")
    else:
        authorized_user(message)


@bot.message_handler(func=lambda message: message.text == "Сменить пользователя")
def change_user_start(message):
    user = User.objects.filter(chat_id=message.chat.id, is_active=True)
    if user.exists():
        authorized_user(message)
    else:
        bot.send_message(message.chat.id, "Вы еще не авторизованы")


@bot.message_handler(func=lambda message: True)
def other_handle_message(message):
    user = User.objects.filter(chat_id=message.chat.id, is_active=True)
    if not user.exists():
        bot.send_message(message.chat.id, f'{message.from_user.first_name}! Для начала авторизуйтесь.')


def process_email(message):
    email = message.text
    user = User.objects.filter(email=email, is_active=True)

    if user.exists() and not user.first().chat_id:
        bot.send_message(message.chat.id, "Введите пароль")
        bot.register_next_step_handler(message, process_password, user.first())
    elif user.exists() and user.first().chat_id:
        bot.send_message(message.chat.id, "Вы уже авторизованы под этим пользователем!")
    else:
        bot.send_message(message.chat.id, "Такого пользователя не существует")


def process_password(message, user):
    password = message.text
    if user.check_password(password):
        user.chat_id = message.chat.id
        user.save()
        bot.send_message(message.chat.id, "Вы успешно авторизованы!")
    else:
        bot.send_message(message.chat.id, "Неверный пароль")


def authorized_user(message):
    bot.send_message(message.chat.id, "Введите адрес электронной почты")
    bot.register_next_step_handler(message, process_email)
