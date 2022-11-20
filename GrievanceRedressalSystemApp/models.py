
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Grievant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grievantTypeChoices = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    ]
    programChoices = [
        ('UG', 'UG'),
        ('PG', 'PG'),
        ('PHD', 'PHD')
    ]
    uType = models.CharField(max_length=20, choices=grievantTypeChoices)
    program = models.CharField(blank=True, max_length=3, choices=programChoices)
    gender = models.CharField(blank=True, max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    
    def __str__(self):
        return str(self.user)



class Handler(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    grievantTypeChoices = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    ]
    grievantType = models.CharField(max_length=20, choices=grievantTypeChoices)
    categoryChoices = [
        ('Student',(
            ("academic", "Teaching-Learning and Evaluation"),
            ("registration", "Registration, Fees, Results and Transcripts"),
            ("placement", "Internships and Placement"),
            ("general", "General Amenities and Services"),
            ("stud2stud", "Student to Student Grievances"),
            )
        ),
        ('Faculty/Staff', (
            ("hra", "Human Resource and Administration"),
            ("facultyAction", "Matters related to an Action of any Member of the Faculty"),
            ("staffAction", "Matters related to an Action of any Member of the Staff"),
            ("service", "Matters related to Service Conditions"),
            )
        )
    ]
    category = models.CharField(max_length=20, choices=categoryChoices)
    levelChoices = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
    ]
    level = models.IntegerField(choices=levelChoices, default=1)

    def __str__(self):
        return str(self.user)
        


class Grievance(models.Model):
    grievanceID = models.CharField(primary_key=True, max_length=15)
    grievant = models.ForeignKey(Grievant, on_delete=models.CASCADE)
    grievantTypeChoices = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    ]
    grievantType = models.CharField(max_length=20, choices=grievantTypeChoices)
    categoryChoices = [
        ('Student',(
            ("academic", "Teaching-Learning and Evaluation"),
            ("registration", "Registration, Fees, Results and Transcripts"),
            ("placement", "Internships and Placement"),
            ("general", "General Amenities and Services"),
            ("stud2stud", "Student to Student Grievances"),
            )
        ),
        ('Faculty/Staff', (
            ("hra", "Human Resource and Administration"),
            ("facultyAction", "Matters related to an Action of any Member of the Faculty"),
            ("staffAction", "Matters related to an Action of any Member of the Staff"),
            ("service", "Matters related to Service Conditions"),
            )
        )
    ]
    category = models.CharField(max_length=20, choices=categoryChoices)
    levelChoices = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
    ]
    level = models.IntegerField(choices=levelChoices, default=1)
    statusChoices = [
        (0, 'In Progress'),
        (1, 'Solved'),
        (-1, 'Rejected'),
    ]
    status = models.IntegerField(choices=statusChoices, default=0)
    created = models.DateTimeField()
    subject = models.CharField(max_length=256)
    level2 = models.DateTimeField(blank=True, null=True)
    level3 = models.DateTimeField(blank=True, null=True)
    solved = models.DateTimeField(blank=True, null=True)
    rejected = models.DateTimeField(blank=True, null=True)
    response = models.DateTimeField(null=True)
    content = models.TextField()

    def __str__(self):
        return str(self.grievanceID)

    @property
    def ResponseTime(self):
        if self.response:
            return (self.response - self.created)
        else:
            return None
    
    @property
    def ResolutionTime(self):
        if self.solved:
            return (self.solved - self.created)
        elif self.rejected:
            return (self.rejected - self.created)
        else:
            return None



class Update(models.Model):
    updateID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grievanceID = models.ForeignKey(Grievance, on_delete=models.CASCADE)
    level = models.IntegerField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    
    def __str__(self):
        return str(self.updateID)
    