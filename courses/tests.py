from django.test        import TestCase
from django.core        import mail
from django.test.client import Client
from django.urls        import reverse
from .models            import Course
from django.conf        import settings
class ContactCourseTestCase(TestCase):

    def setUp(self):
        self.course = Course.objects.create(name='Django', slug='django')

    def tearDown(self):
        self.course.delete()

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_contact_form_error(self):
        data = {'name':'tamer', 'email':'', 'message':''}
        client = Client()
        path = reverse('courses:details', args = [self.course.slug])
        response = client.post(path, data)
        self.assertFormError(response, 'form', 'email', 'Este campo é obrigatório.')
        self.assertFormError(response, 'form', 'message', 'Este campo é obrigatório.')

    def test_contact_form_success(self):
        data = {'name':'tamer', 'email':'tamer@gmail.com', 'message':'oi'}
        client = Client()
        path = reverse('courses:details', args = [self.course.slug])
        response = client.post(path, data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [settings.CONTACT_EMAIL])
