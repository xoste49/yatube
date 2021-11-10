from django.urls import path
from . import views

'''
path() для страницы регистрации нового пользователя
её полный адрес будет auth/signup/,
но префикс auth/ обрабатывается в головном urls.py
'''
urlpatterns = [
    # path() для страницы регистрации нового пользователя
    # её полный адрес будет auth/signup/, но префикс auth/ обрабатывается в головном urls.py
    path("signup/", views.SignUpView.as_view(), name="signup")
]
