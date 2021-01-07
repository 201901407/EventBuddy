from django.shortcuts import render,redirect
from Home.models import User,Event
from django.http import HttpResponse
import datetime

# Create your views here.
def home(request,uname=''):
    elst = []
    i=1     #for displaying only three items on user's home page
    #collect the events in which user has participated or is the host
    for all_events in Event.objects.all():
        if i <= 3:
            if all_events.host == uname:
                elst.append(all_events)
                i += 1
        else:
            break
    return render(request,'home.html',{'uname':uname,'eventlst':elst})

def signin(request):
    if request.method == 'POST':
        email = request.POST['mail']
        password = request.POST['paword']
        if not email or not password:
            return render(request,'signin.html',{'message':'Please fill out all the fields.'})
        else:    
            for all_users in User.objects.all():
                if password == all_users.password and email == all_users.email:
                    #redirect to user's home page if credentials are valid
                    return redirect( home , uname = all_users.name)
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
        else:  
            for all_users in User.objects.all():
                #validation which checks whether user with same credentials already exist or not
                if email == all_users.email:
                    return render(request,'signup.html',{'message':'Email already exists. Please enter another email.'})

            #saving data to database        
            temp = User(email=email,password=password,name=name)        
            temp.save()

            #redirect to user's home page if credentials are valid
            return redirect( home, uname = name ) 
    else:
        return render(request,'signup.html')           

def newevent(request,uname=''):
    if request.method == 'POST':
        name = request.POST['ename']
        event_start_date = request.POST['estartd']
        event_start_time = request.POST['estartt']
        event_end_date = request.POST['eendd']
        event_end_time = request.POST['eendt']
        if not name or not event_start_date or not event_start_time or not event_end_date or not event_end_time:
            return render(request,'createevent.html',{'message':'Please fill out all the fields.'})
        else:
             #separating out data to create datetime instance
             es = datetime.datetime(int(event_start_date[:4]),int(event_start_date[5:7]),int(event_start_date[8:]),int(event_start_time[:2]),int(event_start_time[3:]))  
             ee = datetime.datetime(int(event_end_date[:4]),int(event_end_date[5:7]),int(event_end_date[8:]),int(event_end_time[:2]),int(event_end_time[3:]))
             edes = request.POST['edes']

             #validation logic for event dates and times
             dtnow = datetime.datetime.now().strftime('%Y-%m-%d')
             timenow = datetime.datetime.now().strftime('%H:%M')

             if event_end_date < dtnow or event_end_date < dtnow:
                 return render(request,'createevent.html',{'message':'Start date or end date can\'t be before current date'})
             if event_start_date > event_end_date:
                 return render(request,'createevent.html',{'message':'Start date must be before end date'})    
             if event_start_time < timenow or event_end_time < timenow:
                 return render(request,'createevent.html',{'message':'Start time must be after current time.'})
             if event_start_time > event_end_time:
                 return render(request,'createevent.html',{'message':'Start time must be before end time.'})      

             #saving data in database if validation is true    
             for all_events in Event.objects.all():
                 if name == all_events.event_name and (es == all_events.event_start or ee == all_events.event_end):
                     return render(request,'createevent.html',{'message':'Event with same credentials already exists.'})
             temp = Event(event_name = name, event_start = es,event_end = ee,host = uname,event_description = edes)
             temp.save()

             #redirect to home page once event is created
             return redirect(home,uname = uname)
    else:
        return render(request,'createevent.html')      

def allevent(request,uname=''):
    return render(request,'allevents.html',{'uname':uname})                  