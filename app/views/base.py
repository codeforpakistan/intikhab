"""
Base views for general functionality like homepage and profile
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import Election, Vote

def index(request):
    """Homepage view showing only active elections"""
    elections = Election.objects.filter(active=True).order_by('-created')
    return render(request, 'app/index.html', {'elections': elections})

@login_required
def profile(request):
    """User profile view showing their voting history"""
    votes = Vote.objects.filter(user=request.user)
    return render(request, 'app/profile.html', {'votes': votes})