from rest_framework import serializers

from habits.models import Habit
from habits.validators import HabitValidator


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ['user']
        validators = [HabitValidator(is_pleasurable='is_pleasurable', related_habit='related_habit', reward='reward')]
