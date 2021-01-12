from django.shortcuts import render,redirect
from Home.models import User,Event,Participant
from django.http import HttpResponse
from django.utils import timezone
import datetime

# Create your views here.
def home(request,uid=''):
    elst = []
    eidlst = []
    i=1     #for displaying only three items on user's home page
    for all_users in User.objects.all():
        if all_users.user_id == uid:
            uname = all_users.name
            umail = all_users.email
    if uid == '':
        uname = ''  
        umail = ''      
    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            all_events.delete()    
    #collect the events in which user has participated or is the host  
    for all_participants in Participant.objects.all():
        if all_participants.participant_email == umail:
            eidlst.append(all_participants.pevent_id)
    for all_events in Event.objects.all():
        if i <= 3:
            if all_events.host_email == umail:
                elst.append(all_events)  
                i += 1 
        else:
            break     
    for entry in eidlst:      
        for all_events in Event.objects.all():
            if i <= 3:
                if all_events.event_id == entry:
                    elst.append(all_events)
                    i += 1
            else:
                break             
    elst.sort(key = lambda eve : eve.event_start)        
    return render(request,'home.html',{'uname':uname,'eventlst':elst,'uid':uid,'umail':umail})

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
                    return redirect( home , uid = all_users.user_id)
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
            return redirect( home, uid = temp.user_id ) 
    else:
        return render(request,'signup.html')           

def newevent(request,uid=''):
    if request.method == 'POST':
        name = request.POST['ename']
        event_start_date = request.POST['estartd']
        event_start_time = request.POST['estartt']
        event_end_date = request.POST['eendd']
        event_end_time = request.POST['eendt']
        for all_users in User.objects.all():
            if all_users.user_id == uid:
                uname = all_users.name
                umail = all_users.email
        if uid == '':
            uname = ''  
            umail = ''
        if not name or not event_start_date or not event_start_time or not event_end_date or not event_end_time:
            return render(request,'createevent.html',{'message':'Please fill out all the fields.','uid':uid})
        else:
             #separating out data to create datetime instance
             es = datetime.datetime(int(event_start_date[:4]),int(event_start_date[5:7]),int(event_start_date[8:]),int(event_start_time[:2]),int(event_start_time[3:]))  
             ee = datetime.datetime(int(event_end_date[:4]),int(event_end_date[5:7]),int(event_end_date[8:]),int(event_end_time[:2]),int(event_end_time[3:]))
             edes = request.POST['edes']

             #validation logic for event dates and times
             dtnow = datetime.datetime.now().strftime('%Y-%m-%d')
             timenow = datetime.datetime.now().strftime('%H:%M')

             if event_end_date < dtnow or event_end_date < dtnow:
                 return render(request,'createevent.html',{'message':'Start date or end date can\'t be before current date','uid':uid})
             if event_start_date > event_end_date:
                 return render(request,'createevent.html',{'message':'Start date must be before end date','uid':uid})    
             if event_start_date == dtnow and (event_start_time < timenow or event_end_time < timenow):
                 return render(request,'createevent.html',{'message':'Start time must be after current time for current date.','uid':uid})
             if event_start_time > event_end_time:
                 return render(request,'createevent.html',{'message':'Start time must be before end time.','uid':uid})      

             #saving data in database if validation is true    
             for all_events in Event.objects.all():
                 if name == all_events.event_name and (es == all_events.event_start or ee == all_events.event_end):
                     return render(request,'createevent.html',{'message':'Event with same credentials already exists.','uid':uid})
             temp = Event(event_name = name, event_start = es,event_end = ee,host_email = umail,host_name = uname,event_description = edes)
             temp.save()

             #redirect to home page once event is created
             return redirect(home,uid = uid)
    else:
        return render(request,'createevent.html',{'uid':uid})      

def allevent(request,uid=''):
    elst = []
    eidlst = []
    for all_users in User.objects.all():
        if all_users.user_id == uid:
            uname = all_users.name
            umail = all_users.email
    if uid == '':
        uname = ''  
        umail = ''
    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            all_events.delete()     
    for all_participants in Participant.objects.all():
            if all_participants.participant_email == umail:
                eidlst.append(all_participants.pevent_id)
    for all_events in Event.objects.all():
            if all_events.host_email == umail:
                elst.append(all_events)     
    for entry in eidlst:      
        for all_events in Event.objects.all():
                if all_events.event_id == entry:
                    elst.append(all_events)           
    elst.sort(key = lambda eve : eve.event_start)                   
    return render(request,'allevents.html',{'uname':uname,'alleventlst':elst,'uid':uid,'umail':umail})  

def deleteevent(request,uid='',eid=''):
    for all_events in Event.objects.all():
        if all_events.event_id == eid:
            all_events.delete()
    return redirect(home,uid = uid)  


def explore(request,uid=''):
    exp = []
    for all_users in User.objects.all():
        if all_users.user_id == uid:
            uname = all_users.name
            umail = all_users.email
    if uid == '':
        uname = ''  
        umail = ''
    curr_dt = timezone.now()
    print(curr_dt)
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            all_events.delete()     
    for all_events in Event.objects.all():
        exp.append(all_events)
    exp.sort(key  = lambda eve: eve.event_start)    
    return render(request,'explorepage.html',{'explst':exp,'uid':uid,'uname':uname,'umail':umail})    

def participate(request,uid='',eid=''):
    if request.method == 'POST':
        for all_users in User.objects.all():
            if all_users.user_id == uid:
                uname = all_users.name
                umail = all_users.email
        if uid == '':
            uname = ''  
            umail = ''
        cono = request.POST['cono']
        reg = request.POST.get('grpreg')
        if reg == 'group':
            isGrp = True
            nopar = request.POST['nopar']
        else:
            isGrp = False
            nopar = 1    
        if not cono or not reg or not nopar:
            return render(request,'participantform.html',{'uid':uid,'eid':eid,'message':'Please fill out all the fields.'})
        for all_participants in Participant.objects.all():    
            if all_participants.participant_email == umail and all_participants.pevent_id == eid:
                return render(request,'participantform.html',{'uid':uid,'eid':eid,'message':'You have already participated in this event.'})
        for all_events in Event.objects.all():
            if all_events.event_id == eid:
                temp = Participant(pevent_id = eid, participant_email = umail, participant_contactno = cono,participant_name = uname,group_registration=isGrp
                ,no_of_members = nopar)      
                try:
                    temp.save()
                except ValueError:
                    return render(request,'participantform.html',{'uid':uid,'eid':eid,'message':'Contact Number should only consist of numbers.'})
                return redirect(explore, uid = uid)  
    else:    
        return render(request,'participantform.html',{'uid':uid,'eid':eid})    


def viewprofile(request,uid=''):
    for all_users in User.objects.all():
        if all_users.user_id == uid:
                uname = all_users.name
                umail = all_users.email
    if uid == '':
            uname = ''  
            umail = ''
    return render(request,'profilepage.html',{'uid':uid,'uname':uname,'umail':umail})

def changepassword(request,uid=''):
    if request.method == 'POST':
        oldpass = request.POST['cono']
        confirmpass = request.POST['cnewpass']
        newpass = request.POST['newpass']
        if not oldpass or not newpass or not confirmpass:
            return render(request,'changepass.html',{'uid':uid,'err':'Please fill out all the fields.'})  
        if newpass != confirmpass:
            return render(request,'changepass.html',{'uid':uid,'err':'Please enter new password in confirm password.'})    
        for all_users in User.objects.all():
            if all_users.user_id == uid:
                if all_users.password != oldpass:      
                    return render(request,'changepass.html',{'uid':uid,'err':'Old password is incorrect!'})
                else:
                    all_users.password = newpass
                    all_users.save()
                    return redirect(viewprofile,uid = uid)
    else:    
        return render(request,'changepass.html',{'uid':uid})    