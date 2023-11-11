from rest_framework import serializers

from habits.models import Habit


class HabitSerializer(serializers):
    class Meta:
        model = Habit
        fields = '__all__'
