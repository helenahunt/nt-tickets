from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
import time
import factory
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.core.files import File
from tickets import models
from pricing import models

from django.test.utils import override_settings
from django.conf import settings

import datetime
import os

def UserFactory():
  User.objects.create_user(
    username='Jim', 
    email='jim@rash.com', 
    password = 'correcthorsebatterystaple',

    is_superuser = True
  )

class CategoryFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Category

  name = 'In House'
  slug = 'in_house'
  sort = 1

class ShowFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Show

  category = factory.SubFactory(CategoryFactory)
  start_date = datetime.date.today() + datetime.timedelta(days=2)
  end_date = datetime.date.today() + datetime.timedelta(days=5)

  name='Test Show'
  location='Somewhere'
  description='Test show present'
  long_description='Some more info'
  # poster=File(open('test/test_poster.jpg'))



class OccurrenceFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Occurrence

  show = factory.SubFactory(ShowFactory)
  date = datetime.date.today() + datetime.timedelta(days=2)
  time=datetime.datetime.now()
  maximum_sell=2
  hours_til_close=2



class BookTest(LiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')

    OccurrenceFactory.create()

  def tearDown(self):
    self.browser.quit()

  def test_book_show_quick(self):
    browser = self.browser
    
    show_id = models.Show.objects.get(name='Test Show').id

    browser.get(self.live_server_url + '/book/' + str(show_id))

    # Check the title is correct
    title_text = browser.find_element_by_xpath(
      '//p[1]'
      ).text
    self.assertIn(
      title_text,
      'You\'re booking tickets for Test Show at Somewhere.'
      )

    # Input correct details
    occurrence = Select(browser.find_element_by_id('id_occurrence'))
    occurrence.select_by_value(str(show_id))
    quantity = Select(browser.find_element_by_id('id_quantity'))
    quantity.select_by_value('1')
    name = browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    browser.find_element_by_id('submit-btn').click()
    # Wait a little for the page to load
    browser.implicitly_wait(10)
    thanks_title = browser.find_element_by_xpath('//div[@class="main"]/h1').text
    self.assertEqual(thanks_title, 'Thanks!') 
    self.assertEqual(
      self.live_server_url + '/book/' + str(show_id) + '/thanks/',
      browser.current_url
      )

    # Navigate back to booking
    browser.get(self.live_server_url + '/book/' + str(show_id))

    # Submit another form with the same details
    occurrence = Select(browser.find_element_by_id('id_occurrence'))
    occurrence.select_by_value(str(show_id))
    quantity = Select(browser.find_element_by_id('id_quantity'))
    quantity.select_by_value('1')
    name = browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    browser.find_element_by_id('submit-btn').click()
    # Wait for the page to load
    browser.implicitly_wait(10)
    error_title = browser.find_element_by_xpath('//div[@class="main"]/h1').text
    # Should get an error
    self.assertEqual(error_title, 'Error')

    # Wait to be allowed to book tickets again
    time.sleep(6)
    # Navigate to the boking page
    browser.get(self.live_server_url + '/book/' + str(show_id))

    # Submit another form with the same details
    occurrence = Select(browser.find_element_by_id('id_occurrence'))
    occurrence.select_by_value(str(show_id))
    quantity = Select(browser.find_element_by_id('id_quantity'))
    quantity.select_by_value('1')
    name = browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    browser.find_element_by_id('submit-btn').click()
    # Wait for the page to load
    browser.implicitly_wait(10)

    # Make sure we are allowed to book tickets
    thanks_title = browser.find_element_by_xpath('//div[@class="main"]/h1').text
    self.assertEqual(thanks_title, 'Thanks!') 
    self.assertEqual(
      self.live_server_url + '/book/' + str(show_id) + '/thanks/',
      browser.current_url
      )


  def test_book_show_no_date(self):
    browser = self.browser
    show_id = models.Show.objects.get(name='Test Show').id
    browser.get(self.live_server_url + '/book/' + str(show_id))

    # Input correct details but no date or seats
    name = browser.find_element_by_id('id_person_name')
    name.send_keys('Test Name1')
    email = browser.find_element_by_id('id_email_address')
    email.send_keys('test@test.com')

    # Submit the form
    browser.find_element_by_id('submit-btn').click()
    # Wait a little bit
    # self.browser.implicitly_wait(10)
    occurrence_err = browser.find_element_by_xpath(
      '//form[@class="submit-once"]/div[@class="col col_left"]/div[@class="control-group error required"][1]/div[@class="controls"]/p[@class="help-block"]'
      ).text
    self.assertEqual(occurrence_err, 'This field is required.')


class ListTest(LiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')

    OccurrenceFactory.create()

  def tearDown(self):
    self.browser.quit()

  def test_list_view(self):
    browser = self.browser

    browser.get(self.live_server_url + '/list')

    # Check that we have a title
    browser.implicitly_wait(3)
    title_text = browser.find_element_by_id('show-title').text
    self.assertEqual(title_text, 'Test Show')


class AuthTest(StaticLiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')
    self.browser.set_window_size(1200, 1000)
    self.browser.implicitly_wait(5)
    UserFactory()

  def tearDown(self):
    self.browser.quit()

  def test_login_correct(self):
    self.browser.get(self.live_server_url + '/')

    # Test that we've actually got a login page
    self.assertIn('login', self.browser.current_url)

    username = self.browser.find_element_by_id('username')
    username.send_keys('Jim')
    password = self.browser.find_element_by_id('password')
    # Send the wrong password
    password.send_keys('correcthorsebatterystapleerror')

    # Submit the form

    submit = self.browser.find_element_by_id('submit')
    submit.click()

    error_text = self.browser.find_element_by_xpath('//p[@class="red-text"]').text
    # Make sure we got an error
    self.assertIn('incorrect', error_text)

    # Test that we're still on the login page
    self.assertIn('login', self.browser.current_url)

    username = self.browser.find_element_by_id('username')
    username.send_keys('Jim')
    password = self.browser.find_element_by_id('password')
    # Send the correct password
    password.send_keys('correcthorsebatterystaple')

    # Submit the form
    submit = self.browser.find_element_by_id('submit')
    submit.click()

    nav_text = self.browser.find_element_by_xpath('//a[@class="dropdown-button"]').text
    # Check the username is in the nav
    self.assertIn('Jim', nav_text)

    # Test login page with authenticated user
    self.browser.get(self.live_server_url + '/login/')

    nav_text = self.browser.find_element_by_xpath('//a[@class="dropdown-button"]').text
    # Check the username is in the nav
    self.assertIn('Jim', nav_text)

    # Test login page with a page request with authenticated user
    self.browser.get(self.live_server_url + '/login/?Pnext=/')
    
    nav_text = self.browser.find_element_by_xpath('//a[@class="dropdown-button"]').text
    # Check the username is in the nav
    self.assertIn('Jim', nav_text)

    # test that we can logout as well
    self.browser.get(self.live_server_url + '/login/')
    drop = self.browser.find_element_by_xpath('//a[@class="dropdown-button"]')
    logout = self.browser.find_element_by_xpath('//ul[@id="dropdown1"]/li[3]/a')

    action_chains = ActionChains(self.browser)
    action_chains.click(on_element=drop)
    action_chains.click(on_element=logout)
    action_chains.perform()

    logout = self.browser.find_element_by_xpath('//h4[@class="light nnt-orange medium-text"]').text
    self.assertEqual(logout, 'Logged Out')


class IndexTest(StaticLiveServerTestCase):

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')
    # Force desktop sizing
    self.browser.set_window_size(1200, 1000)

    UserFactory()
    OccurrenceFactory.create()

  def tearDown(self):
    self.browser.quit()

  def test_index(self):
    browser = self.browser
    browser.get(self.live_server_url + '/')

    # Login
    username = browser.find_element_by_id('username')
    username.send_keys('Jim')
    password = browser.find_element_by_id('password')
    # Send the wrong password
    password.send_keys('correcthorsebatterystaple')

    # Submit the form
    submit = browser.find_element_by_id('submit')
    submit.click()

    title = browser.find_element_by_id('title').text
    self.assertEqual(title, 'Test Show')

    browser.get(self.live_server_url + '/?page=10')

    page = browser.find_element_by_id('page').text
    self.assertIn('1', page)


class ReportTest(StaticLiveServerTestCase):
  fixtures = ['initial_pricing.json']

  def setUp(self):
    self.browser = webdriver.Chrome('bin/chromedriver')
    # Force desktop sizing
    self.browser.set_window_size(1200, 1000)

    self.browser.implicitly_wait(10)

    UserFactory()
    OccurrenceFactory.create(maximum_sell=80)

  def tearDown(self):
    self.browser.quit()

  @override_settings(DEBUG=True)
  def test_report(self):
    show_id = models.Show.objects.get(name='Test Show').id

    self.browser.get(self.live_server_url + '/')

    # Login
    username = self.browser.find_element_by_id('username')
    username.send_keys('Jim')
    password = self.browser.find_element_by_id('password')
    # Send the wrong password
    password.send_keys('correcthorsebatterystaple')

    # Submit the form
    submit = self.browser.find_element_by_id('submit')
    submit.click()

    # Navigate to the sale page
    img = self.browser.find_element_by_xpath('//div[@class="card small grey darken-3"][1]//img[@id="report-image"]')
    img.click()

    # Get the choose showing modal
    showing = self.browser.find_element_by_xpath('//div[@class="col s6 center-align"][1]/button')
    showing.click()

    wait = WebDriverWait(self.browser, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID,'picker-modal')))

    modal = self.browser.find_element_by_id('picker-modal')
    self.assertTrue(modal.is_displayed())

    occ = self.browser.find_element_by_id('showing')
    occ.click()

    free_text = self.browser.find_element_by_xpath('//div[@id="sale-update"]//p').text
    self.assertIn('No tickets sold', free_text)
    self.assertIn('No tickets reserved', free_text)
    self.assertIn('80 tickets free', free_text)

    # Check selling tickets adds up properly
    pricing = models.InHousePricing.objects.get(id=1)
    member_price = pricing.member_price
    concession_price = pricing.concession_price
    public_price = pricing.public_price
    mat_f_price = pricing.matinee_freshers_price
    mat_f_nnt_price = pricing.matinee_freshers_nnt_price

    out = self.browser.find_element_by_id('out1').text

    member = self.browser.find_element_by_id('member')
    action = ActionChains(self.browser)
    action.click(on_element=member)
    action.send_keys('1')
    action.key_down(Keys.CONTROL)
    action.key_up(Keys.CONTROL)
    action.perform()
    # member.click()
    # member.send_keys('1')
    # member.send_keys('tab')
