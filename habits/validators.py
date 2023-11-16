from rest_framework.exceptions import ValidationError


class HabitValidator:
    __slots__ = ('is_pleasurable', 'related_habit', 'reward')

    def __init__(self, is_pleasurable: str, related_habit: str, reward: str) -> None:
        self.is_pleasurable = is_pleasurable
        self.related_habit = related_habit
        self.reward = reward

    def __call__(self, value) -> None:
        _is_pleasurable = value.get(self.is_pleasurable)
        _related_habit = value.get(self.related_habit)
        _reward = value.get(self.reward)

        if all((_related_habit, _reward)):
            raise ValidationError('Нельзя одновременно иметь связанную привычку и вознаграждение, выберите что-то одно')
        elif not any((_related_habit, _reward)) and not _is_pleasurable:
            raise ValidationError('Выберите вознаграждение или связанную привычку')

        if _is_pleasurable and any((_related_habit, _reward)):
            raise ValidationError('У приятной привычки не может быть вознаграждения или связанной привычки')

        if _related_habit and not _related_habit.is_pleasurable:
            raise ValidationError(
                'В связанные привычки могут попадать только привычки с признаком приятной привычки.')
