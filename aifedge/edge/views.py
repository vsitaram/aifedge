from django.shortcuts import get_object_or_404, render

from .models import Pitch, Member


def dashboard(request):
	template_name = 'edge/dashboard.html'
	current_holdings = Pitch.objects.all()
	current_holdings = Pitch.objects.filter(currently_invested=True)
	recent_pitches = Pitch.objects.order_by('-pitch_date')[:6]
	context = {
		'current_holdings': current_holdings,
		'recent_pitches': recent_pitches
	}
	return render(request, template_name, context)

def pitches(request):
    template_name = 'edge/pitches.html'
    pitch_list = Pitch.objects.all()
    context = {
    	'pitch_list': pitch_list
    }
    return render(request, template_name, context)


def pitch(request, pitch_id):
    template_name = 'edge/pitch.html'
    pitch = get_object_or_404(Pitch, pk=pitch_id)
    context = {
    	'pitch' : pitch
    }
    return render(request, template_name, context)

