from django.shortcuts import render


def index(request):
    return render(request, "index.html")

def propos(request):
    return render(request, "a_propos.html")

def contact(request):
    return render(request, "contact.html")

def connexion(request) :
    return render(request, 'connexion.html')

