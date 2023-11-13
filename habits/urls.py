from django.urls import path

from habits.apps import HabitConfig
from habits.views import HabitCreateAPIView, HabitListAPIView, HabitUpdateAPIView, HabitRetrieveAPIView, \
    HabitDestroyAPIView

app_name = HabitConfig.name

urlpatterns = [
    path('habit/create/', HabitCreateAPIView.as_view(), name='habit-create'),
    path('habit/list/', HabitListAPIView.as_view(), name='habit-list'),
    path('habit/<int:pk>/update/', HabitUpdateAPIView.as_view(), name='habit-update'),
    path('habit/<int:pk>/', HabitRetrieveAPIView.as_view(), name='habit'),
    path('habit/<int:pk>/delete/', HabitDestroyAPIView.as_view(), name='habit-delete'),

]