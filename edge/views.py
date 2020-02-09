from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from django.conf import settings
import datetime as datetime



from .models import Pitch, Member, Document
from .analysis import security_total_return, year_to_date_return, one_year_risk_adjusted_return


def dashboard(request):
	template_name = 'edge/dashboard.html'
	current_holdings = Pitch.objects.filter(currently_invested=True)
	recent_pitches = Pitch.objects.order_by('-pitch_date')[:6]
	context = {
		'current_holdings': current_holdings,
		'recent_pitches': recent_pitches
	}
	return render(request, template_name, context)

@login_required
def pitches(request):
    template_name = 'edge/pitches.html'
    pitch_list = Pitch.objects.all()
    context = {
    	'pitch_list': pitch_list
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
        'year_to_date_return': year_to_date_return(securities=[pitch.stock_ticker], weights=[1])
    }
    if pitch.investment_entered==True:
        context['one_year_risk_adjusted_return'] = one_year_risk_adjusted_return(threeFactor=False, securities=[pitch.stock_ticker], weights=[1])
        if pitch.currently_invested:
            context['security_total_return'] = security_total_return(securities=[pitch.stock_ticker], entry_price=pitch.entry_price, entry_date=pitch.entry_date, exit_price=None, exit_date=datetime.datetime.today().strftime('%Y-%m-%d'))
        else:
            context['security_total_return'] = 1.0 
    return render(request, template_name, context)

def login(request):
	template_name = 'edge/login.html'
	return render(request, template_name)