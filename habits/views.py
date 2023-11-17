from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from habits.models import Habit
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer
from habits.services import create_periodic_task, update_periodic_task, delete_periodic_task


class HabitCreateAPIView(generics.CreateAPIView):
    """
        Создание привычки
    """

    serializer_class = HabitSerializer

    def perform_create(self, serializer):
        """Если привычка полезная, добавляем задачу на отправку уведомлений"""

        habit = serializer.save(user=self.request.user)
        if not habit.is_pleasurable:
            create_periodic_task(habit)


class HabitUpdateAPIView(generics.UpdateAPIView):
    """
        Обновление привычки
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsOwner]

    def perform_update(self, serializer):
        """При наличии периодической задачи, Обновление задачи на отправку уведомлений"""

        habit = serializer.save()
        if habit.task_id:
            update_periodic_task(habit)


class HabitListAPIView(generics.ListAPIView):
    """
        Список привычек
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()

    def get_queryset(self):
        """Предоставление доступа персоналу ко всему списку привычек"""

        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    """
        Получение привычки
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsOwner | IsAdminUser]


class HabitDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление привычки
    """
    queryset = Habit.objects.all()
    permission_classes = [IsOwner]

    def perform_destroy(self, instance):
        """При наличии у привычки периодической задачи, её удаление"""
        if instance.task_id:
            delete_periodic_task(instance)
        instance.delete()


class PublicHabitListAPIView(generics.ListAPIView):
    """
        Получение списка публичных привычек
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_public=True)
