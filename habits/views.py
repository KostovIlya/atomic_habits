from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from habits.models import Habit
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer
from habits.services import send_message_bot, create_periodic_task, update_periodic_task, delete_periodic_task


class HabitCreateAPIView(generics.CreateAPIView):
    """
    Создание привычки с добавлением задачи на отправку уведомлений
    """

    serializer_class = HabitSerializer

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        if not habit.is_pleasurable:
            create_periodic_task(habit)


class HabitUpdateAPIView(generics.UpdateAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsOwner]

    def perform_update(self, serializer):
        habit = serializer.save()
        update_periodic_task(habit)


class HabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsOwner | IsAdminUser]


class HabitDestroyAPIView(generics.DestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = [IsOwner]

    def perform_destroy(self, instance):
        delete_periodic_task(instance)
        instance.delete()


class PublicHabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_public=True)
