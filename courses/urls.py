from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from courses import views
# from courses.views import course_list



router = DefaultRouter()
router.register(r'courses', views.CourseViewset)
router.register(r'modules', views.ModuleViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)


urlpatterns = [
    path('', include (router.urls)),
    path('stk_push/', views.stk_push, name='stk_push'),
    path('mpesa_callback/', views.mpesa_callback, name='mpesa_callback'),


    

]
