from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, Module, Enrollment
from .serializers import CourseSerializer, ModuleSerializer, EnrollmentSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

class CoursePagination(PageNumberPagination):
    page_size = 10

class CourseViewset(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CoursePagination


    @action(detail=True, methods=['get'])
    def modules(self, request, pk=None):
        course = self.get_object()
        modules = Module.objects.filter(course=course)
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)    



class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


    @action(detail=True, methods=['post'])
    def enroll_in_course(self, request, pk=None):
        course = self.get_object()
        user = request.user

        # check if student is enrolled
        if Enrollment.objects.filter(course=course, user=user).exists():
            return Response ({"detail": "User is already enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment = Enrollment.objects.create(course=course, user=user)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)






