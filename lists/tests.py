# from django.urls import resolve
from django.test import TestCase
# from django.http import HttpRequest
# from django.template.loader import render_to_string
# from lists.views import home_page


# Create your tests here.
class HomePageTest(TestCase):

    # def test_root_url_resolves_to_home_page(self):
    #     found = resolve('/')
    #     self.assertEqual(found.func, home_page)

    def test_page_returns_correct_html(self):
        # request = HttpRequest()
        # response = home_page(request)
        response = self.client.get('/')
        html = response.content.decode('utf8')
        # expected_html = render_to_string('home.html')

        # self.assertEqual(html, expected_html)
        # self.assertTrue(html.startswith('<html>'))
        # self.assertIn('<title>To-Do lists</title>', html)
        # self.assertTrue(html.strip().endswith('</html>'))
        self.assertTemplateUsed(response, 'home.html')