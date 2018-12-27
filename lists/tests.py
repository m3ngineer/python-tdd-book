# from django.urls import resolve
from django.test import TestCase
from lists.models import Item, List
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

class ListAndItemModelsTest(TestCase):

    def test_saving_and_retriving_items(self):
        list_ = List()
        list_.save()
        first_item = Item()
        first_item.text = 'The first (ever) item list'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()

        saved_list_ = List.objects.first()
        self.assertEqual(saved_list_, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) item list', f'{first_saved_item}')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)

class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        response = self.client.post('/lists/new',
            data = {'item_text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new',
            data = {'item_text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

class ListViewTest(TestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_all_items(self):
        correct_list = List.objects.create()
        Item.objects.create(text='item 1', list=correct_list)
        Item.objects.create(text='item 2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_passes_corect_list_to_template(self):
        correct_list = List.objects.create()
        other_list = List.objects.create()

        Item.objects.create(text='item 1', list=correct_list)
        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertEqual(response.context['list'], correct_list)

class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.post(f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'})
        self.assertRedirects(response, f'/lists/{correct_list.id}/')
