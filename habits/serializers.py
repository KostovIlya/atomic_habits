from rest_framework import serializers

from habits.models import Habit
from habits.validators import HabitValidator


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор привычек"""

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ['user']
        validators = [HabitValidator(is_pleasurable='is_pleasurable', related_habit='related_habit', reward='reward')]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        valid_fields = dict(is_pleasurable=instance.is_pleasurable,
                            related_habit=instance.related_habit.pk if instance.related_habit else None,
                            reward=instance.reward)

        self.run_validation(valid_fields)
        instance.save()
        return instance
