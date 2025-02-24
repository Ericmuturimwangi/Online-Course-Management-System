from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title
    
class Enrollemnt(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together =('course', 'student')

        

