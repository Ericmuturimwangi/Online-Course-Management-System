from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, Module, Enrollment
from .serializers import CourseSerializer, ModuleSerializer, EnrollmentSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import datetime
from .mpesa import get_mpesa_access_token

# mpesa api
@csrf_exempt
def stk_push(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        amount = request.POST.get("amount")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode().decode()
        access_token = get_mpesa_access_token()
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "OCMS",
            "TransactionDesc": "Payment for course"
        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
        )

        return JsonResponse(response.json())
    return JsonResponse({"error": "Invalid request method"}, status=400)



class CoursePagination(PageNumberPagination):
    page_size = 10

class CourseViewset(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by()
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







