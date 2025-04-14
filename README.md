# Projet Django

Ce projet est une application Django. Suivez les instructions ci-dessous pour configurer l'environnement et lancer le serveur de développement.

## Prérequis

- Python 3.9 : 
Pour installer python 3.9 : 
```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9 python3.9-venv python3.9-dev
```
Pour verifier l'instalation :
```bash
python3.9 --version
```
- Pip

## Installation de l'environnement

1. Clonez ce repository.
   
   ```bash
   git clone <URL_DU_REPOSITORY>
   cd <nom_du_dossier_du_projet>

2. installer l'environnement virtuel :
```bash
python 3.9 -m venv .env
```
## Configuration de l'environnement virtuel
Activez l'environnement virtuel :

Sur Mac/Linux :
```bash
source .env/bin/activate
```
Installez les dépendances nécessaires :
```bash
pip install -r requirements.txt
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


## Branche et commit pour GitHub

Créer une nouvelle branche à votre nom, autre que la branche "master" (et penser à désactiver l'environnement avec la cmde ci-dessous)

1. (première fois) -> pour commit la branche sur GitHub depuis votre IDE

```bash
git branch
```

Vous allez voir un * devant votre nouvelle branche, genre :

* ma-nouvelle-branche

2. Pousse ta branche vers GitHub :

```bash
git push -u origin ma-nouvelle-branche
```


Pour faire un nouveau commit (depuis votre IDE)

```bash
git add .
```

puis

```bash
git commit  -m "le commentaire"
```

Pour obtenir le dernier commit (depuis votre IDE)

```bash
git pull
```

## Accéder à l'application
Après avoir lancé le serveur, ouvrez votre navigateur et accédez à l'adresse localhost ou celle fournie dans le terminal.

## Désactiver l'environnement

Pour désactiver l'environnement depuis le clavier : ctrl+c

