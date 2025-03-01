from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    
    if "Body" in data and "stkCallback" in data["Body"]:
        result_code = data["Body"]["stkCallback"]["ResultCode"]

        if result_code == 0:
            return JsonResponse({"message": "success"})
        
    return JsonResponse({"error": "Invalid request"}, status=400)

