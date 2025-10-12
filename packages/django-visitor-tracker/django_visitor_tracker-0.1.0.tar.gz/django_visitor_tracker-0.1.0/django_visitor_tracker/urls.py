from django.urls import path
from . import views

app_name = 'django_visitor_tracker'

urlpatterns = [
    path('stats/', views.stats_view, name='stats'),
    path('counts/', views.summary_counts, name='counts'),
]
