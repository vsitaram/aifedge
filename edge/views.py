from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from django.conf import settings
import datetime as datetime
from dateutil.relativedelta import relativedelta

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

import json

from .models import Pitch, Member, Document, Tool
from .analysis import *

data = Data()

def dashboard(request):
    template_name = 'edge/dashboard.html'
    current_holdings = Pitch.objects.filter(currently_invested=True)
    recent_pitches = Pitch.objects.order_by('-pitch_date')[:6]
    risk_adj_return = '{:.1%}'.format(data.one_year_risk_adjusted_return_from_NAV(threeFactor=True)["Coef."]["const"])
    context = {
    	'current_holdings': current_holdings,
    	'recent_pitches': recent_pitches,
        'dashboard_as_of': data.dashboard_as_of(),
        'portfolio_year_to_date_return': data.portfolio_year_to_date_return(),
        'one_year_risk_adjusted_return_from_NAV': risk_adj_return
    }
    
    context['portfolio_one_year_return'] = data.portfolio_one_year_return()
    return render(request, template_name, context)

@api_view(['GET'])
def dashboard_graph_data(request, time_horizon):
    param_dict = {
        "5D": {"days": 5},
        "1M": {"months": 1},
        "3M": {"months": 3},
        "6M": {"months": 6},
        "1Y": {"years": 1},
        "5Y": {"years": 5},
        "ALL": None
    }

    if request.method == 'GET':
        return Response(data.aif_nav_data_for_template(param_dict[time_horizon]))

@login_required
def pitches(request):
    template_name = 'edge/pitches.html'
    pitch_list = Pitch.objects.all()
    tickers_and_current_prices = {pitch.stock_ticker: data.get_current_price([pitch.stock_ticker]) for pitch in pitch_list}
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
        'pitch_as_of': data.pitch_as_of(),
        'return_since_pitch': data.security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.pitch_price, entry_date=pitch.pitch_date, exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d')),

    }
    if pitch.investment_entered:
        if pitch.currently_invested:
            context['return_since_investment'] = data.security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.entry_price, entry_date=pitch.entry_date, exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d'))
            context['year_to_date_return'] = data.securities_year_to_date_return(securities=[pitch.stock_ticker], weights=[1])
        else:
            context['total_return_over_investment_period'] = data.security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.entry_price, entry_date=pitch.entry_date, exit_price=pitch.exit_price, exit_date=pitch.exit_date)
            context['return_since_investment'] = data.security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.entry_price, entry_date=pitch.entry_date, exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d'))
    else:
        context['year_to_date_return'] = data.securities_year_to_date_return(securities=[pitch.stock_ticker], weights=[1])


    return render(request, template_name, context)

@login_required
def tools(request):
    template_name = 'edge/tools.html'
    tool_list = Tool.objects.all()
    context = {
        'tool_list': tool_list
    }

    return render(request, template_name, context)

@login_required
def tool(request, tool_id):
    tool = get_object_or_404(Tool, pk=tool_id)
    template_name = 'edge/' + tool.template_name
    context = {
        'tool': tool
    }

    return render(request, template_name, context)


@api_view(['GET'])
def one_year_risk_adjusted_return_custom_portfolio(request, three_factor):

    if request.method == 'GET':
        query_params = request.query_params["data"]
        json_query_params = json.loads(query_params)
        three_factor_param = three_factor == "3F"
        securities_param = list(json_query_params.keys())
        weights_param = list(json_query_params.values())
        return Response(data.one_year_risk_adjusted_return_from_securities(three_factor_param, securities_param, weights_param))

@api_view(['GET'])
def one_year_risk_adjusted_return_from_nav(request, three_factor):

    if request.method == 'GET':
        three_factor_param = three_factor == "3F"
        return Response(data.one_year_risk_adjusted_return_from_NAV(three_factor_param))
        
        

def login(request):
	template_name = 'edge/login.html'
	return render(request, template_name)