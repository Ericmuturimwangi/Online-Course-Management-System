from django.test import TestCase, Client
from courses.models import Course
from django.urls import reverse
from django.contrib.auth.models import User
class CourseModelTest(TestCase):

    def setUp(self):
        """Create a sample user and course for testing"""
        # Create a User instance
        self.user = User.objects.create_user(username='admin', password='adminpassword')

        # Create a course with the User instance as the instructor
        self.course = Course.objects.create(
            title="Python Basics",  # Use 'title' field
            description="Learn Python from scratch",  # Use 'description' field
            instructor=self.user  # Use the User instance for instructor
        )

    def test_course_creation(self):
        """Test if the course is created correctly"""
        self.assertEqual(self.course.title, "Python Basics")  # Assert on 'title'
        self.assertEqual(self.course.description, "Learn Python from scratch")  # Assert on 'description'
        self.assertEqual(self.course.instructor.username, "admin")  # Assert on 'instructor' (User instance)

    def test_course_str_method(self):
        """Test the __str__ method of the Course model"""
        self.assertEqual(str(self.course), "Python Basics") 


class CourseViewSet(TestCase):
    
    def setUp(self):
        """Set up initial data for testing"""
        self.client = Client()

        # Create a user instance as the instructor
        self.user = User.objects.create_user(username="admin", password="adminpassword")

        # Create a course with the created user as instructor
        self.course = Course.objects.create(
            title="Python Basics", 
            description="Learn python from scratch", 
            instructor=self.user
        )

    def test_course_list_view(self):
        """Test if the course list view displays the course correctly"""
        # Use the reverse function to get the URL for the course list view
        response = self.client.get(reverse("course-list"))

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the course title is in the response
        self.assertContains(response, "Python Basics")



