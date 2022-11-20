from calendar import month
from datetime import datetime, timedelta
from django.shortcuts import render
from GrievanceRedressalSystemApp.models import Grievance
from django.db.models.functions import Trunc
from django.db.models import Count, Q
import json
from django.contrib.auth.decorators import login_required


# Create your views here.


@login_required(login_url='landing')
def Analytics(request, year=datetime.now().year, gType="gtype", category="category"):
    if gType == "gtype" and category == "category":
        GrievanceSet = Grievance.objects.filter(created__year=year)
    else:
        if gType == "student":
            categoryData = [Grievance.objects.filter(grievantType=gType, category=cat).count() for cat in 
                ['academic', 'registration', 'placement', 'general', 'stud2stud']]

            cLabels = ["Teaching-Learning and Evaluation", 
                "Registration, Fees, Results and Transcripts", 
                "Internships and Placement", 
                "General Amenities and Services", 
                "Student to Student Grievances"
            ]
        else:
            categoryData = [Grievance.objects.filter(grievantType=gType, category=cat).count() for cat in 
                ['hra', 'facultyAction', 'staffAction', 'service']]

            cLabels = ["Human Resource and Administration", 
                "Matters related to an Action of any Member of the Faculty", 
                "Matters related to an Action of any Member of the Staff", 
                "Matters related to Service Conditions", 
            ]
        GrievanceSet = Grievance.objects.filter(created__year=year, grievantType=gType, category=category)

    G_month = GrievanceSet.annotate(month=Trunc('created', 'month')).values('level', 'month').annotate(count=Count('grievanceID')) 
    barData = [[0]*12, [0]*12, [0]*12]
    for g in G_month:
        barData[g['level']-1][g['month'].month - 1] = g['count']

    statusData = []
    if GrievanceSet.count():
        statusData = [GrievanceSet.filter(status=s).count() for s in [1, -1, 0]]
    
    if category == "category":
        if GrievanceSet.count():
            categoryData = [GrievanceSet.filter(grievantType=gt).count() for gt in ['student', 'faculty', 'staff']]
            cLabels = ["Student", "Faculty", "Staff"]
        cat = "Grievant Type"
        catsize = "80%"
        catBool = "true"

    if gType != "gtype":
        cat = gType.capitalize() + " Categories"
        catsize = "65%"
        catBool = "false"

    responseG = GrievanceSet.filter(response__isnull=False)
    avgResponseTime = timedelta()
    avgResponseTimeStr = ""
    if responseG:
        for g in responseG:
            avgResponseTime += g.ResponseTime
        avgResponseTime /= responseG.count()
        avgResponseTimeStr = str(avgResponseTime.days) + "d " + str(avgResponseTime.seconds//3600) + "h"

    resolvedG = GrievanceSet.filter(Q(status=-1) | Q(status=1))
    avgResolutionTime = timedelta()
    avgResolutionTimeStr = ""
    if resolvedG:    
        for g in resolvedG:
            avgResolutionTime += g.ResolutionTime
        avgResolutionTime /= resolvedG.count()
        avgResolutionTimeStr = str(avgResolutionTime.days) + "d " + str(avgResolutionTime.seconds//3600) + "h"

    years = [y['year'] for y in Grievance.objects.annotate(year=Trunc('created', 'year')).values('year').distinct('year')]

    cLabels = json.dumps(cLabels)

    if sum(categoryData) == 0:
        categoryData = []

    return render(request, 'analytics.html', {
            'Year':year, 
            'Category':category, 'CLabels':cLabels, 'catDisplay':catBool, 'catSize':catsize,
            'GType':gType, 
            'years':years,
            'Gdata':barData, 
            'Sdata':statusData, 'Cdata': categoryData, 'cat':cat,
            'response':avgResponseTimeStr, 'resolution':avgResolutionTimeStr, 'Gtotal':sum(statusData)
        })