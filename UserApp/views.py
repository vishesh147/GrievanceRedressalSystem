from django.shortcuts import render, redirect
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from GrievanceRedressalSystemApp.models import Grievance, Grievant, Update, Handler
from django.template.loader import render_to_string
from html2text import html2text
from django.contrib import messages

@login_required(login_url='landing')
def Dashboard(request):
    try:
        grievant = Grievant.objects.get(user=request.user)
    except:
        raise PermissionDenied
    grievances = Grievance.objects.filter(grievant=grievant).order_by('-created')
    return render(request, 'userdashboard.html', {'grievances':grievances})    


@login_required(login_url='landing')
def FileGrievance(request):
    try:
        grievant = Grievant.objects.get(user=request.user)
    except:
        raise PermissionDenied

    if request.method == 'POST':
        category = request.POST.get('category', '')
        subject = request.POST.get('subject', '')
        timestamp = datetime.now()
        
        grievance = Grievance(
            grievanceID="GRC"+timestamp.strftime("%d%m%y%H%M%S"), 
            grievant=grievant, 
            grievantType=grievant.uType, 
            category=category, 
            subject=subject,
            created=timestamp,
            content=request.POST.get('content'),
        )
        
        try:
            handler = Handler.objects.get(grievantType=grievant.uType, category=grievance.category, level=1)
            html_text_h = render_to_string('newGrievanceEmailH.html', {'grievance':grievance, 'grievant':grievant})
            plain_text_h = html2text(html_text_h) 
            hEmail = EmailMultiAlternatives(
                subject="A New Grievance has been Registered : " + grievance.grievanceID,
                body=plain_text_h,
                to=[handler.user.email],
            )
            hEmail.attach_alternative(html_text_h, "text/html")
            hEmail.send()

            html_text_g = render_to_string('newGrievanceEmailG.html', {'grievance':grievance, 'handler':handler})
            plain_text_g = html2text(html_text_g) 
            gEmail = EmailMultiAlternatives(
                subject="Your Grievance has been Registered : " + grievance.grievanceID,
                body=plain_text_g,
                to=[grievant.user.email],
            )
            gEmail.attach_alternative(html_text_g, "text/html")
            gEmail.send()

            grievance.save()
        except:
            messages.error(request, "An error occured. Please Try Again Later.")
            return redirect('userDashboard')
        
        return redirect('userDashboard')

    studentOptions = {
        "Teaching-Learning and Evaluation":"academic",
        "Registration, Fees, Results and Transcripts":"registration",
        "Internships and Placement":"placement",
        "General Amenities and Services":"general",
        "Student to Student Grievances":"stud2stud",
    }
    facultyStaffOptions = {
        "Human Resource and Administration":"hra",
        "Matters related to an Action of any Member of the Faculty":"facultyAction",
        "Matters related to an Action of any Member of the Staff":"staffAction",
        "Matters related to Service Conditions":"service"
    }
    
    if grievant.uType == 'student':
        return render(request, 'grievanceForm.html', {'options': studentOptions})
    else:
        return render(request, 'grievanceForm.html', {'options': facultyStaffOptions})


@login_required(login_url='landing')
def ViewGrievance(request, gID):
    try:
        grievant = Grievant.objects.get(user=request.user)
    except:
        raise PermissionDenied
    grievance = Grievance.objects.get(grievanceID=gID)
    if grievant != grievance.grievant:
        return PermissionDenied
    conversation = Update.objects.filter(grievanceID = gID).order_by('timestamp')
    return render(request, 'usergrievance.html', {'grievance':grievance, 'conversation':conversation})
