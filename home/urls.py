from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path('', views.index, name="home"),
    path('login', views.loginUser, name="login"),
    path('logout', views.logoutUser, name="logout"),
    path('addstudents', views.addstudents, name="addstudents"),
    path('addclassrooms', views.addclassrooms, name="addclassrooms"),
    path('generateseating', views.generateseating, name="generateseating"),
    path('generatecomplex', views.generatecomplex, name="generatecomplex")
]
