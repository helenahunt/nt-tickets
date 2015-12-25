# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.core import serializers
import json


from django.views import generic
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render_to_response

from tickets.models import *
from tickets.forms import *

import configuration.customise as config

import datetime
import settings
import mailchimp_util


def login(request, **kwargs):
    if request.user.is_authenticated():
        next = request.REQUEST.get('next', '/')
        return HttpResponseRedirect(request.REQUEST.get('next', '/'))
    else:
        from django.contrib.auth.views import login

        return login(request, authentication_form=forms.LoginForm)


def ShowIndex(request):
    report = dict()
    show = dict()
    show_list = Show.objects.all()

    number = 0

    for sh in show_list:
        if sh.is_current():
            number = number + 1
            report['number'] = number

    report['show'] = show_list
    show = show_list

    context = {
        'show': show,
        'report': report,
    }

    return render_to_response('show_index.html', context, context_instance=RequestContext(request)) 


def ShowReport(request, show_name, occ_id):
    report = dict()
    occurrence_fin = dict()
    show_list = get_object_or_404(Show, id=show_name)
    occurrence = Occurrence.objects.get_available(show=show_name)

    show = show_list

    report['default_time'] = config.DEFAULT_TIME.strftime('%-I:%M %p').lower()
    report['default_time_matinee'] = config.DEFAULT_TIME_MATINEE.strftime('%-I:%M %p').lower()

    report['concession_price'] = config.CONCESSION_PRICE[0]
    report['public_price'] = config.PUBLIC_PRICE[0]
    report['fringe_price'] = config.FRINGE_PRICE[0]
    report['external_price'] = config.EXTERNAL_PRICE[0]
    report['matinee_freshers_price'] = config.MATINEE_FRESHERS_PRICE[0]
    report['matinee_freshers_nnt_price'] = config.MATINEE_FRESHERS_PRICE_NNT[0]

    # If there has been an occurrnece selected
    if occ_id > '0':
        report['have_form'] = True
        occ_fin = Occurrence.objects.get(id=occ_id)

        report['day'] = occ_fin.day_formatted()
        report['time'] = occ_fin.time_formatted()

        report['max'] = occ_fin.maximum_sell

        report['tickets'] = Ticket.objects.filter(occurrence=occ_fin).order_by('person_name')
        report['how_many_reserved'] = occ_fin.tickets_sold()
        report['reserve_percentage'] = (report['how_many_reserved'] / float(occ_fin.maximum_sell)) * 100

        report['category'] = occ_fin.show.category
        report['total_sales'] = occ_fin.total_sales()
    else:
        report['have_form'] = False

    # Testing if the show is current
    if show.is_current():
        report['current'] = True
    else:
        report['current'] = False

    # If the a form has been submitted
    if request.method == 'POST':
        S_form = SaleForm(request.POST)
        R_form = ReserveForm(request.POST)

        if S_form.is_valid():
            s = Sale()
            s.occurrence = occ_fin
            s.ticket = S_form.cleaned_data['ticket']

            s.number_concession = S_form.cleaned_data['number_concession']
            s.number_public = S_form.cleaned_data['number_public']
            s.number_season = S_form.cleaned_data['number_season']
            s.number_fellow = S_form.cleaned_data['number_fellow']
            s.number_external = S_form.cleaned_data['number_external']

            s.number_fringe = S_form.cleaned_data['number_fringe']

            s.number_matinee_freshers = S_form.cleaned_data['number_matinee_freshers']
            s.number_matinee_freshers_nnt = S_form.cleaned_data['number_matinee_freshers_nnt']

            s.price = (
                S_form.cleaned_data['number_concession'] * config.CONCESSION_PRICE[0] +
                S_form.cleaned_data['number_public'] * config.PUBLIC_PRICE[0] +
                S_form.cleaned_data['number_external'] * config.EXTERNAL_PRICE[0] +
                S_form.cleaned_data['number_fringe'] * config.FRINGE_PRICE[0] +
                S_form.cleaned_data['number_matinee_freshers'] * config.MATINEE_FRESHERS_PRICE[0]+
                S_form.cleaned_data['number_matinee_freshers_nnt'] * config.MATINEE_FRESHERS_NNT_PRICE[0]
                )

            s.save()

            report['reservation'] = 'None'

            if occ_id > '0':
                report['sold'] = occ_fin.sales()
                report['how_many_left'] = occ_fin.maximum_sell - occ_fin.tickets_sold() - occ_fin.sales()
                report['sale_percentage'] = (report['sold'] / float(occ_fin.maximum_sell)) * 100
                report['total_sales'] = occ_fin.total_sales()

        elif R_form.is_valid():
            report['reservation'] = R_form.cleaned_data['ticket']
        else:
            pass
    else:
        S_form = SaleForm()
        R_form = ReserveForm()
        report['reservation'] = 'None'

        if occ_id > '0':
            report['sold'] = occ_fin.sales()
            report['how_many_left'] = occ_fin.maximum_sell - occ_fin.tickets_sold() - occ_fin.sales()
            report['sale_percentage'] = (report['sold'] / float(occ_fin.maximum_sell)) * 100
            report['total_sales'] = occ_fin.total_sales()

    context = {
        'report': report,
        'show': show,
        'occurrence': occurrence,
        'S_form': S_form,
        'R_form': R_form,
        'occ_id': occ_id,
        'show_name': show_name,
    }

    return render_to_response('show_report.html', context, context_instance=RequestContext(request))


def SaleReport(request):
    report = dict()
    show = dict()
    show_list = Show.objects.all()
    occurrence = Occurrence.objects.all

    number = 0

    for sh in show_list:
        if sh.is_current():
            number = number + 1
            report['number'] = number

    report['show'] = show_list
    show = show_list

    context = {
        'show': show,
        'occurrence': occurrence,
        'report': report,
    }

    return render_to_response('sale_report.html', context, context_instance=RequestContext(request))


def defaultFNI(request):
    html = "<html><body><h1>nt_tickets</h1><p>Function not implemented.</p></body></html>"
    return HttpResponse(html)


def book_landing(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    if show.is_current() is False:
        return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}))
    step = 1
    total = 2
    message = "Tickets for performances are reserved online and payed for on collection at the box office."
    foh_contact = 'foh@newtheatre.org.uk'

    mailchimp = mailchimp_util.get_mailchimp_api()
    if mailchimp is None:
        mc = False
    else:
        mc = True

    if request.method == 'POST':    # If the form has been submitted...
        form = BookingFormLanding(request.POST, show=show)    # A form bound to the POST data
        if form.is_valid():     # All validation rules pass
            t = Ticket()
            t.person_name = form.cleaned_data['person_name']
            t.email_address = form.cleaned_data['email_address']
            t.show = show
            occ_id = form.cleaned_data['occurrence']
            t.occurrence = Occurrence.objects.get(pk=occ_id)
            if t.occurrence.date < datetime.date.today():
                return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}))
            t.quantity = form.cleaned_data['quantity']
            if t.occurrence.maximum_sell < (t.occurrence.tickets_sold()+t.quantity):
                return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}) + "?err=sold_out")

            t.save()
            request.session["ticket"] = t

            email_html = get_template('email/confirm.html').render(
                Context({
                    'show': show,
                    'ticket': t,
                    'settings': settings,
                    'customise': config,
                }))
            email_subject = 'Tickets reserved for ' + show.name
            email = EmailMessage(
                subject=email_subject,
                body=email_html,
                to=[t.email_address],
                from_email="Box Office <boxoffice@newtheatre.org.uk>"
                )
            email.content_subtype = 'html'
            if settings.ACTUALLY_SEND_MAIL:
                email.send()

            # Do MailChimp subscribe if using and if checked
            if settings.DO_CHIMP:
                if form.cleaned_data['add_to_mailinglist']:
                    email = form.cleaned_data['email_address']
                    fullname = form.cleaned_data['person_name']
                    fullname_s = fullname.split(" ")
                    if len(fullname_s) == 2:
                        first = fullname_s[0]
                        last = fullname_s[1]
                    else:
                        first = fullname
                        last = ""
                    mailchimp_util.subscribe(email, first, last)

            return HttpResponseRedirect(reverse('finish', kwargs={'show_id': show.id}))   # Redirect after POST
    else:
        form = BookingFormLanding(show=show)    # An unbound form

    return render(request, 'book_landing.html', {
        'form': form,
        'show': show,
        'step': step,
        'total': total,
        'message': message,
        'mc': mc,
        'foh_contact': foh_contact,
    })


def how_many_left(request):
    if 'occ' in request.GET:
        occ = get_object_or_404(Occurrence, pk=request.GET['occ'])

        response_data = {}
        response_data['sold_out'] = occ.sold_out()
        left = occ.maximum_sell - occ.tickets_sold()
        if left <= settings.MAX_DISCLOSURE:
            response_data['more_than_max'] = False
            response_data['how_many_left'] = left
        else:
            response_data['more_than_max'] = True
            response_data['how_many_left'] = settings.MAX_DISCLOSURE
        response_data['error'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data = {}
        response_data['error'] = True
        response_data['error_message'] = 'Required parameters not given'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def book_finish(request, show_id):
    show = Show.objects.get(id=show_id)
    ticket = request.session["ticket"]

    return render(request, 'book_finish.html', {
        'show': show,
        'ticket': ticket,
    })


def book_error(request, show_id):
    if 'err' in request.GET:
        err = request.GET['err']
    else:
        err = None
    return render(request, 'book_error.html', {'err': err})


def list(request):
    shows = Show.objects.all()

    return render(request, 'list.html', {
        'shows': shows
    })


class OrderedListView(ListView):

    def get_queryset(self):
        return super(OrderedListView, self).get_queryset().order_by(self.order_by)


class ListShows(OrderedListView):
    model = Show
    template_name = 'list_shows.html'
    context_object_name = 'shows'
    order_by = 'start_date'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ListShows, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

    def get_queryset(self):
        today = datetime.date.today()
        return super(ListShows, self).get_queryset().filter(end_date__gte=today).filter(category__slug__in=settings.PUBLIC_CATEGORIES)


class ListPastShows(OrderedListView):
    model = Show
    template_name = 'list_past_shows.html'
    context_object_name = 'shows'
    order_by = '-start_date'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ListPastShows, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

    def get_queryset(self):
        today = datetime.date.today()
        return super(ListPastShows, self).get_queryset().filter(end_date__lte=today)


class DetailShow(DetailView):
    model = Show
    template_name = 'detail_show.html'
    context_object_name = 'show'


def sidebar(request):
    categories = Category.objects.all().exclude(sort=0).order_by('sort')
    today = datetime.date.today()
    limit = today + config.SIDEBAR_FILTER_PERIOD
    current_shows = []
    for category in categories:
        shows = Show.objects.filter(category=category).filter(end_date__gte=today).order_by('end_date').filter(start_date__lte=limit).filter(category__slug__in=settings.PUBLIC_CATEGORIES)
        if len(shows) > 0:
            current_shows.append(shows[0])
    return render(request, 'sidebar.html', {'shows': current_shows, 'settings': settings})


def cancel(request, ref_id):
    ticket = get_object_or_404(Ticket, unique_code=ref_id)
    if request.POST.get("id", "") == ticket.unique_code:
        ticket.cancelled = True
        ticket.save()
        cancelled = True
        already_cancelled = False
    elif ticket.cancelled is True:
        already_cancelled = True
        cancelled = False
    else:
        cancelled = False
        already_cancelled = False

    context = {
        'ticket': ticket,
        'cancelled': cancelled,
        'already_cancelled': already_cancelled,
    }

    return render(request, 'cancel.html', context)
