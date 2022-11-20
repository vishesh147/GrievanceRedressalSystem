from django.shortcuts import render, redirect
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from GrievanceRedressalSystemApp.models import Grievance, Update, Handler
from django.template.loader import render_to_string
from html2text import html2text
import pytz
from django.contrib import messages


@login_required(login_url='landing')
def Dashboard(request):
    handler = Handler.objects.filter(user=request.user)
    if not handler:
        raise PermissionDenied

    analytics = 0
    # if request.user.username == 'grhc':
    #     analytics = 1
    analytics = 1
    studentPermissions = handler.filter(grievantType='student')
    staffPermissions = handler.filter(grievantType='staff')
    facultyPermissions = handler.filter(grievantType='faculty')
    grievances = Grievance.objects.none()
    for p in handler:
        grievances |= Grievance.objects.filter(grievantType=p.grievantType, category=p.category).order_by('-created')
    return render(request, 'handlerdashboard.html', {'grievances':grievances, 
            'permissions':{
                'student':studentPermissions,
                'staff':staffPermissions,
                'faculty':facultyPermissions,
            },
            'aP':analytics,
        })


@login_required(login_url='landing')
def ViewGrievance(request, gID):
    grievance = Grievance.objects.get(grievanceID=gID)
    try:
        handler = Handler.objects.get(user=request.user, grievantType=grievance.grievantType, category=grievance.category)
    except:
        raise PermissionDenied

    if request.method == "POST":
        update = Update(grievanceID=grievance, level=grievance.level, sender=request.user, content=request.POST['message'])
        update.save()
        html_text = render_to_string('emails/update.html', {'grievance':grievance, 'update':update})
        plain_text = html2text(html_text) 

        email = EmailMultiAlternatives(
            subject= grievance.grievanceID + " : Grievance Updated",
            body=plain_text,
            to=[grievance.grievant.user.email],
            cc=[handler.user.email],
        )
        email.attach_alternative(html_text, "text/html")
        email.send()

        if not grievance.response :
            grievance.response = datetime.now()
            grievance.save()

        return redirect('handleGrievance', gID=gID)

    conversation = Update.objects.filter(grievanceID = gID).order_by('timestamp')
    
    return render(request, 'handlergrievance.html', {'grievance':grievance, 'conversation':conversation, 
        'handlerLevel':handler.level})



@login_required(login_url='landing')
def Reject(request, gID):
    grievance = Grievance.objects.get(grievanceID=gID)
    try:
        handler = Handler.objects.get(
            user=request.user, 
            grievantType=grievance.grievantType, 
            category=grievance.category, 
            level=grievance.level
        )
    except:
        raise PermissionDenied

    if request.method == "POST":
        grievance.rejected = datetime.now()
        grievance.status = -1

        if not grievance.response :
            grievance.response = datetime.now()

        try:
            html_text = render_to_string('emails/reject.html', {'grievance':grievance, 'reason':request.POST['reason']})
            plain_text = html2text(html_text) 

            email = EmailMultiAlternatives(
                subject=grievance.grievanceID + " : Grievance Rejected",
                body=plain_text,
                to=[grievance.grievant.user.email],
                cc=[handler.user.email],      
            )
            email.attach_alternative(html_text, "text/html")
            email.send()

            grievance.save()
        except:
            messages.error(request, 'Some error occured. Try again.')

    return redirect('handlerDashboard')

@login_required(login_url='landing')
def Solve(request, gID):
    grievance = Grievance.objects.get(grievanceID=gID)
    try:
        handler = Handler.objects.get(
            user=request.user, 
            grievantType=grievance.grievantType, 
            category=grievance.category, 
            level=grievance.level
        )
    except:
        raise PermissionDenied

    if request.method == "POST":
        grievance.solved = datetime.now()
        grievance.status = 1

        if not grievance.response :
                grievance.response = datetime.now()

        try:
            html_text = render_to_string('emails/solve.html', {'grievance':grievance, 'handler':handler, 
                'message':request.POST['message']})
            plain_text = html2text(html_text) 

            email = EmailMultiAlternatives(
                subject=grievance.grievanceID + " : Grievance Solved",
                body=plain_text,
                to=[grievance.grievant.user.email],
                cc=[handler.user.email],      
            )

            email.attach_alternative(html_text, "text/html")
            email.send()
            
            grievance.save()
        except:
            messages.error(request, 'Some error occured. Try again.')

    return redirect('handlerDashboard')


@login_required(login_url='landing')
def Escalate(request, gID):
    grievance = Grievance.objects.get(grievanceID=gID)
    try:
        handler = Handler.objects.get(
            user=request.user, 
            grievantType=grievance.grievantType, 
            category=grievance.category, 
            level=grievance.level
        )
    except:
        raise PermissionDenied

    if not grievance.response :
            grievance.response = datetime.now()

    if grievance.level < 3:
        grievance.level = grievance.level + 1
    if grievance.level == 2:
        grievance.level2 = datetime.now()
    elif grievance.level == 3:
        grievance.level3 = datetime.now()
    grievance.save()

    try:
        nextHandler = Handler.objects.get(
            user=request.user, 
            grievantType=grievance.grievantType, 
            category=grievance.category, 
            level=grievance.level
        )
    except:
        pass

    html_text = render_to_string('emails/escalate.html', {'grievance':grievance})
    plain_text = html2text(html_text) 

    email = EmailMultiAlternatives(
        subject=grievance.grievanceID + " : Grievance Escalated",
        body=plain_text,
        to=[grievance.grievant.user.email],
        cc=[handler.user.email],        # Add email to nextHandler
    )

    email.attach_alternative(html_text, "text/html")
    email.send()

    return redirect('handlerDashboard')



