from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm

def index(request):
    return render(request, "index.html")

def propos(request):
    return render(request, "a_propos.html")

def connexion(request) :
    return render(request, 'connexion.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Envoi de l'email
            send_mail(
                subject=f"Nouveau message de {nom}",
                message=message,
                from_email=email,
                recipient_list=['matheo.arondeau@gmail.com'],  # Change ça pour ton adresse email
            )
            return render(request, "contact.html", {
                'form': ContactForm(), 
                'success': True  # Affichage d'un message de succès
            })
    else:
        form = ContactForm()

    return render(request, "contact.html", {'form': form})
