from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('<str:uid>home',views.home,name="home"),
    path('signin',views.signin,name="signin"),
    path('signup',views.signup,name="signup"),
    path('<str:uid>home/newevent',views.newevent,name="newevent"),
    path('<str:uid>home/allevent',views.allevent,name="allevent"),
    path('<str:uid>home/delevent<str:eid>',views.deleteevent,name="deleteevent"),
    path('<str:uid>home/explore',views.explore,name="explore"),
    path('explore',views.explore,name="explore"),
    path('<str:uid>home/participantform<str:eid>',views.participate,name="participate"),
    path('<str:uid>home/profile',views.viewprofile,name="viewprofile"),
    path('<str:uid>home/profile/changepassword',views.changepassword,name="changepassword"),
]