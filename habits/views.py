from django.shortcuts import render
from rest_framework import generics

from habits.models import Habit
from habits.serializers import HabitSerializer


class HabitCreateAPIView(generics.CreateAPIView):
    serializer_class = HabitSerializer


class HabitUpdateAPIView(generics.UpdateAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()


class HabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()


class HabitDestroyAPIView(generics.DestroyAPIView):
    queryset = Habit.objects.all()
