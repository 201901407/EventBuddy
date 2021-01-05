from django.shortcuts import render,redirect
from Home.models import User
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request,'home.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST['mail']
        password = request.POST['paword']
        if not email or not password:
            return render(request,'signin.html',{'message':'Please fill out all the fields.'})
        else:    
            for all_users in User.objects.all():
                if password == all_users.password and email == all_users.email:
                    return redirect( home )
            return render(request,'signin.html',{'message':'Email or Password is incorrect!'})
    else:
        return render(request,'signin.html')        

def signup(request):
    if request.method == 'POST':
        email = request.POST['mail']
        password = request.POST['paword']
        name = request.POST['uname']
        if not email or not password or not name:
            return render(request,'signup.html',{'message':'Please fill out all the fields.'})
        else:  #logic here
            for all_users in User.objects.all():
                if email == all_users.email:
                    return render(request,'signup.html',{'message':'Email already exists. Please enter another email.'})
            temp = User(email=email,password=password,name=name)        
            temp.save()
            return redirect( home ) 
    else:
        return render(request,'signup.html')           