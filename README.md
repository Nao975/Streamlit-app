# Streamlit-app

Streamlit-app est un projet de création d'une application qui permet de réaliser des graphiques à partir d'un dataset. Celui-ci peut être soit celui déjà chargé dans l'application, soit un dataset téléchargé par l'utilisateur. 

### Outils utilisés & Protection de l'application
L'application est réalisée à partir du framework streamlit, avec quelques implémentations de code html, javascript et css. Elle est protégée par défaut contre les failles csrf et xss de par l'utilisation de streamlit, et les codes html et javascript y sont directement implémentés. \
Les datasets utilisés sont chacun stocké directement dans un dataframe sans passer par une base de données. 

### Description & Rendu visuel
L'application est séparée en deux partie : 
 - une partie centrale qui permet d'afficher les graphiques, de télécharger et supprimer un dataset, et d'avoir un aperçu du dataframe
 - une partie secondaire qui permet de gérer tout ce qui est relatif aux graphiques. \
#mettre une première image globale / ajout-suppression dataset / affichage dataset \

La réalisation du graphique commence avec la sélection des colonnes du dataset qui intéressent l'utilisateur. Ce choix débloque ensuite la sélection du graphique à réaliser selon les types de colonnes sélectionnées (numérique, catégoriel, ou les deux). \

L'utilisateur a la possibilité de modifier les colonnes utilisées comme axes x et y, ainsi que d'ajouter ou non un tri par groupe via une colonne catégorielle. Des options supplémentaires permettent de modifier le titre du graphique et les noms des axes x et y. \
#mettre une image des options de graphique / ajout-suppression tri par groupe / légende

