from django.contrib import admin
from django.urls import path
from csprediction import views

urlpatterns = [
    path("login/", views.index, name='login'),
    path("register/", views.registration, name='registration'),
    path("contact/", views.contact, name='contact'),
    path("predictor/", views.predictor, name='predictor'),
    path("about/", views.about, name='about'),
    path("", views.home, name='home'),
    path("logout/", views.logout_view, name="logout"),
]



