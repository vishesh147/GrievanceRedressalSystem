from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Grievant, Handler
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from html2text import html2text
import random
from django.core.mail import EmailMultiAlternatives


def Landing(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            logout(request)
            request.session.flush()
            return redirect('landing')

        if request.session['utype'] == "handler":
            return redirect('handlerDashboard')
        else:
            return redirect('userDashboard')
        
    return render(request, 'landing.html')


def UserLogin(request, slug):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            logout(request)
            request.session.flush()
            return redirect('landing')
        if request.session['utype'] == "handler":
            return redirect('handlerDashboard')
        else:
            return redirect('userDashboard')
            
    if request.method == "POST":
        username = str(request.POST['username'])
        password = str(request.POST['password'])
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, "Invalid user ID or password.")
        else:
            if slug == "handler":
                handler = Handler.objects.filter(user=user)
                if not handler:
                    messages.error(request, "Access Denied.")
                else:
                    request.session['utype'] = "handler"
                    request.session['email'] = user.email
                    request.session.set_expiry(0)
                    # login(request, user)
                    return redirect('OTPlogin')
            else:
                request.session['utype'] = "grievant"
                request.session['email'] = user.email
                request.session.set_expiry(0)
                # login(request, user)
                return redirect('OTPlogin')

    return render(request, 'login.html', context={'type':slug})


def OTPlogin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            logout(request)
            request.session.flush()
            return redirect('landing')
        if request.session['utype'] == "handler":
            return redirect('handlerDashboard')
        else:
            return redirect('userDashboard')

    if request.method == "POST":
        if request.POST['iOTP'] == request.session['otp']:
            user = User.objects.get(email=request.session['email'])
            login(request, user)
            if request.session['utype'] == "handler":
                return redirect('handlerDashboard')
            else:
                return redirect('userDashboard')
        else:
            messages.error(request, 'Invalid OTP.')
            return render(request, 'otplogin.html')
    else:
        otp = ""
        for i in range(6):
            otp += str(random.randint(1,9))
        request.session['otp'] = otp
        request.session.set_expiry(0)

        try:
            html_text = render_to_string('email/otp.html', {'otp':otp})
            plain_text = html2text(html_text) 

            email = EmailMultiAlternatives(
                subject="OTP for Grievance Redressal Portal",
                body=plain_text,
                to=[request.session['email']],      
            )
            email.attach_alternative(html_text, "text/html")
            email.send()
        except:
            messages.error(request, 'Some error occured. Try again later.')

        return render(request, 'otplogin.html')


def Logout(request):
    logout(request)
    request.session.flush()
    return redirect('landing')


@login_required(login_url='landing')
def ChangePass(request):
    if request.method == "POST":
        user = authenticate(username=request.user, password=request.POST['currpass'])
        if user is None:
            messages.error(request, 'Entered current password is incorrect.')
            return render(request, 'changepass.html')

        if request.POST['newpass'] != request.POST['newpass2']:
            messages.error(request, 'Entered passwords do not match.')
            return render(request, 'changepass.html')

        if len(request.POST['newpass']) < 8:
            messages.error(request, 'Password must be atleast 8 characters long.')
            return render(request, 'changepass.html')

        user.set_password(request.POST['newpass'])
        messages.success(request, 'Password changed successfully.')
        return render(request, 'changepass.html')
    
    return render(request, 'changepass.html')


@staff_member_required()
def Upload(request):
    if request.method == "POST":
        csvfile = request.FILES['csvfile']
        csvdata = csvfile.read().decode("utf-8-sig")
        data = csvdata.split('\r\n')
        header = data.pop(0)
        header = header.split(',')
        failed = []
        for line in data:
            if not line:
                continue
            fields = line.split(',')
            username = fields[header.index('user_id')]
            email = fields[header.index('email')]
            first_name = fields[header.index('name')]
            password = fields[header.index('pass')]
            # password = User.objects.make_random_password(length=10)
            # last_name = fields[3]
            try:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
                user.save()
                grievant = Grievant(user=user, uType=request.POST['gtype'])
                grievant.save()
            except:
                failed.append(username)
        return render(request, 'admin/upload.html', {'failed':failed})
    return render(request, 'admin/upload.html')