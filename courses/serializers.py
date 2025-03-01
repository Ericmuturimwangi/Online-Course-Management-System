from .models import Course, Module, Enrollment
from rest_framework import serializers

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields =['id', 'title', 'description', 'instructor']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model= Module
        fields = ['id', 'content', 'course']

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields =['id', 'course', 'student']

