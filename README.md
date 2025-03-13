# Streamlit-app

Streamlit-app est un projet de création d'une application qui permet de réaliser des graphiques à partir d'un dataset. Celui-ci peut être soit celui déjà chargé dans l'application, soit un dataset téléchargé par l'utilisateur. 

### Outils utilisés & Protection de l'application
L'application est réalisée à partir du framework streamlit, avec quelques implémentations de code html, javascript et css. Elle est protégée par défaut contre les failles csrf et xss de par l'utilisation de streamlit, et les codes html et javascript y sont directement implémentés. \
Les datasets utilisés sont chacun stocké directement dans un dataframe sans passer par une base de données. 

### Description & Premiers rendus visuels
L'application est séparée en deux partie : 
 - une partie centrale qui permet d'afficher les graphiques, de télécharger et supprimer un dataset, et d'avoir un aperçu du dataframe
 - une partie secondaire qui permet de gérer tout ce qui est relatif aux graphiques. \
<img src="https://github.com/Nao975/Streamlit-app/blob/main/images/0-%20Rendu%20g%C3%A9n%C3%A9ral%20application.jpg?raw=true" width=50% height=50%><img src="https://github.com/Nao975/Streamlit-app/blob/main/images/4-%20S%C3%A9lection%20de%20colonne%20et%20graphique.jpg?raw=true" width=50% height=50%>

La réalisation du graphique commence avec la sélection des colonnes du dataset qui intéressent l'utilisateur. Ce choix débloque ensuite la sélection du graphique à réaliser selon les types de colonnes sélectionnées (numérique, catégoriel, ou les deux).

L'utilisateur a la possibilité de modifier les colonnes utilisées comme axes x et y, ainsi que d'ajouter ou non un tri par groupe via une colonne catégorielle. Des options supplémentaires permettent de modifier le titre du graphique et les noms des axes x et y. \
<img src="https://github.com/Nao975/Streamlit-app/blob/main/images/5-%20Tri%20par%20groupe.jpg?raw=true" width=50% height=50%><img src="https://github.com/Nao975/Streamlit-app/blob/main/images/6-%20Modification%20de%20la%20l%C3%A9gende.jpg?raw=true" width=50% height=50%>

### Rendus visuels complémentaires
#### Téléchargement et suppression de dataset 
<img src="https://github.com/Nao975/Streamlit-app/blob/main/images/1-%20T%C3%A9l%C3%A9chargement%20d'un%20dataset.png?raw=true" width=50% height=50%><img src="https://github.com/Nao975/Streamlit-app/blob/main/images/2-%20Suppression%20d'un%20dataset.png?raw=true" width=40% height=40%>

#### Aperçu du dataframe 
<img src="https://github.com/Nao975/Streamlit-app/blob/main/images/3-%20Aper%C3%A7u%20du%20dataframe.png?raw=true" width=50% height=50%>
