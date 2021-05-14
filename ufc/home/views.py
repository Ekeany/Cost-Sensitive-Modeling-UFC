
from django.shortcuts import render
from .models import HomeStat
# Create your views here.

# Home page view with overall stats
def homepage_view(request):
    stats = HomeStat.objects.all()
    return render(request,
                'home.html',
                {'stats': stats})