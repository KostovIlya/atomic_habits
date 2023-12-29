import json
from datetime import timedelta, datetime

from django_celery_beat.models import PeriodicTask, IntervalSchedule
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create(
            email='test@test.com',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.admin_user.set_password('0000')
        self.admin_user.save()
        self.access_token_admin_user = str(AccessToken.for_user(self.admin_user))

        self.user = User.objects.create(
            email='test@test1234.com',
            is_active=True
        )
        self.user.set_password('0000')
        self.user.save()
        self.access_token_user = str(AccessToken.for_user(self.user))

        self.credentials = {
            'admin_user': f'Bearer {self.access_token_admin_user}',
            'user': f'Bearer {self.access_token_user}',
        }

        self.habit_1 = Habit.objects.create(
            user=self.user,
            place='test_habit_1',
            time='2023-11-17 17:15',
            action='1 pull-aps',
            frequency=2,
            reward='eat cookies',
            duration=4,
            is_public=True
        )

        self.habit_2 = Habit.objects.create(
            user=self.admin_user,
            place='test_habit_2',
            time='2023-11-17 17:16',
            action='2 pull-aps',
            is_pleasurable=True,
            duration=5
        )

        self.habit_3 = Habit.objects.create(
            user=self.admin_user,
            place='test_habit_3',
            time='2023-11-17 17:17',
            action='3 pull-aps',
            related_habit=self.habit_2,
            duration=6
        )

        schedule, created = IntervalSchedule.objects.get_or_create(
            every=self.habit_3.frequency,
            period=IntervalSchedule.DAYS,
        )

        task = PeriodicTask.objects.create(
            interval=schedule,
            name=f'Sending messages - Habit {self.habit_3.id}',
            task='habits.tasks.send_telegram_message',
            kwargs=json.dumps({
                'habit_id': self.habit_3.id,
            }),
            start_time=datetime.fromisoformat(self.habit_3.time) - timedelta(minutes=10)
        )

        self.habit_3.task_id = task.id
        self.habit_3.save()

    def test_create_habit(self):
        """Тестирование создания привычки"""

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['admin_user'])

        data = dict(place='test', time='2024-02-20 1:00', action='10 pull-aps', reward='test', frequency=7, duration=12,
                    is_public=True)

        response_data = dict(id=4, place='test', time='2024-02-20T01:00:00+03:00', action='10 pull-aps',
                             is_pleasurable=False, frequency=7, reward='test', duration=12, is_public=True, task_id=2,
                             user=1, related_habit=None)

        response = self.client.post('/habit/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), response_data)
        self.assertEqual(PeriodicTask.objects.filter(pk=response_data['task_id']).exists(), True)

        data = dict(place='test_4', time='2024-02-20 1:00', action='10 pull-aps', reward='test', frequency=7,
                    duration=12,
                    is_public=True, related_habit=2)

        response = self.client.post('/habit/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
            'Нельзя одновременно иметь связанную привычку и вознаграждение, выберите что-то одно']})

        data = dict(place='test_5', time='2024-02-20 1:00', action='10 pull-aps', frequency=7, duration=12,
                    is_public=True)

        response = self.client.post('/habit/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': ['Выберите вознаграждение или связанную привычку']})

        data = dict(place='test_6', time='2024-02-20 1:00', action='10 pull-aps', is_pleasurable=True, reward='test',
                    frequency=7, duration=12, is_public=True)

        response = self.client.post('/habit/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {
            'non_field_errors': ['У приятной привычки не может быть вознаграждения или связанной привычки']})

        data = dict(place='test_7', time='2024-02-20 1:00', action='10 pull-aps', related_habit=3,
                    frequency=7, duration=12, is_public=True)

        response = self.client.post('/habit/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {
            'non_field_errors': ['В связанные привычки могут попадать только привычки с признаком приятной привычки.']})

    def test_habits_list(self):
        """Тестирование получения списка привычек"""

        habits = Habit.objects.all()

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['admin_user'])
        response = self.client.get('/habit/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(habits))
        self.assertEqual(response.json()['results'][0]['id'], habits[0].pk)

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['user'])
        response = self.client.get('/habit/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)

    def test_retrieve_habit(self):
        """Тестирование получения привычки"""

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['user'])
        response = self.client.get(f'/habit/{self.habit_1.pk}/')

        response_data = dict(id=self.habit_1.pk, place='test_habit_1', time='2023-11-17T17:15:00+03:00',
                             action='1 pull-aps', is_pleasurable=False, frequency=2, reward='eat cookies',
                             duration=4, is_public=True, task_id=None, user=self.user.pk, related_habit=None)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), response_data)
        self.assertEqual(str(self.habit_1), '1 pull-aps 2023-11-17 17:15 - test_habit_1')

        response = self.client.get(f'/habit/{self.habit_2.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'You do not have permission to perform this action.'})

    def test_update_habit(self):
        """Тестирование изменения привычки"""

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['user'])

        valid_data = dict(
            place='test_habit_1',
            time='2023-11-17 17:15',
            action='1 pull-aps',
            frequency=2,
            reward='eat',
            duration=6
        )

        response_data = dict(id=self.habit_1.pk, place='test_habit_1', time='2023-11-17T17:15:00+03:00',
                             action='1 pull-aps', is_pleasurable=False, frequency=2, reward='eat',
                             duration=6, is_public=True, task_id=None, user=self.user.pk, related_habit=None)

        response = self.client.put(f'/habit/{self.habit_1.pk}/update/', valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), response_data)

    def test_update_habit_validated_data(self):
        """Тестирование валидации данных при изменении привычки"""

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['user'])

        invalid_frequency = dict(
            frequency=0
        )

        invalid_frequency_2 = dict(
            frequency=8
        )

        # invalid_duration = dict(
        #     duration=121
        # )

        invalid_duration = dict(
            is_pleasurable=True
        )

        # test_data = dict(
        #     place='test_habit_1',
        #     time='2023-11-17 17:15',
        #     action='1 pull-aps',
        #     frequency=2,
        #     duration=6,
        #     is_public=True
        # )

        no_data = {}

        response = self.client.put(f'/habit/{self.habit_1.pk}/update/', no_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'place': ['This field is required.'],
                                           'time': ['This field is required.'],
                                           'action': ['This field is required.'],
                                           'duration': ['This field is required.']})

        response = self.client.put(f'/habit/{self.habit_2.pk}/update/', no_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'Вы не являетесь владельцем этой привычки.'})

        response = self.client.patch(f'/habit/{self.habit_1.pk}/update/', invalid_frequency)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'frequency': ['Ensure this value is greater than or equal to 1.']})

        response = self.client.patch(f'/habit/{self.habit_1.pk}/update/', invalid_frequency_2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'frequency': ['Ensure this value is less than or equal to 7.']})

        response = self.client.patch(f'/habit/{self.habit_1.pk}/update/', invalid_duration)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.json())
        # self.assertEqual(response.json(), {'duration': ['Ensure this value is less than or equal to 120.']})

        # response = self.client.put(f'/habit/{self.habit_1.pk}/update/', test_data)

        # print(response.json())

    def test_update_habit_with_task(self):
        """Тестирование изменений периодической задачи при изменении привычки"""

        valid_data_periodic = dict(
            place='test_habit_3',
            time='2023-11-17 17:17',
            action='1 pull-aps',
            frequency=3,
            related_habit=self.habit_2.pk,
            duration=6
        )

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['admin_user'])

        response = self.client.put(f'/habit/{self.habit_3.pk}/update/', valid_data_periodic)
        response_data = dict(id=self.habit_3.pk, place='test_habit_3', time='2023-11-17T17:17:00+03:00',
                             action='1 pull-aps', is_pleasurable=False, frequency=3, duration=6, is_public=False,
                             task_id=self.habit_3.task_id, reward=None, user=self.habit_3.user.pk,
                             related_habit=self.habit_2.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), response_data)
        self.assertEqual(PeriodicTask.objects.filter(pk=self.habit_3.task_id).exists(), True)

    def test_delete_habit(self):
        """Тестирование удаления привычки и периодической задачи"""
        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['admin_user'])

        response = self.client.delete(f'/habit/{self.habit_3.pk}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(pk=self.habit_3.pk).exists(), False)
        self.assertEqual(PeriodicTask.objects.filter(pk=self.habit_3.task_id).exists(), False)

    def test_public_habit_list(self):
        """Тестирование списка публичных привычек"""

        habits = Habit.objects.filter(is_public=True)

        self.client.credentials(HTTP_AUTHORIZATION=self.credentials['user'])

        response = self.client.get('/habit/public_list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(habits))
