from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest

class  NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it(self):
        # User has heard about a new online to-do app. She goes to chekc out homepage
        self.browser.get('http://localhost:8000')

        # User notices page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # User is invited to enter a to-do item straight away
        input_box = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(input_box.get_attribute('placeholder'), 'Enter a to-do item')

        # User types 'Buy peacock feathers' into textbox
        input_box.send_keys('Buy peacock feathers')

        # User hits enter, updating the list, which now says '1: Buy peacock feathers' as an item in list
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn('1: Buy peacock feathers', [row.text for row in rows], f"New to-do item did not appear in table. Contents were: \n{table.text}")

        # There is still a text box inviting user to add another item
        # User enters 'Use peacock feathers to make a fly'
        self.fail('Finish the test.')

if __name__ == '__main__':
    unittest.main(warnings='ignore')
