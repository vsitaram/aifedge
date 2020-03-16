from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from django.conf import settings
import datetime as datetime
from dateutil.relativedelta import relativedelta



from .models import Pitch, Member, Document
from .analysis import *

def dashboard(request):
    template_name = 'edge/dashboard.html'
    current_holdings = Pitch.objects.filter(currently_invested=True)
    recent_pitches = Pitch.objects.order_by('-pitch_date')[:6]

    entry_and_exit_dates = []
    for pitch in Pitch.objects.filter(investment_entered=True):
        info = {
            'stock_ticker': pitch.stock_ticker,
            'entry_date': pitch.entry_date.strftime('%m-%d-%Y') if pitch.entry_date else "NULL",
            'exit_date': pitch.exit_date.strftime('%m-%d-%Y') if pitch.exit_date else "NULL"
        }
        entry_and_exit_dates.append(info)

    context = {
    	'current_holdings': current_holdings,
    	'recent_pitches': recent_pitches,
        'portfolio_year_to_date_return': portfolio_year_to_date_return(),
        'one_year_risk_adjusted_return_from_NAV': one_year_risk_adjusted_return_from_NAV(threeFactor=True),
        'aif_nav_data_for_template_5D': aif_nav_data_for_template_5D(),
        'aif_index_data_for_template_5D': aif_index_data_for_template_5D(),
        'aif_nav_data_for_template_1M': aif_nav_data_for_template_1M(),
        'aif_index_data_for_template_1M': aif_index_data_for_template_1M(),
        'aif_nav_data_for_template_3M': aif_nav_data_for_template_3M(),
        'aif_index_data_for_template_3M': aif_index_data_for_template_3M(),
        'aif_nav_data_for_template_6M': aif_nav_data_for_template_6M(),
        'aif_index_data_for_template_6M': aif_index_data_for_template_6M(),
        'aif_nav_data_for_template_1Y': aif_nav_data_for_template_1Y(),
        'aif_index_data_for_template_1Y': aif_index_data_for_template_1Y(),
        'aif_nav_data_for_template_5Y': aif_nav_data_for_template_5Y(),
        'aif_index_data_for_template_5Y': aif_index_data_for_template_5Y(),
        'aif_nav_data_for_template_all': aif_nav_data_for_template_all(),
        'aif_index_data_for_template_all': aif_index_data_for_template_all(),
        'entry_and_exit_dates': entry_and_exit_dates

    }
    
    context['portfolio_one_year_return'] = portfolio_one_year_return() #1 year
    return render(request, template_name, context)

@login_required
def pitches(request):
    template_name = 'edge/pitches.html'
    pitch_list = Pitch.objects.all()
    tickers_and_current_prices = {pitch.stock_ticker: get_current_price([pitch.stock_ticker]) for pitch in pitch_list}
    context = {
    	'pitch_list': pitch_list,
        'tickers_and_current_prices': tickers_and_current_prices
    }
    return render(request, template_name, context)

@login_required
def pitch(request, pitch_id):
    template_name = 'edge/pitch.html'
    pitch = get_object_or_404(Pitch, pk=pitch_id)
    documents = pitch.document_set.all()
    context = {
    	'pitch' : pitch,
        'documents': documents,
        'return_since_pitch': security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.pitch_price, entry_date=pitch.pitch_date, exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d')),

    }
    if pitch.investment_entered:
        if pitch.currently_invested:
            context['return_since_investment'] = security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.entry_price, entry_date=pitch.entry_date, exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d'))
            context['year_to_date_return'] = securities_year_to_date_return(securities=[pitch.stock_ticker], weights=[1])
        else:
            context['total_return_over_investment_period'] = security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.entry_price, entry_date=pitch.entry_date, exit_price=pitch.exit_price, exit_date=pitch.exit_date)
            context['return_since_investment'] = security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.entry_price, entry_date=pitch.entry_date, exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d'))
    else:
        context['year_to_date_return'] = securities_year_to_date_return(securities=[pitch.stock_ticker], weights=[1])


    return render(request, template_name, context)

def login(request):
	template_name = 'edge/login.html'
	return render(request, template_name)