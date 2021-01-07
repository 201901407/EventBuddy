from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('<str:uname>home',views.home,name="home"),
    path('signin',views.signin,name="signin"),
    path('signup',views.signup,name="signup"),
    path('<str:uname>home/newevent',views.newevent,name="newevent"),
    path('<str:uname>home/allevent',views.allevent,name="allevent"),
]