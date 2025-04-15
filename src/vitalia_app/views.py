from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm
from .models import MessageContact


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
            objet = form.cleaned_data['objet']
            message = form.cleaned_data['message']

            # Enregistrement dans la bdd
            MessageContact.objects.create(
                nom=nom,
                email=email,
                objet=objet,
                message=message
            )

            # Envoi du mail
            full_message = f"Objet : {objet}\n\nMessage : {message}"
            send_mail(
                subject=f"Nouveau message de {nom} - {objet}",
                message=full_message,
                from_email=email,
                recipient_list=['matheo.arondeau@gmail.com'], # Pour recevoir les mails résultant du formulaire de contact, mettez votre adresse mail
            )

            return render(request, "contact.html", {
                'form': ContactForm(),
                'success': True
            })
    else:
        form = ContactForm()

    return render(request, "contact.html", {'form': form})

# @login_required
def message_admin(request):
    messages = MessageContact.objects.order_by('date_envoi')
    return render(request, 'vitalia_app/message_admin.html', {'messages': messages})

@csrf_exempt  # uniquement tester
#@login_required
def repondre_message(request, message_id):
    if request.method == 'POST':
        reponse = request.POST.get('reponse')
        message = MessageContact.objects.get(id=message_id)
        
        send_mail(
            subject=f"Réponse à votre message : {message.objet}",
            message=reponse,
            from_email='8a86bc001@smtp-brevo.com',
            recipient_list=[message.email],
        )
        return redirect('/messages/')
