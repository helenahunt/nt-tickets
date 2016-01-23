from django.test import TestCase
from django.core.files import File
from models import *
from markdown2 import Markdown

from datetime import date, timedelta, datetime



class StaticPageTest(TestCase):

    def test_list_view(self):
        response = self.client.get('/list/')
        self.assertEqual(response.status_code, 200)

    def test_sidebar_view(self):
        response = self.client.get('/sidebar/')
        self.assertEqual(response.status_code, 200)


class BookTest(TestCase):

    def setUp(self):
        cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        start_date = date.today() + timedelta(days=2)
        end_date = date.today() + timedelta(days=5)
        Show.objects.create(
            name='Test Show',
            location='Somewhere',
            description='Some Info',
            long_description='Some more info',
            poster=File(open('test/test_poster.jpg')),
            start_date=start_date,
            end_date=end_date,
            category=cat
            )
    def test_category_name(self):
        cat = Category.objects.get(pk=1).__str__()
        self.assertEqual(cat, 'Test Category')

    def test_show_exists(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.name, 'Test Show')

    def test_book_form(self):
        response = self.client.get('/book/1/')
        self.assertEqual(response.status_code, 200)

    def test_show_sold_out_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.show_sold_out(), False)

    def test_has_occurrences_false(self):
        show = Show.objects.get(pk=1)
        self.assertEqual(show.has_occurrences(), False)


class ShowTest(TestCase):

    def setUp(self):
        cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        today = date.today()
        now = datetime.now()
        loc = 'Location 1'
        desc = 'A show somewhere'
        l_desc = 'A longer show somewhere'
        poster = File(open('test/test_poster.jpg'))

        # Create some good shows
        show = Show.objects.create(name='S1', category=cat, location=loc, description='show current', long_description=l_desc, poster=poster, start_date=today, end_date=today + timedelta(days=6))
        # cls.show{2} = Show.objects.create(name='S2', category=cls.cat, location=cls.loc, description='show past', long_description=cls.l_desc, start_date=cls.today - timedelta(days=6), end_date=cls.today)

        # Create an occurrence 
        occ = Occurrence.objects.create(show=show, date=today, time=datetime.now()+timedelta(hours=3), maximum_sell=2, hours_til_close=2)

        ticket = Ticket.objects.create(
            occurrence=occ,
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            )

        sale = Sale.objects.create(occurrence=occ, ticket='None', price=1, number=2)

    def test_is_current_false(self):
        show = Show.objects.get(name='S1')
        show.end_date = date.today() + timedelta(days=-5)
        self.assertEqual(show.is_current(), False)

    def test_sold_out_true(self):
        show = Show.objects.get(name='S1')
        occ = Occurrence.objects.get(show=show)
        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.now(),
            person_name='testman2',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )

        self.assertTrue(show.show_sold_out())
        self.assertTrue(occ.sold_out())

    def test_sold_out_false(self):
        show = Show.objects.get(name='S1')
        occ = Occurrence.objects.get(show=show)
        self.assertFalse(occ.sold_out())
        self.assertFalse(show.show_sold_out())

    def test_has_occurrences_true(self):
        show = Show.objects.get(name='S1')
        self.assertTrue(show.has_occurrences())

    def test_show_name(self):
        show = Show.objects.get(name='S1')
        self.assertEqual(show.__str__(), show.name)

    def test_markdown(self):
        show = Show.objects.get(name='S1')
        ld_md = '<p>A longer show somewhere</p>\n'
        self.assertEqual(show.long_markdown(), ld_md)

    def test_datetime_formatted(self):
        show = Show.objects.get(name='S1')
        occ = Occurrence.objects.get(show=show)
        day_format = occ.date.strftime('%A')
        time_format = occ.time.strftime('%-I:%M %p').lower()
        datetime_format = occ.date.strftime('%A %d %B ') + \
            occ.time.strftime('%-I%p').lower()

        self.assertEqual(occ.day_formatted(), day_format)
        self.assertEqual(occ.time_formatted(), time_format)
        self.assertEqual(occ.datetime_formatted(), datetime_format)

    def test_occurrence_str(self):
        show = Show.objects.get(name='S1')
        occ = Occurrence.objects.get(show=show)
        occ_str = occ.show.name + \
            " on " + str(occ.day_formatted()) + \
            " at " + str(occ.time_formatted())
        self.assertEqual(occ.__str__(), occ_str)

    def test_ticket_str(self):
        show = Show.objects.get(name='S1')
        occ = Occurrence.objects.get(show=show)
        tick = Ticket.objects.get(occurrence=occ)
        tick_str = tick.occurrence.show.name + \
            " on " + str(tick.occurrence.date) + \
            " at " + str(tick.occurrence.time) + \
            " for " + tick.person_name

        self.assertEqual(tick.__str__(), tick_str)

    def test_get_available(self):
        show = Show.objects.get(name='S1')
        occ = Occurrence.objects.get(show=show)
        datetime_format = datetime_format = occ.date.strftime('%A %d %B ') + \
            occ.time.strftime('%-I%p').lower()

        r1 = Occurrence.objects.get_available(show)

        self.assertEqual(occ.sold_out(), False)    # Sanity Check
        self.assertEqual(r1, [(1, datetime_format)])

    def test_get_available_sold_out(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)
        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.now(),
            person_name='testman2',
            email_address='test@test.com',
            quantity=79,
            cancelled=False,
            unique_code=rand_16(),
            )


        r = Occurrence.objects.get_available(show)

        self.assertEqual(show.show_sold_out(), True)    # Sanity Check
        self.assertEqual(occ.sold_out(), True)

        self.assertEqual(r, [])

    def test_show_sales(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)

        self.assertEqual(show.show_sales(), 1)

class ShowClosed(TestCase):
    def setUp(self):
        cat = Category.objects.create(name='Test Category', slug='test', sort=1)
        start_date = date.today() + timedelta(days=2)
        end_date = date.today() + timedelta(days=5)
        Show.objects.create(
            name='Test Show',
            location='Somewhere',
            description='Some Info',
            long_description='Some more info',
            poster=File(open('test/test_poster.jpg')),
            start_date=start_date,
            end_date=end_date,
            category=cat
            )

        Occurrence.objects.create(
            show=Show.objects.get(pk=1),
            date=date.today(),
            time=datetime.now(),
            maximum_sell=2,
            hours_til_close=2,
            unique_code=rand_16(),
            )

        Ticket.objects.create(
            occurrence=Occurrence.objects.get(pk=1),
            stamp=datetime.now(),
            person_name='testman',
            email_address='test@test.com',
            quantity=1,
            cancelled=False,
            unique_code=rand_16(),
            )

    def test_get_available_show_closed(self):
        show = Show.objects.get(pk=1)
        occ = Occurrence.objects.get(pk=1)

        r = Occurrence.objects.get_available(show)

        self.assertEqual(r, [])
