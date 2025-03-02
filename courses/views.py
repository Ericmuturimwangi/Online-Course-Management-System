from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, Module, Enrollment, Payment
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
import json
import traceback
from rest_framework.response import Response
from rest_framework import status

# mpesa api
@csrf_exempt
def stk_push(request):

    data = json.loads(request.body)
    
    if request.method == "POST":
        phone_number =data.get("phone_number")

        amount = data.get("amount")
        if not amount:
            return JsonResponse({"error": "Amount is required"}, status=400)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return JsonResponse({"error": "Invalid amount"}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid amount"}, status=400)


        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode((settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()).decode()
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

def mpesa_callback(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"error": "Invalid request method"}, status=400)

        # Parse the callback data
        callback_data = json.loads(request.body)
        # print("M-PESA Callback Data: ", callback_data)

        # Get the ResultCode from the callback
        result_code = callback_data["Body"]["stkCallback"].get("ResultCode", None)
        if result_code is None:
            return JsonResponse({"error": "ResultCode missing from callback"}, status=400)

        if result_code == 0:
            try:
                # Extract the transaction ID if available
                transaction_id = callback_data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
                return JsonResponse({"success": "Payment Success", "transaction_id": transaction_id}, status=200)
            except KeyError:
                return JsonResponse({"error": "Transaction ID not found"}, status=400)
        else:
            return JsonResponse({"error": "Payment Failed"}, status=400)

    except Exception as e:
        error_message = str(e)
        stack_trace = traceback.format_exc()
        print(f"Error: {error_message}")
        print(f"Stack trace: {stack_trace}")
        return JsonResponse({"error": error_message}, status=500)

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

        payment = Payment.objects.filter(user=user, course=course, payment_status='completed').first()

        if not payment:
            return Response({"detail":"Payment for the course is required"}, status= status.HTTP_400_BAD_REQUEST)
        
        enrollment = Enrollment.objects.create(course=course, user=user)
        return Response (EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)
    

# iniating a payment callback
@csrf_exempt
def stk_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if data["Body"]["stkCallback"]["ResultCode"] == 0:  # Success
                payment = Payment.objects.create(
                    phone_number=data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"],
                    amount=data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"],
                    transaction_id=data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"]
                )
                payment.save()
                return JsonResponse({"message": "Payment saved"}, status=201)
            else:
                return JsonResponse({"error": "Payment failed"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)




