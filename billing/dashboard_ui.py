from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def billing_dashboard(request):
    return render(request, "billing/dashboard.html")
