from flask import render_template, request, flash, redirect

#La fonction request permet d'afficher les requêtes

#On importe la variable app qui instancie l'application
from djangophoto.app import app, login
#On déclare les tables de la BDD
from djangophoto.modeles.donnees import Image
from djangophoto.modeles.utilisateurs import User
from flask_login import login_user, current_user, logout_user


#On importe flask :
#- render_template permet de relier les templates aux URLS
#- url_for permet de construire les URLS vers les fonctions et les pages HTML
from flask import render_template, url_for
from flask import Flask
#On importe SQLAlchemy ainsi que l'opérateur or_ 
#qui sert dans la fonction de requête pour la recherche plein texte 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_


#On souhaite avoir 5 résultats par page lors de la recherche
RESULTATS_PAR_PAGES = 5

#On définit les différentes routes 
#page d'accueil
@app.route("/")
def accueil():
        return render_template("pages/accueil.html")

#page Galerie
@app.route("/Galerie")
def galerie():
    cheminImages = Image.query.all()
    return render_template("pages/galerie.html", Images=cheminImages)
#Permet de faire apparaitre l'ensemble des images dans la page Galerie

#page de la biographie de Django Reinhardt
@app.route("/Biographie")
def biographie():
		return render_template("pages/biographie.html") 

#page à propos
@app.route("/A_propos")
def a_propos():
		return render_template("pages/a_propos.html")

# Définition de la route vers chaque image grâce à leur identifiant (int)
@app.route("/Imgs/<int:id>")
def img(id):
    unique_img = Image.query.get(id)
    return render_template("pages/imgs.html", img = unique_img, id=id)

#On définit la route pour la recherche plein-texte
@app.route("/recherche")
def recherche():
    motclef = request.args.get("keyword", None)
    page = request.args.get("page",1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1 

#Création d'une liste vide pour les résultats
    resultats = []
    titre = "Recherche"

    if motclef:
    # Si on a un mot-clé, on requête toutes les tables de notre base de données pour vérifier s'il y a des correspondances
    # Le résultat de cette requête est stocké dans la liste resultats = []
        resultats = Image.query.filter(
            or_(
                Image.date.like("%{}%".format(motclef)),
                Image.orientation.like("%{}%".format(motclef)),
                Image.description.like("%{}%".format(motclef)),
                Image.tag.like("%{}%".format(motclef)),
                Image.titre.like("%{}%".format(motclef)),
                Image.nom_photographe.like("%{}%".format(motclef)),
                Image.source.like("%{}%".format(motclef)),
            )
        ).paginate(page=page, per_page=RESULTATS_PAR_PAGES)
        titre = "Résultats pour votre recherche '"+ motclef + "'"
        # On affiche une phrase de titre qui indiquera les résultats de la recherche en fonction du mot-clé rentré par l'utilisateur
        # Cette variable titre sera réutilisée dans la page recherche.html
    return render_template("pages/recherche.html", resultats=resultats, titre=titre, keyword=motclef)
    # On retourne la page recherhce.html, et on indique à quoi correspondent les variables resultats, titre et keyword,
    # qui seront appelées ensuite au sein des pages html

@app.route("/Inscription", methods=["GET", "POST"])
def inscription():
	   
    #Route gérant les inscriptions
    #
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        statut, donnees = User.creer(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")
   

@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    """ Route gérant les connexions
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")
    # Si on est en POST, cela veut dire que le formulaire a été envoyé
    if request.method == "POST":
        utilisateur = User.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("pages/connexion.html")
login.login_view = 'connexion'


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")

#page de l'erreur 404 lorsque la page demandée est introuvable
#template "error/404"
@app.errorhandler(404)
def page_not_found(error):
    return render_template("error/404.html"), 404