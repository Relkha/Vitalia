from datetime import datetime

from django.shortcuts import render


def index (request):
    date = datetime.today()
    return render(request, "index.html", context={"date": date})

def propos(request):
    return render(request, "a_propos.html")

def contact(request):
    return render(request, "contact.html")