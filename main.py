import streamlit as st
from streamlit import session_state as ss
from streamlit.components.v1 import html
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random, string, threading, time
from wordcloud import WordCloud
import squarify



#Chargement du code css de l'appplication
css = """
<style>
    [data-autofocus-inside='true'] > [data-baseweb='popover'] {
        width: 450px;
    }

    [data-testid='stPopoverButton'] .st-emotion-cache-18qnc74 {
        display: none;
    }

    [data-autofocus-inside='true'] [data-baseweb='popover'] [data-testid='stTextInput'] {
        width: 400px;
    }

    [data-testid='stFileUploader'] {
        width: 400px;
    }

    [data-testid='stFileUploader'] section {
        padding: 5px;
    }

    [data-baseweb='tag'] {
        border-bottom-left-radius: 0.45rem;
        border-bottom-right-radius: 0.45rem;
        border-top-right-radius: 0.45rem;
        border-top-left-radius: 0.45rem;
    }
    
    [data-testid='stBaseButton-secondary'] {
        border-bottom-left-radius: 0.8rem;
        border-bottom-right-radius: 0.8rem;
        border-top-right-radius: 0.8rem;
        border-top-left-radius: 0.8rem;
    }

    [data-testid='stVerticalBlockBorderWrapper'] [data-testid='stHorizontalBlock'] {
        gap: 0.5rem;
    }

    [data-baseweb='button-group'] {
        display: flex;
        gap: 0.25rem;
    }
    
    [data-testid='stButtonGroup'] {
        display: flex;
        flex-direction: row-reverse;
        float: left;
    }

    [data-testid='stExpander'] [data-testid='stVerticalBlock'] {
        gap: 0.4rem;
    }

    [data-testid='stTabs'] [data-testid='stVerticalBlock'] {
        gap: 0.25rem;
    }

    [data-testid='stExpander'] [data-testid='stTextInputRootElement'] {
        height: 2.3rem;
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)



#Définition des variables de la session state
#Biliothèque de tous les datasets
if 'datasets_available' not in ss:
    ss['datasets_available'] = {'steam': pd.read_json('steam.json')}

#Partie Téléchargement de dataset
#Variables utilisées pour limiter le nombre de téléchargement de dataset
if 'json_error' not in ss:
    ss['json_error'] = None
if 'title_disabled' not in ss:
    ss['title_disabled'] = False
if 'uploader_disabled' not in ss:
    ss['uploader_disabled'] = False
if 'form_submit_disabled' not in ss:
    ss['form_submit_disabled'] = False
if 'upload_count' not in ss:
    ss['upload_count'] = 0

#Partie Sélection du dataset à utiliser
#Liste déroulante des options possibles
if 'selectbox_options' not in ss:
    ss['selectbox_options'] = ss['datasets_available'].keys()

#Partie Aperçu du dataset 
#Dataframe à afficher selon le dataset choisi
if 'dataframe_displayed' not in ss:
    ss['dataframe_displayed'] = ss['datasets_available']['steam']

#Partie Réalisation des graphiques
#Multi-liste des différentes colonnes du dataset
if 'multiselect_options' not in ss:
    ss['multiselect_options'] = ss['datasets_available']['steam'].columns

#Boutons pour choisir quel graphique réaliser
 #clés des boutons
graphs_propositions = {'distribution': 'dis', 'evolution': 'evo', 'correlation_scatter': 'corr1', 'correlation_bubble': 'corr2',
                       'hierarchy': 'hier', 'composition': 'comp'}
 #désactivation des boutons
graphs_enabled = {'distribution': True, 'evolution': True, 'correlation_scatter': True, 'correlation_bubble': True, 
                  'hierarchy': True, 'composition': True} 
 #désélection des bouton
graphs_default_value = {'distribution': None, 'evolution': None, 'correlation_scatter': None, 'correlation_bubble': None,
                        'hierarchy': None, 'composition': None}
 #mise dans la session state
if 'graphs' not in ss:
    ss['graphs'] = graphs_propositions
if 'disabled' not in ss:
    ss['disabled'] = graphs_enabled
if 'default' not in ss:
    ss['default'] = graphs_default_value

#Variable pour indiquer quel graphique réaliser
if 'graph_to_plot' not in ss:
    ss['graph_to_plot'] = None



#Fonction : générer une clé de widget aléatoire
def generate_random_key(length=10):
    letters_n_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_n_digits) for i in range(length))

#Partie Téléchargement de dataset
#Fonction : envoie un message d'erreur si le fichier json n'est pas lu par pandas
@st.dialog('Erreur')
def error_message(message):
    st.write(message)

    if st.button('Confirmer'):
        st.rerun()
 
#Fonction : vérifier le formulaire (js) et soumettre les données 
@st.fragment
def submit_form():
    #envoie du formulaire
    form_button = st.form_submit_button("Valider", disabled=ss['form_submit_disabled'])

    #vérification et indication des erreurs avec javascript
    html_to_execute = f"""
    <head>
        <style>
            body {{
                margin: 0px;
            }}
            .message_window {{
                margin: 0px;
                padding: 7px;
                display: none;
            }}
            .display-error {{
                background-color: #fde8ec;
                color: #af4242;
                display: block;
            }}
            .display-success {{
                background-color: #d2ffd2;
                color: green;
                display: block;
            }}

        </style>
    </head>
    <body>
        <p class="message_window"></p>
    </body>
    <script>

        let fileTitle = '{ss['file_title']}'; //mettre une fonction pour échapper les guillemets solo ' mis en début/fin, dire que nom changé
        let uploadedFile = "{None if ss['uploaded_file']==None else 'File'}";
        let specialChars = {['\\','/',':','*','?','"','<','>','|']};
        let titlesUsed = {list(ss['datasets_available'].keys())};
        let submitSuccess = false;
        let errorCleared = false;

        
        function clearError(){{
            document.querySelector(".message_window").classList.remove("display-error");
        }}

        function showError(errorMessage){{
            document.querySelector(".message_window").classList.add("display-error");
            document.querySelector(".message_window").innerHTML = errorMessage;
        }}


        clearError();
        
        if (uploadedFile === "None" && fileTitle === ""){{
            showError("Veuillez sélectionner un fichier et entrer un nom.");
        }} else if (uploadedFile === "None"){{
            showError("Vous n'avez pas sélectionné de fichier à télécharger.");
        }} else if (fileTitle === ""){{
            showError("Vous n'avez pas entré de nom pour le dataset.");
        }} else if (specialChars.some(character => fileTitle.includes(character))){{
            showError("Caractères désactivés : " + String(specialChars).replace(/[ \[\]\'\, ]/g, "") + ". Veuillez recommencer.");
        }} else if (titlesUsed.includes(fileTitle)){{
            showError("Nom déjà utilisé par un dataset. Choisissez un autre nom.");
        }} else {{
            submitSuccess = true;
        }}

        if (submitSuccess === true){{
            document.querySelector(".message_window").classList.add("display-success");
            document.querySelector(".message_window").innerHTML = "Dataset enregistré !";  
        }}

        //Si remplissage du formulaire intérrompu, effacer message d'erreur
        if (document.querySelector(".message_window").classList.contains("display-error")) {{
            setTimeout(function() {{
                clearError();
            }}, 7000);
        }}     

    </script>
    """
    
    if form_button:
        html(html_to_execute, width=400, height=35)

        title = ss['file_title']
        dataset = ss['uploaded_file']

        if dataset is not None and title!='':
            wrong_character = None
            for letter in title:
                if letter in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    wrong_character = letter
                    break

            if wrong_character==None and title not in ss['datasets_available'].keys():               
                #mise à jour du nombre de dataset téléchargé
                ss['upload_count'] += 1

                #vérification du fichier json
                try:
                    pd.read_json(dataset)
                except:
                    ss['upload_count'] -= 1
                    msg = "Pandas n'a pas réussi à lire le fichier .json : Fichier supprimé."
                    error_message(msg) 

                    #si l'utilisateur ferme le modal en cliquant au-dehors, supprime l'iframe
                    time.sleep(3)
                    st.rerun()
                else:
                    #chargement dans la bibliothèque
                    ss['datasets_available'].update({title : dataset})

                    #mise-à-jour de la liste de sélection des datasets
                    ss['selectbox_options'] = ss['datasets_available'].keys()
                    st.rerun()

@st.dialog("Dataset à supprimer")
def remove_dataset():
    check_list = {}
    for item in ss['datasets_available'].keys():
        if item == 'steam':
            st.checkbox(item, disabled=True)
        else:
            st.checkbox(item, key='checkbox_'+item)
            check_list.update({'checkbox_'+item: item})

    if st.button('Valider'):
        #suppression de la bibliothèque
        for key, dataset_name in check_list.items():
            if ss[key] == True:
                ss['datasets_available'].pop(dataset_name)

        #mise-à-jour de la liste de sélection des datasets
        ss['selectbox_options'] = ss['datasets_available'].keys()
        st.rerun()

#Parties Aperçu du dataset & Réalisation des graphiques
#Fonction : mettre-à-jour les colonnes et le graphique à afficher
def update_columns_and_dataset_displayed():
    #mise-à-jour des colonnes à proposer
    dataset_name = ss['selectbox_key']
    ss['multiselect_options'] = ss['datasets_available'][dataset_name].columns
    
    #mise-à-jour du dataset affiché 
    ss['dataframe_displayed'] = ss['datasets_available'][dataset_name]
    
#Fonction : activer la sélection des graphiques selon les types des colonnes choisies
def update_proposed_graphs():
    #récupération de la valeur des colonnes sélectionnées
    selected_columns = ss['multiselect_key']

    #détermination et comptes des types des colonnes sélectionnées
    columns_types = ss['dataframe_displayed'][selected_columns].dtypes
    num_count = 0
    for item in ['int','float','<M8[ns]']:
        num_count += columns_types.tolist().count(item)

    columns_types = columns_types.unique().tolist()

    #types de graphiques possibles selon le type de colonne
    num = ['distribution','evolution','correlation_scatter','correlation_bubble']
    cat = ['hierarchy','composition']

    #valeur du graph à plotter selon les pills activées
    plot_values = {'distribution': ['Histogramme','Diagramme de densité','Diagramme en boîte'],
                   'evolution': ['Graphique linéaire','Graphique en aires'],
                   'correlation_scatter': ['Nuage de points'],
                   'correlation_bubble': ['Graphique à bulles'],
                   'hierarchy': ['Graphique en barres','Graphique lollipop','Nuage de mots'],
                   'composition': ['Diagramme circulaire','Treemap']}

    #activation selon le type de colonnes
    #Pas de colonne sélectionnée
    if columns_types == []:
        ss['graph_to_plot'] = None
        for name in num + cat: 
            if ss['disabled'][name] == False:
                ss['disabled'][name] = True
                ss['graphs'][name] = generate_random_key()
    
    #Colonnes numérique et catégorielle
    elif ('int' in columns_types or 'float' in columns_types or '<M8[ns]' in columns_types) and 'O' in columns_types:
        #activation des tous les graphiques
        for name in num + cat:
            #conditions à respecter pour scatter et bubble plot
            if ss['disabled'][name] == True:
                if name=='correlation_bubble' and num_count<3:
                    continue
                elif name=='correlation_scatter' and num_count<2:
                    continue
                else:
                    ss['disabled'][name] = False
                    ss['graphs'][name] = generate_random_key()
            #désactivation de scatter et bubble plot si conditions non respectées
            elif ss['disabled']['correlation_bubble']==False and num_count<3:
                ss['disabled']['correlation_bubble'] = True
                ss['graphs']['correlation_bubble'] = generate_random_key()

                #désactivation du graphique si pill correspondante desactivée
                if ss['graph_to_plot'] in plot_values['correlation_bubble']:
                    ss['graph_to_plot'] = None
                    
            elif num_count < 2:
                if ss['disabled']['correlation_bubble']==False:
                    ss['disabled']['correlation_bubble'] = True
                    ss['graphs']['correlation_bubble'] = generate_random_key()
                    if ss['graph_to_plot'] in plot_values['correlation_bubble']:
                        ss['graph_to_plot'] = None

                if ss['disabled']['correlation_scatter']==False:
                    ss['disabled']['correlation_scatter'] = True
                    ss['graphs']['correlation_scatter'] = generate_random_key()
                    if ss['graph_to_plot'] in plot_values['correlation_scatter']:
                        ss['graph_to_plot'] = None
    
    #Colonnes numériques
    elif 'int' in columns_types or 'float' in columns_types or '<M8[ns]' in columns_types:
        #activation des graphs numériques
        for name in num:
            #conditions à respecter pour scatter et bubble plot
            if ss['disabled'][name] == True:
                if name=='correlation_bubble' and num_count<3:
                    continue
                elif name=='correlation_scatter' and num_count<2:
                    continue
                else:
                    ss['disabled'][name] = False
                    ss['graphs'][name] = generate_random_key()
            #désactivation de scatter et bubble plot si conditions non respectées
            elif ss['disabled']['correlation_bubble']==False and num_count<3:
                ss['disabled']['correlation_bubble'] = True
                ss['graphs']['correlation_bubble'] = generate_random_key()

                #désactivation du graphique si pill correspondante desactivée
                if ss['graph_to_plot'] in plot_values['correlation_bubble']:
                    ss['graph_to_plot'] = None

            elif num_count < 2:
                if ss['disabled']['correlation_bubble']==False:
                    ss['disabled']['correlation_bubble'] = True
                    ss['graphs']['correlation_bubble'] = generate_random_key()
                    if ss['graph_to_plot'] in plot_values['correlation_bubble']:
                        ss['graph_to_plot'] = None

                if ss['disabled']['correlation_scatter']==False:
                    ss['disabled']['correlation_scatter'] = True
                    ss['graphs']['correlation_scatter'] = generate_random_key()
                    if ss['graph_to_plot'] in plot_values['correlation_scatter']:
                        ss['graph_to_plot'] = None

        #désactivation des graphs catégoriels
        for name in cat:
            if ss['disabled'][name] == False:
                ss['disabled'][name] = True
                ss['graphs'][name] = generate_random_key()
                if ss['graph_to_plot'] in plot_values[name]:
                    ss['graph_to_plot'] = None
    
    #Colonnes catégorielles
    elif 'O' in columns_types:
        #activation des graphs catégoriels
        for name in cat:
            if ss['disabled'][name] == True:
                ss['disabled'][name] = False
                ss['graphs'][name] = generate_random_key()

        #désactivation des graphs numériques
        for name in num:
            if ss['disabled'][name] == False:
                ss['disabled'][name] = True
                ss['graphs'][name] = generate_random_key()
                if ss['graph_to_plot'] in plot_values[name]:
                    ss['graph_to_plot'] = None

#Fonction : activer / désactiver les pills selon sélection et réaliser le graphique
def disable_pills_and_plot(a,b,c,d,e,f,g,h,i,j): 
    #clé sélectionnée
    selected_pill = ''.join([a,b,c,d,e,f,g,h,i,j])
    
    #désactiver les autres clés
    for key, value in ss['graphs'].items():
        if value == selected_pill:
            continue
        else:
            ss['default'][key] = None
            ss['graphs'][key] = generate_random_key()

    #indication du graph à plotter
    ss['graph_to_plot'] = ss[selected_pill]



#décomposition de l'écran d'affichage
col1, col2, col3 = st.columns([0.655, 0.001, 0.344])

#colonne de droite: gestion / options des graphiques
with col3:
    st.title('Options')
    #partie sélection des colonnes à utiliser
    with st.container(border=True):
        selected_columns = st.multiselect('Sélection des colonnes :', options=ss['multiselect_options'], max_selections=5, key='multiselect_key', on_change=update_proposed_graphs)


    #partie sélection du graphique à réaliser
    with st.expander('Type de graphique'): 
        tab1, tab2, tab3, tab4, tab5 = st.tabs(['Distribution','Evolution','Corrélation','Hiérarchie','Composition'])
        
        with tab1: #Distribution 
            st.pills('', options=['Histogramme','Diagramme de densité','Diagramme en boîte'], default=ss['default']['distribution'], disabled=ss['disabled']['distribution'], key=ss['graphs']['distribution'], label_visibility='collapsed', on_change=disable_pills_and_plot, args=ss['graphs']['distribution'])
        with tab2: #Evolution   
            st.pills('', options=['Graphique linéaire','Graphique en aires'], default=ss['default']['evolution'], disabled=ss['disabled']['evolution'], key=ss['graphs']['evolution'], label_visibility='collapsed', on_change=disable_pills_and_plot, args=ss['graphs']['evolution'])
        with tab3: #Corrélation
            help_scatter = 'Sélectionnez 2 colonnes numériques'
            help_bubble = 'Sélectionnez 3 colonnes numériques'
            st.pills('', options=['Nuage de points'], help=help_scatter, default=ss['default']['correlation_scatter'], disabled=ss['disabled']['correlation_scatter'], key=ss['graphs']['correlation_scatter'], on_change=disable_pills_and_plot, args=ss['graphs']['correlation_scatter'])
            st.pills('', options=['Graphique à bulles'], help=help_bubble,  default=ss['default']['correlation_bubble'], disabled=ss['disabled']['correlation_bubble'], key=ss['graphs']['correlation_bubble'], on_change=disable_pills_and_plot, args=ss['graphs']['correlation_bubble'])
        with tab4: #Hiérarchie
            st.pills('', options=['Graphique en barres','Graphique lollipop','Nuage de mots'], default=ss['default']['hierarchy'], disabled=ss['disabled']['hierarchy'], key=ss['graphs']['hierarchy'], label_visibility='collapsed', on_change=disable_pills_and_plot, args=ss['graphs']['hierarchy'])
        with tab5: #Composition
            st.pills('', options=['Diagramme circulaire','Treemap'], default=ss['default']['composition'], disabled=ss['disabled']['composition'], key=ss['graphs']['composition'], label_visibility='collapsed', on_change=disable_pills_and_plot, args=ss['graphs']['composition'])


    #partie sélection des axes et options correspondantes pour chaque graphique       
    with st.expander('Paramètres des axes'):
        #récupération du dataset
        df = ss['dataframe_displayed']
        
        #répartition des colonnes selon leur type
        num_columns, cat_columns = [], []
        for column in selected_columns:
            if df[column].dtypes in ['int','float','<M8[ns]']:
                num_columns.append(column) 
            elif df[column].dtypes == 'O':
                cat_columns.append(column) 

        #configuration des axes et options nécessaires pour chaque graphique
        #pas de graphique sélectionné
        if ss['graph_to_plot'] == None:
            st.write('*Sélectionnez un graphique*')
            x_column = None
            y_column = None

        #histogramme
        elif ss['graph_to_plot'] == 'Histogramme':
            x_column = st.selectbox('x :', options=num_columns) 
            bins_value = st.number_input('bins :', value=10, min_value=2, max_value=200, help='valeurs possibles : 2 à 200')
            group_column = None
            y_column = None
            
            #activation et options du tri par groupe
            if cat_columns == []:
                st.checkbox('trier par groupe', key='hist', disabled=True)   
            else:
                checkbox = st.checkbox('trier par groupe :', key='hist')
                if checkbox == False:
                    st.selectbox('', options=cat_columns, disabled=True, label_visibility='collapsed')
                    st.number_input('nombre de catégories', value=10, disabled=True)
                else:
                    group_column = st.selectbox('', options=cat_columns, label_visibility='collapsed')
                    df = df.explode(group_column)
                    
                    max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, help='valeurs possibles : 2 à 50')
                    cat_new_values = df[group_column].value_counts().index[:max_displayed]
                    df = df[df[group_column].isin(cat_new_values)==True]

        #diagramme de densité - density plot         
        elif ss['graph_to_plot'] == 'Diagramme de densité':
            x_column = st.selectbox('x :', options=num_columns) 
            alpha_value = st.number_input('alpha :', value=0.5, min_value=0.0, max_value=1.0, help='valeurs possibles : 0 à 1')
            group_column = None
            y_column = None

            #activation et options du tri par groupe
            if cat_columns == []:
                st.checkbox('trier par groupe', key='density', disabled=True)   
            else:
                checkbox = st.checkbox('trier par groupe :', key='density')
                if checkbox == False:
                    st.selectbox('', options=cat_columns, disabled=True, label_visibility='collapsed')
                    st.number_input('nombre de catégories', value=10, disabled=True)
                else:
                    group_column = st.selectbox('', options=cat_columns, label_visibility='collapsed')
                    df = df.explode(group_column)
                    
                    max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, help='valeurs possibles : 2 à 50')
                    cat_new_values = df[group_column].value_counts().index[:max_displayed]
                    df = df[df[group_column].isin(cat_new_values)==True]

        #diagramme en boîte - boxplot 
        elif ss['graph_to_plot'] == 'Diagramme en boîte':
            x_column = st.selectbox('x :', options=num_columns) 
            group_column = None
            y_column = None

            #activation et options du tri par groupe
            if cat_columns == []:
                st.checkbox('trier par groupe', key='boxplot', disabled=True)   
            else:
                checkbox = st.checkbox('trier par groupe :', key='boxplot')
                if checkbox == False:
                    st.selectbox('', options=cat_columns, disabled=True, label_visibility='collapsed')
                    st.number_input('nombre de catégories', value=10, disabled=True)
                else:
                    group_column = st.selectbox('', options=cat_columns, label_visibility='collapsed')
                    df = df.explode(group_column)
                    
                    max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, help='valeurs possibles : 2 à 50')
                    cat_new_values = df[group_column].value_counts().index[:max_displayed]
                    df = df[df[group_column].isin(cat_new_values)==True]

        #graphique linéaire - lineplot 
        elif ss['graph_to_plot'] == 'Graphique linéaire':
            x_column = st.selectbox('x :', options=['index']+num_columns) 
            y_column = st.selectbox('y :', options=num_columns) 
            group_column = None

            #tri pour une évolution croissante de x 
            df_x = df.copy()
            if x_column == 'index':
                df_x.insert(0, 'index', df_x.index)
            elif x_column != 'index':
                df_x = df_x.sort_values(by=x_column).reset_index()
            
            #activation et options du tri par groupe
            if cat_columns == []:
                st.checkbox('trier par groupe', key='lineplot', disabled=True)   
            else:
                checkbox = st.checkbox('trier par groupe :', key='lineplot')
                if checkbox == False:
                    st.selectbox('', options=cat_columns, disabled=True, label_visibility='collapsed')
                    st.number_input('nombre de catégories', value=10, disabled=True)
                else:
                    group_column = st.selectbox('', options=cat_columns, label_visibility='collapsed')
                    df_x = df_x.explode(group_column)
                    
                    max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, help='valeurs possibles : 2 à 50')
                    cat_new_values = df_x[group_column].value_counts().index[:max_displayed]
                    df_x = df_x[df_x[group_column].isin(cat_new_values)==True]

        #graphique en aires - areaplot  
        elif ss['graph_to_plot'] == 'Graphique en aires':
            x_column = st.selectbox('x :', options=['index']+num_columns) 
            y_column = st.selectbox('y :', options=num_columns) 
            alpha_value = st.number_input('alpha :', value=0.5, min_value=0.0, max_value=1.0, help='valeurs possibles : 0 à 1')
            
            #tri croissant pour une évolution selon x
            df_x = df.copy()
            if x_column == 'index':
                df_x.insert(0, 'index', df_x.index)
            elif x_column != 'index':
                df_x = df_x.sort_values(by=x_column).reset_index()

        #nuage de points - scatter plot 
        elif ss['graph_to_plot'] == 'Nuage de points':
            x_column = st.selectbox('x :', options=num_columns)
            y_column = st.selectbox('y :', options=num_columns, index=1)
            group_column = None
            alpha_value = st.number_input('alpha :', value=0.5, min_value=0.0, max_value=1.0, help='valeurs possibles : 0 à 1')
            
            #activation et options du tri par groupe
            if cat_columns == []:
                st.checkbox('trier par groupe', key='scatter', disabled=True)   
            else:
                checkbox = st.checkbox('trier par groupe :', key='scatter')
                if checkbox == False:
                    st.selectbox('', options=cat_columns, disabled=True, label_visibility='collapsed')
                    st.number_input('nombre de catégories', value=10, disabled=True)
                else:
                    group_column = st.selectbox('', options=cat_columns, label_visibility='collapsed')
                    df = df.explode(group_column).reset_index()
                    
                    max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, help='valeurs possibles : 2 à 50')
                    cat_new_values = df[group_column].value_counts().index[:max_displayed]
                    df = df[df[group_column].isin(cat_new_values)==True]

        #graphique à bulles - bubble plot 
        elif ss['graph_to_plot'] == 'Graphique à bulles':
            x_column = st.selectbox('x :', options=num_columns)
            y_column = st.selectbox('y :', options=num_columns, index=1)
            group_column = None
            bubble_column = st.selectbox('bulles :', options=num_columns, index=2)
            bubble_size_min = st.number_input('taille des bulles :', value=20, min_value=1, max_value=100, help='valeurs possibles : 1 à 100')
            bubble_size_max = st.number_input('à :', value=350, min_value=101, max_value=600, help='valeurs possibles : 101 à 600')
            alpha_value = st.number_input('alpha :', value=0.5, min_value=0.0, max_value=1.0, help='valeurs possibles : 0 à 1')
            
            #activation et options du tri par groupe
            if cat_columns == []:
                st.checkbox('trier par groupe', key='bubble', disabled=True)   
            else:
                checkbox = st.checkbox('trier par groupe :', key='bubble')
                if checkbox == False:
                    st.selectbox('', options=cat_columns, disabled=True, label_visibility='collapsed')
                    st.number_input('nombre de catégories', value=10, disabled=True)
                else:
                    group_column = st.selectbox('', options=cat_columns, label_visibility='collapsed')
                    df = df.explode(group_column).reset_index()
                    
                    max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, help='valeurs possibles : 2 à 50')
                    cat_new_values = df[group_column].value_counts().index[:max_displayed]
                    df = df[df[group_column].isin(cat_new_values)==True]

        #graphique en barres - barplot 
        elif ss['graph_to_plot'] == 'Graphique en barres':
            y_column = st.selectbox('colonne:', options=cat_columns)
            df = df.explode(y_column)
            max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, key='limit_barplot', help='valeurs possibles : 2 à 50')
            values = df[y_column].value_counts().values[:max_displayed]
            labels = df[y_column].value_counts().index[:max_displayed]   
            x_column = None

        #graphique lollipop 
        elif ss['graph_to_plot'] == 'Graphique lollipop':
            y_column = st.selectbox('colonne :', options=cat_columns)
            df = df.explode(y_column)
            max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, key='limit_lollipop', help='valeurs possibles : 2 à 50')
            values = df[y_column].value_counts().values[:max_displayed]
            labels = df[y_column].value_counts().index[:max_displayed]
            x_column = None

        #nuage de mots - wordcloud 
        elif ss['graph_to_plot'] == 'Nuage de mots':
            column = st.selectbox('colonne :', options=cat_columns)
            df = df[df[column].isna()==False].explode(column)
            width_value = st.number_input('largeur :', value=480, min_value=350, max_value=1000, help='valeurs possibles : 350 à 1000')
            height_value = st.number_input('hauteur :', value=480, min_value=350, max_value=1000, help='valeurs possibles : 350 à 1000')
            min_size = st.number_input('taille des mots :', value=10, min_value=5, max_value=20, help='valeurs possibles : 5 à 20')
            max_size = st.number_input('à', value=50, min_value=21, max_value=100, help='valeurs possibles : 21 à 100')
            x_column = None
            y_column = None

        #diagramme circulaire - piechart 
        elif ss['graph_to_plot'] == 'Diagramme circulaire':
            column = st.selectbox('colonne :', options=cat_columns)
            df = df.explode(column)
            max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, key='limit_piechart', help='valeurs possibles : 2 à 50')
            values = df[column].value_counts().values[:max_displayed]
            labels = df[column].value_counts().index[:max_displayed]
            x_column = None
            y_column = None

        #treemap
        elif ss['graph_to_plot'] == 'Treemap':
            column = st.selectbox('colonne :', options=cat_columns)
            df = df.explode(column)
            max_displayed = st.number_input('nombre de catégories', value=10, min_value=2, max_value=50, key='limit_treemap', help='valeurs possibles : 2 à 50')
            values = df[column].value_counts().values[:max_displayed]
            labels = df[column].value_counts().index[:max_displayed]
            alpha_value = st.number_input('alpha :', value=0.5, min_value=0.0, max_value=1.0, help='valeurs possibles : 0 à 1')
            x_column = None
            y_column = None


    #partie ajustement de la légende
    with st.expander('Modification de la légende'):
        if ss['graph_to_plot'] == None:
            st.write('*Sélectionnez un graphique*')
        else:

            #possibilité d'ajout d'un titre et modification des noms de x et y
            fig_title = st.text_input('titre', value='')
            if x_column != None:
                fig_xlabel = st.text_input('axe x', value=x_column, placeholder=x_column)
            if y_column != None:
                fig_ylabel = st.text_input('axe y', value=y_column, placeholder=y_column)


#colonne centrale: affichage de graphiques, gestion des datasets
with col1:
    st.title('Visualization for Data')
    #partie affichage des graphiques
    with st.container(border=True):
        fig, ax = plt.subplots()#figsize=(size_h,size_v)) #ajuster apres avoir mis la légende
        ss['ax'] = ax
        if ss['graph_to_plot'] == None:
            st.bar_chart(pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"]))
        
        elif ss['graph_to_plot'] == 'Histogramme':
            sns.histplot(data=df, x=x_column, bins=bins_value, hue=group_column)
            plt.title(fig_title)
            plt.xlabel(fig_xlabel)
            st.pyplot(fig)
        
        elif ss['graph_to_plot'] == 'Diagramme de densité':
            sns.kdeplot(data=df, x=x_column, fill=True, hue=group_column, alpha=alpha_value)
            plt.title(fig_title)
            plt.xlabel(fig_xlabel)
            st.pyplot(fig)
        
        elif ss['graph_to_plot'] == 'Diagramme en boîte':
            sns.boxplot(data=df, x=x_column, y=group_column, orient='h')
            plt.title(fig_title)
            plt.xlabel(fig_xlabel)
            st.pyplot(fig)
            
        elif ss['graph_to_plot'] == 'Graphique linéaire':
            sns.lineplot(data=df_x, x=x_column, y=y_column, hue=group_column)
            plt.title(fig_title)
            plt.xlabel(fig_xlabel)
            plt.ylabel(fig_ylabel)
            st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Graphique en aires':
            plt.fill_between(data=df_x, x=x_column, y1=0, y2=y_column, alpha=alpha_value)
            plt.title(fig_title)
            plt.xlabel(fig_xlabel)
            plt.ylabel(fig_ylabel)
            st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Nuage de points':
            sns.scatterplot(data=df, x=x_column, y=y_column, hue=group_column, alpha=alpha_value, edgecolor='black')
            plt.title(fig_title)
            plt.xlabel(fig_xlabel)
            plt.ylabel(fig_ylabel)
            st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Graphique à bulles':
            sns.scatterplot(data=df, x=x_column, y=y_column, size=bubble_column, sizes=(bubble_size_min,bubble_size_max), hue=group_column, alpha=alpha_value, edgecolor='black')
            plt.title(fig_title)
            plt.xlabel(fig_xlabel)
            plt.ylabel(fig_ylabel)
            st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Graphique en barres':
            sns.barplot(x=values, y=labels, estimator='sum')
            plt.title(fig_title)
            plt.ylabel(fig_ylabel)
            st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Graphique lollipop':
            plt.stem(values, orientation='horizontal')
            plt.yticks(range(len(values)), labels)
            plt.gca().invert_yaxis()
            plt.title(fig_title)
            plt.ylabel(fig_ylabel)
            st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Nuage de mots':
            text = ' '.join(['"""'] + list(df[column]) + ['"""'])
            try :
                wordcloud = WordCloud(width=width_value, height=height_value, min_font_size=min_size, max_font_size=max_size, background_color='white').generate(text)
            except:
                msg = 'Valeurs non reconnues par WordCloud! : Nombres ou plages de nombres'
                error_message(msg)

                ss['graph_to_plot'] = None
                ss['graphs']['hierarchy'] = generate_random_key()

                #si l'utilisateur ferme le modal en cliquant au-dehors, supprime l'iframe
                time.sleep(3)
                st.rerun()
            else:
                plt.imshow(wordcloud, interpolation="bilinear")
                plt.title(fig_title)
                plt.axis("off")
                st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Diagramme circulaire':
            plt.pie(x=values, labels=labels, labeldistance=1.15)
            plt.title(fig_title)
            st.pyplot(fig)

        elif ss['graph_to_plot'] == 'Treemap':
            squarify.plot(sizes=values, label=labels, alpha=alpha_value)
            plt.title(fig_title)
            plt.axis('off')
            st.pyplot(fig)
            

    #partie sélection du dataset, ajout d'un nouveau dataset
    with st.container():
        col1_a, col1_b, col1_c = st.columns([0.75, 0.15, 0.1], vertical_alignment='bottom')

        #colonne de sélection du dataset à utiliser
        with col1_a:
            st.selectbox('Sélection du jeu de données :', options=ss['selectbox_options'], key='selectbox_key', on_change=update_columns_and_dataset_displayed)

        #colonne de téléchargement d'un nouveau dataset
        with col1_b:
            with st.popover('', icon=':material/upload:', use_container_width=True):
                with st.form('dataset_form', clear_on_submit=True, enter_to_submit=False, border=False):
                    upload_help = """Télécharge 2 datasets (fichier .json, taille max 200 Mb)."""
                    st.file_uploader('Ajouter un dataset', type='json', help=upload_help, key='uploaded_file', disabled=ss['uploader_disabled'])
                    st.text_input('dataset_name', placeholder='Nom du dataset', label_visibility='collapsed', key='file_title', disabled=ss['title_disabled'])
                    submit_form()

                    if ss['upload_count'] == 2:
                        ss['title_disabled'] = True
                        ss['uploader_disabled'] = True
                        ss['form_submit_disabled'] = True
                        ss['upload_count'] += 1
                        st.rerun()

        #suppression de dataset
        with col1_c:
            delete_button = st.button('', icon=':material/cancel:')
            if delete_button:
                remove_dataset()


    #partie observation du dataset sélectionné, suppression de dataset
    with st.expander('Aperçu des données'):
        st.dataframe(ss['dataframe_displayed'])
