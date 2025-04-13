# Projet Django

Ce projet est une application Django. Suivez les instructions ci-dessous pour configurer l'environnement et lancer le serveur de développement.

## Prérequis

- Python 3.9
- Pip

## Installation de l'environnement

1. Clonez ce repository.
   
   ```bash
   git clone <URL_DU_REPOSITORY>
   cd <nom_du_dossier_du_projet>
Installez les dépendances nécessaires :
```bash
pip install -r requirements.txt
```
## Configuration de l'environnement virtuel

Activez l'environnement virtuel :

Sur Mac/Linux :
```bash
source .env/bin/activate
```
## Lancer le serveur de développement local
Accédez au répertoire src :

```bash
cd src
```
Lancez le serveur de développement :

```bash
python manage.py runserver
```
Le serveur démarrera à l'adresse indiquée dans le terminal (par défaut http://127.0.0.1:8000/).

## Première utilisation
Lors de votre première exécution, il est nécessaire d'exécuter les migrations pour configurer la base de données :

```bash
python manage.py migrate
```
Cela mettra en place les tables nécessaires à votre projet.

## Accéder à l'application
Après avoir lancé le serveur, ouvrez votre navigateur et accédez à l'adresse localhost ou celle fournie dans le terminal.
