from django.urls import path, include
from rest_framework.routers import DefaultRouter
from courses import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewset)
router.register(r'models', views.ModuleViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)


urlpatterns = [
    path('api/', include ('router.urls')),

]
