from EventManager import settings 
from twilio.rest import Client
from django.core.exceptions import PermissionDenied
from django.template import Context, Template
from django.shortcuts import render,redirect
from Home.models import User,Event,Participant
from django.core.mail import send_mail 
from django.http import HttpResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
import datetime

partlst = []                          #global list for displaying participants for a particular event on home page
flag = 0                              #boolean variable for deciding whether to display participants or not on home page

# Create your views here.
def home(request,uid=''):
    #use global variant of flag instead of creating local variant of it
    global flag                 
    elst = []
    eidlst = []
    expired_eventid_lst = []
    
    if uid != '' and request.session['auth_key'] != uid:
        raise PermissionDenied()


    #for displaying only three items on user's home page
    i=1             

    #if flag is set to 0 then don't display anything else display related information
    if flag == 0:
        templst = []
    else:
        templst = partlst    

    #assign additional info to display on webpage                         
    for all_users in User.objects.all():
        if all_users.user_id == uid:
            uname = all_users.name
            umail = all_users.email
    if uid == '':
        uname = ''  
        umail = ''      

    #automatically remove events from the database which are ongoing or are finished    
    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()    

    #simultaneously remove the participants of these events from participant database        
    for ids in expired_eventid_lst:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()     

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

    #sorting the list according to start dates          
    elst.sort(key = lambda eve : eve.event_start)        
    flag = 0
    return render(request,'home.html',{'uname':uname,'eventlst':elst,'uid':uid,'umail':umail,'partlst':templst})

def signin(request):
    if request.method == 'POST':
        email = request.POST['mail']
        password = request.POST['paword']
        if not email or not password:
            return render(request,'signin.html',{'message':'Please fill out all the fields.'})
        else:    
            for all_users in User.objects.all():
                if check_password(password,all_users.password) and email == all_users.email:

                    #code to send the mail to user upon signin. Uncomment the lines below to enable this feature.
                    #Set the variables EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to the email ID and corresponding password in settings.py
                    #curr_time = timezone.now()
                    #subject = 'Alert for signin into your EventBuddy account'
                    #mailtemplate = Template('Hello {{sname}},\n\nA new signin was detected in your EventBuddy account {{semail}} at {{curr_time}}(GMT +5). If it was you, then your account is fully secure but if not then, change your password immediately.\nRegards,\nEventBuddy Team')
                    #context = Context({'sname':all_users.name,'semail':all_users.email,'curr_time':curr_time})
                    #mailbody = mailtemplate.render(context)
                    #email_from = settings.EMAIL_HOST_USER
                    #recipients = [all_users.email]
                    #try:
                    #    send_mail(subject, mailbody, email_from, recipients) 
                    #except SMTPException:
                    #    print("Mail couldn\'t be sent.")
                    #redirect to user's home page if credentials are valid

                    request.session['auth_key'] = all_users.user_id
                    print(request.session.items())
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
            #email validation
            try:
                validate_email(email)
            except ValidationError:
                return render(request,'signup.html',{'message':'Please enter valid email ID.'}) 
            for all_users in User.objects.all():
                #validation which checks whether user with same credentials already exist or not
                if email == all_users.email:
                    return render(request,'signup.html',{'message':'Email already exists. Please enter another email.'})

            #saving data to database        
            password = make_password(password)                       #encrypting the password using PBKDF2 hasher
            temp = User(email=email,password=password,name=name)        
            temp.save()

            #code to send the mail to user upon signup. Uncomment the lines below to enable this feature.
            #Set the variables EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to the email ID and corresponding password in settings.py
            #subjecttemplate = Template('Welcome to EventBuddy, {{sname}}!')
            #mailtemplate = Template('Hello {{sname}},\n\nWelcome to EventBuddy. We are glad to have you here. Start exploring and participating in various events or create a new event.\nRegards,\nEventBuddy Team')
            #context = Context({'sname':name})
            #mailbody = mailtemplate.render(context)
            #subject = subjecttemplate.render(context)
            #email_from = settings.EMAIL_HOST_USER
            #recipients = [email]
            #try:
            #    send_mail(subject, mailbody, email_from, recipients) 
            #except SMTPException:
            #    print("Mail couldn\'t be sent.")
            #-----Uncomment till here----

            #redirect to user's home page if credentials are valid
            return redirect(signin) 
    else:
        return render(request,'signup.html')           

def newevent(request,uid=''):
    if request.method == 'POST':
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
        name = request.POST['ename']
        event_start_date = request.POST['estartd']
        event_start_time = request.POST['estartt']
        event_end_date = request.POST['eendd']
        event_end_time = request.POST['eendt']
        regendd = request.POST['regendd']
        regendt = request.POST['regendt']
        poslink = request.POST['plink']
        for all_users in User.objects.all():
            if all_users.user_id == uid:
                uname = all_users.name
                umail = all_users.email
        if uid == '':
            uname = ''  
            umail = ''
        if not name or not event_start_date or not event_start_time or not event_end_date or not event_end_time or not regendd or not regendt or not poslink:
            return render(request,'createevent.html',{'message':'Please fill out all the fields.','uid':uid})
        else:
             #separating out data to create datetime instance
             es = datetime.datetime(int(event_start_date[:4]),int(event_start_date[5:7]),int(event_start_date[8:]),int(event_start_time[:2]),int(event_start_time[3:]))  
             ee = datetime.datetime(int(event_end_date[:4]),int(event_end_date[5:7]),int(event_end_date[8:]),int(event_end_time[:2]),int(event_end_time[3:]))
             regdate = datetime.datetime(int(regendd[:4]),int(regendd[5:7]),int(regendd[8:]),int(regendt[:2]),int(regendt[3:]))
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
             if regendd > event_start_date or regendd < dtnow:
                 return render(request,'createevent.html',{'message':'Deadline date must be before end date or after current date.','uid':uid})   
             if regendd == dtnow and regendt <= timenow:
                 return render(request,'createevent.html',{'message':'Deadline time must be after current time.','uid':uid})    

             try:
                 URLValidator()(poslink)
             except ValidationError:
                 return render(request,'createevent.html',{'message':'Please enter valid URL.','uid':uid})         
  
             #saving data in database if validation is true    
             for all_events in Event.objects.all():
                 if name == all_events.event_name and (es == all_events.event_start or ee == all_events.event_end):
                     return render(request,'createevent.html',{'message':'Event with same credentials already exists.','uid':uid})
             temp = Event(event_name = name, event_start = es,event_end = ee,host_email = umail,host_name = uname,event_description = edes,registration_deadline=regdate,event_poster = poslink)
             temp.save()

             #code to send the mail to user upon creation of new event. Uncomment the lines below to enable this feature.
             #Set the variables EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to the email ID and corresponding password in settings.py
             #subject = 'New Event created in EventBuddy'
             #mailtemplate = Template(("Hello {{sname}},\n\nYou recently created the event with following credentials on EventBuddy:\nName of event: {{ename}}\nStart of event: {{estart}}\nEnd of event: {{eend}}\n"
             #"Host: {{host}}\nEvent Description: {{edest}}\nParticipation deadline: {{regde}}\n\nRegards,\nEventBuddy Team"))
             #context = Context({'sname':uname,'ename':name,'estart':es,'eend':ee,'host':uname,'edest':edes,'regde':regdate})
             #mailbody = mailtemplate.render(context)
             #email_from = settings.EMAIL_HOST_USER
             #recipients = [umail]
             #try:
             #    send_mail(subject, mailbody, email_from, recipients) 
             #except SMTPException:
             #    print("Mail couldn\'t be sent.")
             #----Uncomment till here-----
    
             #redirect to home page once event is created
             return redirect(home,uid = uid)
    else:
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
        return render(request,'createevent.html',{'uid':uid})      

def allevent(request,uid=''):
    if uid != '' and request.session['auth_key'] != uid:
        raise PermissionDenied()
    expired_eventid_lst = []
    elst = []
    eidlst = []
    for all_users in User.objects.all():
        if all_users.user_id == uid:
            uname = all_users.name
            umail = all_users.email
    if uid == '':
        uname = ''  
        umail = ''

    #automatically remove events from the database which are ongoing or are finished and their corresponding participants
    curr_dt = timezone.now()
    for all_events in Event.objects.all():
        if all_events.event_start < curr_dt:
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()     

    #simultaneously remove the participants of these events from participant database        
    for ids in expired_eventid_lst:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()          

    #collect the events in which user has participated or is the host  
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

    #sort the list according to start dates                    
    elst.sort(key = lambda eve : eve.event_start)                   
    return render(request,'allevents.html',{'uname':uname,'alleventlst':elst,'uid':uid,'umail':umail})  

def deleteevent(request,uid='',eid=''):
    if uid != '' and request.session['auth_key'] != uid:
        raise PermissionDenied()

    #find the event which has to be deleted in database and delete it
    for all_events in Event.objects.all():
        if all_events.event_id == eid:
            all_events.delete()

    #also delete the participants of that corresponding event        
    for all_participants in Participant.objects.all():
        if all_participants.pevent_id == eid:
            all_participants.delete()        
    return redirect(home,uid = uid)  


def explore(request,uid=''):
    if uid != '' and request.session['auth_key'] != uid:
        raise PermissionDenied()
    exp = []
    expired_eventid_lst = []
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
            expired_eventid_lst.append(all_events.event_id)
            all_events.delete()     
    for ids in expired_eventid_lst:
        for all_participants in Participant.objects.all():
            if all_participants.pevent_id == ids:
                all_participants.delete()         
    for all_events in Event.objects.all():
        exp.append(all_events)
    exp.sort(key  = lambda eve: eve.event_start)    
    return render(request,'explorepage.html',{'explst':exp,'uid':uid,'uname':uname,'umail':umail,'curr_dt':curr_dt})    

def participate(request,uid='',eid=''):
    if request.method == 'POST':
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
        #extracting additional info from database
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
        if len(cono) != 10:
            return render(request,'participantform.html',{'uid':uid,'eid':eid,'message':'Please enter valid contact number.'})

        #logic for checking whether the user has participated in event or not    
        for all_participants in Participant.objects.all():    
            if all_participants.participant_email == umail and all_participants.pevent_id == eid:
                return render(request,'participantform.html',{'uid':uid,'eid':eid,'message':'You have already participated in this event.'})
        
        #save the participant data to the database if validation is true
        curr_time = timezone.now()
        for all_events in Event.objects.all():
            if all_events.event_id == eid:
                if all_events.registration_deadline < curr_time:
                    return render(request,'participantform.html',{'uid':uid,'eid':eid,'message':'The participation deadline has passed.'})
                temp = Participant(pevent_id = eid, participant_email = umail, participant_contactno = cono,participant_name = uname,group_registration=isGrp
                ,no_of_members = nopar)      
                try:
                    temp.save()

                    #code to send the mail to user upon participating. Uncomment the lines below to enable this feature.
                    #Set the variables EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to the email ID and corresponding password in settings.py
                    #subject = 'New Participation in EventBuddy'
                    #mailtemplate = Template(("Hello {{sname}},\n\nYou recently participated in the event with following credentials on EventBuddy:\nName of event: {{ename}}\nStart of event: {{estart}}\nEnd of event: {{eend}}\n"
                    #"Host: {{host}}\nEvent Description: {{edest}}\n\nRegards,\nEventBuddy Team"))
                    #context = Context({'sname':uname,'ename':all_events.event_name,'estart':all_events.event_start,'eend':all_events.event_end,'host':uname,'edest':all_events.event_description})
                    #mailbody = mailtemplate.render(context)
                    #email_from = settings.EMAIL_HOST_USER
                    #recipients = [umail]
                    #try:
                    #    send_mail(subject, mailbody, email_from, recipients) 
                    #except SMTPException:
                    #    print("Mail couldn\'t be sent.")
                    #-----Uncomment tii here----

    
                    #code for sending phone messages to user upon participating using Twilio API. Uncomment the lines below to enable this feature.
                    #Set the variables TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN and TWILIO_NUMBER to your choice in settings.py.
                    #messagetemplate = Template(("You recently participated in the event with following credentials on EventBuddy:\nName of event: {{ename}}\nStart of event: {{estart}}\nEnd of event: {{eend}}\n"
                    #"Host: {{host}}\nEvent Description: {{edest}}"))
                    #context = Context({'ename':all_events.event_name,'estart':all_events.event_start,'eend':all_events.event_end,'host':uname,'edest':all_events.event_description})
                    #message_body = messagetemplate.render(context)
                    #cono_modified = '+91' + cono
                    #try:
                    #    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    #    client.messages.create(to=cono_modified,from_=settings.TWILIO_NUMBER,body=message_body)
                    #except TwilioRestException:
                    #    print("Message couldn\'t be sent")    
                    #----Uncomment till here-----


                except ValueError:
                    return render(request,'participantform.html',{'uid':uid,'eid':eid,'message':'Contact Number should only consist of numbers.'})
                return redirect(explore, uid = uid)  
    else:    
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
        return render(request,'participantform.html',{'uid':uid,'eid':eid})    


def viewprofile(request,uid=''):
    if uid != '' and request.session['auth_key'] != uid:
        raise PermissionDenied()
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
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
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

                    #code to send the mail to user upon changing password. Uncomment the lines below to enable this feature.
                    #Set the variables EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to the email ID and corresponding password in settings.py
                    #subject = 'Password of your EventBuddy account changed'
                    #mailtemplate = Template(("Hello {{sname}},\n\nThe password of your EventBuddy account {{uemail}} was recently changed at {{curr_time}}(GMT +5). If it was you,"
                    #" then your account is fully secure but if not, then change your password again immediately.\n\nRegards,\nEventBuddy Team"))
                    #context = Context({'sname':all_users.name,'uemail':all_users.email,'curr_time':timezone.now()})
                    #mailbody = mailtemplate.render(context)
                    #email_from = settings.EMAIL_HOST_USER
                    #recipients = [all_users.email]
                    #try:
                    #    send_mail(subject, mailbody, email_from, recipients) 
                    #except SMTPException:
                    #    print("Mail couldn\'t be sent.")


                    return redirect(viewprofile,uid = uid)
    else:    
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
        return render(request,'changepass.html',{'uid':uid}) 

def changename(request,uid=''):
    if request.method == 'POST':
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
        newname = request.POST['upname']
        if not newname:
            return render(request,'chgname.html',{'uid':uid,'err':'Please fill out all the fields.'})
        for all_users in User.objects.all():
            if all_users.user_id == uid:
                temp = all_users.email
                all_users.name = newname
                all_users.save()    
        for all_participants in Participant.objects.all():
            if all_participants.participant_email == temp:
                all_participants.participant_name = newname
                all_participants.save()    

        return redirect(viewprofile,uid = uid)       
    else:
        if uid != '' and request.session['auth_key'] != uid:
            raise PermissionDenied()
        return render(request,'chgname.html',{'uid':uid})    


def viewparticipant(request,uid='',eid=''):
    if uid != '' and request.session['auth_key'] != uid:
        raise PermissionDenied()
    #clear the list everytime the user requests for participant information
    partlst.clear()
    global flag
    flag = 1
    for all_participants in Participant.objects.all():
        if all_participants.pevent_id == eid:
            partlst.append(all_participants)       
    return redirect(home,uid=uid)          

def signout(request,uid=''):
    request.session['auth_key'] = ''
    return redirect(home)          
