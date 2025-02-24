from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, Module, Enrollment
from .serializers import CourseSerializer, ModuleSerializer, EnrollmentSerializer
from rest_framework import viewsets

class CourseViewset(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


