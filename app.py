import streamlit as st
import requests
import json
import anthropic
from typing import List, Dict, Tuple
import time
import re

# Charger les secrets si disponibles
if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
    st.session_state['anthropic_key'] = st.secrets['ANTHROPIC_API_KEY']
    st.session_state['serper_key'] = st.secrets['SERPER_API_KEY']
    st.session_state['api_configured'] = True

# ============================================
# CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Discover Writer",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS - Design moderne et épuré
# ============================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global */
    .stApp {
        background: linear-gradient(135deg, #fafafa 0%, #f0f4f8 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom header */
    .app-header {
        text-align: center;
        padding: 2rem 0 3rem 0;
    }
    
    .app-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .app-header p {
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        border-radius: 12px !important;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        font-family: 'Plus Jakarta Sans', sans-serif;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Progress */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 12px;
        margin-bottom: 0.75rem;
    }
    
    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
    }
    
    .step-text {
        color: #475569;
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    /* Result card */
    .result-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.2);
        margin-top: 1.5rem;
    }
    
    .result-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    .result-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .result-content {
        color: #334155;
        line-height: 1.8;
        font-size: 1rem;
    }
    
    /* Source pills */
    .source-pill {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
        font-weight: 500;
    }
    
    /* Success message */
    .success-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Fact-check styles */
    .fc-summary {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }
    
    .fc-score {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
    }
    
    .fc-score-good { color: #10b981; }
    .fc-score-medium { color: #f59e0b; }
    .fc-score-bad { color: #ef4444; }
    
    .fc-corrections-banner {
        background: linear-gradient(135deg, #10b98115, #05966915);
        border: 1px solid #10b98140;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        font-size: 0.9rem;
        color: #065f46;
    }
    
    /* Settings card */
    .settings-toggle {
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .settings-toggle a {
        color: #667eea;
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        color: #475569 !important;
        background: #f8fafc !important;
        border-radius: 12px !important;
    }
    
    /* Warning/Error */
    .stAlert {
        border-radius: 12px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #f1f5f9;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Radio buttons for mode selection */
    .stRadio > div {
        display: flex;
        gap: 1rem;
    }
    
    .stRadio > div > label {
        background: #f8fafc;
        padding: 0.75rem 1.25rem;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        border-color: #667eea;
    }
    
    .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def search_serper(query: str, api_key: str, num_results: int = 10) -> List[Dict]:
    """Recherche via Serper.dev"""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "gl": "fr",
        "hl": "fr",
        "num": num_results
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    
    results = []
    for item in data.get("organic", [])[:num_results]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", "")
        })
    
    return results


def search_serper_news(query: str, api_key: str, num_results: int = 5) -> List[Dict]:
    """Recherche via Serper.dev endpoint News (Google Actualités)"""
    url = "https://google.serper.dev/news"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "gl": "fr",
        "hl": "fr",
        "num": num_results
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("news", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "date": item.get("date", "")
            })
        
        return results
    except Exception as e:
        return []


def fetch_sources_for_fact_check(keyword: str, api_key: str) -> Tuple[List[Dict], List[str]]:
    """
    Récupère des sources indépendantes pour le fact-check en croisant :
    - Google Actualités (articles récents, changements, évolutions)
    - SERP classique (pages de référence, guides, sites institutionnels)
    Retourne jusqu'à 6 sources dédupliquées avec leur contenu.
    """
    all_sources = []
    seen_urls = set()
    
    # --- SERP classique : pages de référence et guides ---
    serp_queries = [
        f"{keyword} 2026 conditions éligibilité",
        f"{keyword} 2026 barème travaux éligibles",
    ]
    for q in serp_queries:
        results = search_serper(q, api_key, num_results=3)
        for r in results:
            if r['url'] not in seen_urls:
                seen_urls.add(r['url'])
                r['source_type'] = 'serp'
                all_sources.append(r)
    
    # --- Google Actualités : articles récents ---
    news_queries = [
        f"{keyword} 2026",
        f"{keyword} 2026 changements nouveautés",
    ]
    for q in news_queries:
        results = search_serper_news(q, api_key, num_results=4)
        for r in results:
            if r['url'] not in seen_urls:
                seen_urls.add(r['url'])
                r['source_type'] = 'news'
                all_sources.append(r)
    
    # Prendre 6 sources max : priorité à la diversité (alterner serp/news)
    serp_sources = [s for s in all_sources if s.get('source_type') == 'serp']
    news_sources = [s for s in all_sources if s.get('source_type') == 'news']
    
    # 3 serp + 3 news, ou plus de l'un si l'autre n'a pas assez
    final_sources = []
    final_sources.extend(serp_sources[:3])
    final_sources.extend(news_sources[:3])
    # Compléter jusqu'à 6 si un côté est court
    remaining = 6 - len(final_sources)
    if remaining > 0:
        extras = [s for s in all_sources if s not in final_sources]
        final_sources.extend(extras[:remaining])
    
    final_sources = final_sources[:6]
    
    # Scrapper le contenu
    fc_contents = []
    for source in final_sources:
        try:
            content = fetch_content_jina(source['url'])
            fc_contents.append(content)
        except Exception:
            fc_contents.append("Contenu non disponible")
    
    return final_sources, fc_contents


def fetch_content_jina(url: str, max_chars: int = 25000) -> str:
    """Récupère le contenu d'une page via Jina Reader en Markdown (préserve les tableaux)"""
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "Accept": "text/markdown",
        "X-Return-Format": "markdown"
    }
    
    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.text[:max_chars]
        return content
    except Exception as e:
        # Fallback en text/plain si le markdown échoue
        try:
            headers_fallback = {"Accept": "text/plain"}
            response = requests.get(jina_url, headers=headers_fallback, timeout=30)
            response.raise_for_status()
            return response.text[:max_chars]
        except Exception as e2:
            return f"Erreur lors de la récupération: {str(e2)}"


def extract_title_from_url(url: str) -> str:
    """Extrait un titre simple depuis l'URL"""
    title = url.replace("https://", "").replace("http://", "").replace("www.", "")
    parts = title.split("/")
    if len(parts) > 1 and parts[1]:
        return f"{parts[0]} - {parts[1][:30]}"
    return parts[0]


# ============================================
# GÉNÉRATION DE L'ARTICLE
# ============================================

def generate_article(
    client: anthropic.Anthropic,
    keyword: str,
    sources: List[Dict],
    contents: List[str],
    custom_instructions: str = "",
    article_length: int = 800
) -> str:
    """Génère l'article via Claude"""
    
    # Préparer le contexte des sources
    sources_context = ""
    for i, (source, content) in enumerate(zip(sources, contents), 1):
        sources_context += f"""
--- SOURCE {i} ---
Titre: {source['title']}
URL: {source['url']}
Contenu:
{content[:12000]}

"""
    
    # Construire le bloc persona. S'il est renseigné, il PILOTE tout le style.
    # S'il est vide, on applique un style par défaut développé.
    if custom_instructions and custom_instructions.strip():
        persona_block = f"""## RÈGLE N°1 — PERSONA ET DIRECTIVES ÉDITORIALES (PRIORITÉ ABSOLUE)

Les consignes ci-dessous ont été rédigées par l'équipe éditoriale. Elles PRIMENT SUR TOUT le reste de ce prompt — ton, style, niveau de langue, tutoiement/vouvoiement, longueur des phrases, registre, humour, technicité, persona, format, tout.

Si une consigne éditoriale contredit une règle ci-dessous (par ex. le persona demande du tutoiement alors que la règle par défaut dit vouvoiement, ou le persona demande un style concis alors que le défaut est développé), c'est LE PERSONA QUI GAGNE. Toujours.

### CONSIGNES ÉDITORIALES :
{custom_instructions}

### CE QUE ÇA IMPLIQUE :
- Adopte le ton, le style et le persona décrits ci-dessus dès la première phrase et maintiens-le jusqu'à la dernière
- Si le persona définit un niveau de développement (concis, détaillé, conversationnel...), applique-le — il remplace les consignes de développement par défaut
- Si le persona définit un registre (familier, expert, humoristique...), chaque phrase doit sonner dans ce registre
- Si le persona utilise le tutoiement, tutoie. S'il vouvoie, vouvoie. S'il ne précise pas, vouvoie par défaut.
- En cas de doute, relis les consignes éditoriales et demande-toi : "est-ce que ma phrase sonne comme ce persona l'écrirait ?" Si non, reformule."""
    else:
        persona_block = """## STYLE PAR DÉFAUT (aucun persona renseigné)

En l'absence de consignes éditoriales spécifiques, applique ce style par défaut :
- Ton expert mais chaleureux et accessible, jamais scolaire ni robotique
- Vouvoiement naturel
- Style développé : chaque idée est expliquée, illustrée et contextualisée (paragraphes de 3-6 phrases)
- Le lecteur doit sentir qu'un humain passionné lui parle"""

    system_prompt = f"""Tu es un rédacteur web polyvalent qui s'adapte parfaitement au brief éditorial qu'on lui donne. Tu écris comme un humain, pas comme une IA.

{persona_block}

## RÈGLES STRUCTURELLES (s'appliquent toujours, sauf si le persona les contredit explicitement)

### Variance structurelle
- Varier la longueur des sections : certaines font 2-3 phrases, d'autres 8-10
- Ne commence jamais deux H2 consécutifs de la même façon
- Varie le formatage entre sections : prose seule, puis une liste, puis un tableau si pertinent
- INTERDIT : que deux sections consécutives aient la même structure interne

### Fluidité et transitions
- Chaque paragraphe s'enchaîne logiquement avec le précédent
- Transitions variées et naturelles, jamais mécaniques
- Les fins de section donnent envie de lire la suite

### Développement des idées (SI le persona ne précise pas le niveau)
Pour chaque idée introduite :
1. Énonce le fait clairement
2. Développe le pourquoi/comment (1-2 phrases minimum)
3. Illustre avec un exemple, chiffre contextualisé ou comparaison
4. Relie à l'idée suivante

Style "sec" INTERDIT sauf demande explicite du persona :
❌ "L'IA transforme le recrutement. Les entreprises l'utilisent pour trier les CV. Cela fait gagner du temps."
✅ "L'intelligence artificielle redessine les contours du recrutement, et pas seulement à la marge. Là où un recruteur passait en moyenne 30 secondes par CV, les algorithmes analysent désormais des centaines de candidatures en quelques minutes, en croisant des critères bien plus fins que les simples mots-clés."

## ACCROCHE
- Ancrage contextuel dès la première phrase (actualité, tendance, chiffre, saison...)
- Le lecteur doit comprendre pourquoi lire ça MAINTENANT
- Pas d'intro bateau type "Le [sujet] est devenu incontournable"

## FORMATAGE
- **Gras** sur les mots-clés stratégiques uniquement (pas les phrases entières)
- Listes à puces UNIQUEMENT pour les énumérations concrètes
- Tableau Markdown UNIQUEMENT si données chiffrées comparables
- En cas de doute entre liste et prose → prose

## ENRICHISSEMENT SÉMANTIQUE
- Intègre naturellement les entités liées au sujet
- Données chiffrées quand disponibles dans les sources
- Expertise qui va au-delà des mots-clés évidents

## RIGUEUR FACTUELLE — RÈGLE CRITIQUE

Tu rédiges un article journalistique, pas un texte créatif. La précision factuelle est NON NÉGOCIABLE :

- **Ne cite que des chiffres, dates, noms et faits présents TEXTUELLEMENT dans les sources fournies.** Si une info n'est pas dans les sources, ne l'invente pas.
- **INTERDIT DE CALCULER, EXTRAPOLER OU ARRONDIR DES CHIFFRES.** Ne fais jamais de calcul à partir de données sources pour en déduire un nouveau chiffre (ex : appliquer un taux de revalorisation à un barème ancien pour obtenir un barème "à jour"). Si le chiffre exact n'est pas dans les sources, ne le donne pas.
- **Si tu n'as pas de chiffre précis, ne fabrique pas de pourcentage ou de statistique.** Utilise des formulations qui renvoient vers la source officielle du sujet. Un tableau avec des chiffres faux est pire qu'un paragraphe qui renvoie vers le site de référence.
- **Pour les barèmes, grilles tarifaires, seuils de revenus** : ne les cite que si tu les trouves mot pour mot dans les sources. Sinon, décris le mécanisme général et renvoie vers la source officielle.
- **Distingue les faits des interprétations.** Les faits viennent des sources. Tes mises en perspective doivent être formulées comme telles ("ce qui suggère que...", "on peut y voir...").
- **En cas de doute sur un fait, formulation prudente** plutôt qu'affirmation.
- **Chaque donnée chiffrée doit être contextualisée** : d'où elle vient (quel acteur, quelle source), à quelle période elle se rapporte.

## LISTES ET CATÉGORIES — RÈGLE CRITIQUE

Quand un sujet comporte plusieurs catégories, parcours, profils ou niveaux (ex : différentes formules, tranches, types de bénéficiaires) :

- **Ne mélange JAMAIS les éléments d'une catégorie avec ceux d'une autre.** Avant de lister ce qui est éligible, autorisé ou inclus dans une catégorie, vérifie dans les sources que chaque élément appartient BIEN à cette catégorie précise — pas à une catégorie voisine.
- **Mentionne TOUJOURS les exclusions.** Si certains profils, publics ou cas de figure sont exclus d'un dispositif, d'une offre ou d'une catégorie, c'est une info critique pour le lecteur. Ne l'omets jamais. Un lecteur qui croit être éligible alors qu'il ne l'est pas, c'est pire qu'un lecteur à qui tu dis "vérifiez votre éligibilité".
- **RÉFLEXE D'INVERSION : chaque fois que tu décris qui/quoi est éligible, pose-toi la question inverse.** Regarde les tableaux et listes dans les sources : si une catégorie, un profil ou un cas de figure n'y apparaît PAS, c'est probablement une exclusion qu'il faut mentionner. Concrètement : si un tableau liste des montants pour les profils A, B et C mais pas D, alors D est exclu — dis-le au lecteur. Si une liste de travaux éligibles mentionne X et Y mais pas Z alors que Z existe dans le même domaine, signale que Z n'est pas couvert. L'absence dans un tableau est une information, pas un oubli à ignorer.
- **Ne fabrique AUCUN item de liste.** Chaque élément d'une énumération (travaux éligibles, documents requis, conditions à remplir, etc.) doit figurer explicitement dans les sources. N'ajoute pas un item parce qu'il te semble logique ou plausible.
- **Si un élément a changé récemment** (ajouté, retiré, modifié), signale-le explicitement. Les changements récents sont l'info la plus précieuse pour le lecteur.
- **Vérifie la cohérence interne.** Si tu écris dans un paragraphe qu'un élément est exclu, ne le liste pas comme éligible dans un autre paragraphe. Relis ton article avant de le finaliser pour traquer ces contradictions.

## LONGUEUR

L'article doit faire environ {article_length} mots. C'est une cible, pas un minimum à atteindre coûte que coûte. Ne remplis JAMAIS pour atteindre une longueur.

## À BANNIR ABSOLUMENT

- Tournures IA : "Il est important de noter", "Dans cet article", "N'hésitez pas", "Il convient de", "Force est de constater", "À l'heure où"
- Structures symétriques (3 sections de même taille, 3 paragraphes miroirs)
- Intros génériques sans accroche
- Remplissage et reformulations qui n'apportent rien
- Liens et URLs : jamais de [texte](url), jamais d'URL brute
- Commencer un paragraphe par "Il est" ou "Il faut"
- "Certes... mais" plus d'une fois par article
- INVENTER des chiffres, statistiques, noms d'études ou citations absents des sources

## CONTEXTE TEMPOREL
Nous sommes en 2026. Ne mentionne jamais 2025 comme étant l'année en cours."""

    user_prompt = f"""Analyse ces {len(sources)} sources sur "{keyword}" et rédige un article optimisé Discover.

{sources_context}

CONSIGNES :
1. Identifie les infos clés, données chiffrées, angles différenciants
2. Repère les entités importantes à intégrer (personnes, marques, concepts...)
3. IMPORTANT : ne retiens QUE les informations factuellement présentes dans les sources.

**MÉTADONNÉES SEO (à fournir EN PREMIER, avant l'article) :**

## TITRES (H1)
Propose 5 titres H1 différents, numérotés de 1 à 5 :
- Variés : question, affirmation, how-to, liste, angle émotionnel
- Accrocheurs sans être clickbait
- Entre 50 et 70 caractères idéalement

## TITLE SEO
Propose 1 balise title optimisée :
- Maximum 60 caractères (espaces compris)
- Mot-clé principal au début si possible
- Incitation au clic

## META DESCRIPTION
Propose 1 meta description :
- Entre 150 et 155 caractères (espaces compris)
- Résume la promesse de l'article
- Contient le mot-clé principal
- Incite au clic avec un bénéfice clair

---

**ARTICLE :**
3. Démarre par une accroche contextuelle forte
4. Structure adaptée au type de contenu
5. Intègre les entités naturellement
6. Utilise le gras sur les mots-clés stratégiques
7. Termine sur une note mémorable
8. AUCUN LIEN dans l'article (ni [texte](url) ni URL brute)
9. DÉVELOPPE chaque idée (sauf si le persona demande un style concis)

CONTRAINTE DE LONGUEUR : L'article (hors métadonnées) doit faire environ {article_length} mots.

FORMAT DE RÉPONSE OBLIGATOIRE :
```
## TITRES (H1)
1. [titre 1] (XX caractères)
2. [titre 2] (XX caractères)
3. [titre 3] (XX caractères)
4. [titre 4] (XX caractères)
5. [titre 5] (XX caractères)

## TITLE SEO
[title] (XX caractères)

## META DESCRIPTION
[meta description] (XXX caractères)

---

[ARTICLE COMPLET EN MARKDOWN SANS AUCUN LIEN]
```"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=6000,
        temperature=0.8,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system=system_prompt
    )
    
    return response.content[0].text


# ============================================
# FACT-CHECK + CORRECTION AUTOMATIQUE
# ============================================

def fact_check_and_correct(
    client: anthropic.Anthropic,
    article: str,
    fc_sources: List[Dict],
    fc_contents: List[str],
    keyword: str,
    custom_instructions: str = ""
) -> Tuple[str, str]:
    """
    Vérifie les faits de l'article contre des sources Google Actualités indépendantes.
    Retourne (rapport_fact_check, article_corrigé).
    """
    
    sources_context = ""
    for i, (source, content) in enumerate(zip(fc_sources, fc_contents), 1):
        date_info = f" ({source.get('date', '')})" if source.get('date') else ""
        sources_context += f"""
--- SOURCE {i} : {source['title']}{date_info} ---
URL: {source['url']}
Contenu:
{content[:12000]}

"""
    
    system_prompt = """Tu es un fact-checker et correcteur éditorial rigoureux. Tu travailles avec deux types de sources indépendantes de celles utilisées pour rédiger l'article :
- Des pages de référence issues de la SERP Google (guides, sites institutionnels, comparateurs)  
- Des articles d'actualité récents issus de Google Actualités

Cette double vérification te permet de croiser les informations de fond (règles, conditions, listes) avec les évolutions récentes (changements, exclusions, nouveautés).

Tu as TROIS missions :

MISSION 1 — VÉRIFICATION DES AFFIRMATIONS : analyser chaque affirmation factuelle de l'article (chiffres, dates, noms, statistiques, conditions, règles) et la croiser avec les sources d'actualité fournies.

MISSION 2 — CONTRÔLE DE COMPLÉTUDE : c'est ta mission la plus critique. Compare l'article aux sources d'actualité pour détecter les INFORMATIONS IMPORTANTES MANQUANTES. Un article factuellement juste mais qui omet une évolution majeure du sujet est trompeur pour le lecteur. Exemples d'omissions graves : un dispositif/produit/travaux qui a été supprimé ou ajouté récemment, un changement de conditions ou de règles, un événement récent qui change la donne, une exclusion nouvelle.

MISSION 3 — CORRECTION : produire une version corrigée de l'article qui :
- Corrige les erreurs factuelles détectées
- INTÈGRE les informations manquantes importantes (en les insérant naturellement dans les sections existantes, pas en ajoutant un bloc fourre-tout)
- Reformule les affirmations douteuses avec prudence

PRINCIPES :
- EXHAUSTIF sur les faits ET les omissions
- CONSERVATEUR sur le style : ne touche qu'au fond factuel, jamais au ton ni à la structure
- Pour les ajouts de complétude, insère-les dans la section la plus pertinente, dans le même style que l'auteur

RÈGLE SPÉCIALE CHIFFRES ET DONNÉES :
- Pour chaque donnée chiffrée de l'article (barème, seuil, plafond, montant, pourcentage, date), vérifie qu'elle apparaît EXACTEMENT et TEXTUELLEMENT dans au moins une source.
- Un chiffre "proche", "plausible" ou "cohérent avec une revalorisation" n'est PAS confirmé. Marque-le ❌ INEXACT ou ⚠️ NON SOURCÉ.
- Si un chiffre de l'article diffère même légèrement d'une source (ex : 17 363 € dans l'article vs 17 173 € dans la source), c'est une ERREUR, pas un arrondi acceptable.
- Dans la version corrigée, remplace les chiffres non confirmés par une formulation qui renvoie à la source officielle, ou par le chiffre exact trouvé dans les sources. Ne laisse JAMAIS un chiffre douteux dans l'article corrigé.

RÈGLE SPÉCIALE LISTES, CATÉGORIES ET EXCLUSIONS :
- Quand l'article liste des éléments éligibles, autorisés ou inclus dans une catégorie (travaux, profils, bénéficiaires, produits...), vérifie que CHAQUE ITEM de la liste appartient bien à cette catégorie dans les sources. Un item qui appartient à une catégorie voisine est une ERREUR.
- Vérifie les EXCLUSIONS : si les sources indiquent que certains profils, publics ou cas sont exclus d'un dispositif, d'une offre ou d'une catégorie, et que l'article ne le mentionne pas, c'est une OMISSION MAJEURE. Un lecteur qui croit être éligible alors qu'il ne l'est pas subira un refus de dossier.
- Vérifie la COHÉRENCE INTERNE : si l'article dit dans un paragraphe qu'un élément est exclu, puis le liste comme éligible dans un autre paragraphe, c'est une ERREUR à signaler et corriger.
- Si l'article affirme qu'une règle a changé (ex : "passé de X à Y en 2026"), vérifie que ce changement est confirmé dans les sources. Une évolution inventée est aussi grave qu'un chiffre inventé."""

    user_prompt = f"""Voici un article sur "{keyword}". Vérifie-le contre les sources d'actualité ci-dessous, contrôle sa complétude, puis produis la version corrigée.

## ARTICLE À VÉRIFIER :
{article}

## SOURCES DE VÉRIFICATION (SERP + Google Actualités) :
{sources_context}

{f"Note : le style de l'article suit un persona éditorial spécifique. Respecte-le dans la version corrigée : {custom_instructions}" if custom_instructions else ""}

## FORMAT DE RÉPONSE — DEUX BLOCS OBLIGATOIRES :

===RAPPORT===

### SCORE GLOBAL
[X/10] — [une phrase résumant la fiabilité ET la complétude. Un article juste mais très incomplet ne peut pas dépasser 6/10]

### AFFIRMATIONS VÉRIFIÉES
Pour chaque affirmation factuelle :

✅ **CONFIRMÉ** — "[affirmation]"
→ Source [N] : [explication courte]

⚠️ **NON SOURCÉ** — "[affirmation]"
→ [plausible / douteuse / invérifiable]. Action : [conservé / reformulé / retiré]

❌ **INEXACT** — "[affirmation]"
→ Les sources indiquent : [fait réel + référence]
→ Correction appliquée : [description]

### OMISSIONS DÉTECTÉES
Pour chaque information importante dans les sources MAIS ABSENTE de l'article :

🔴 **OMISSION MAJEURE** — "[info manquante]"
→ Source [N] — [pourquoi c'est important pour le lecteur]
→ Action : [où et comment l'info a été intégrée dans l'article corrigé]

🟡 **OMISSION MINEURE** — "[info manquante]"
→ Source [N] — [explication]
→ Action : [ajouté / ignoré car secondaire]

Si aucune omission détectée : "Aucune omission significative détectée."

### CHIFFRES ET DONNÉES
| Donnée dans l'article | Statut | Source | Action |
|---|---|---|---|

### RÉSUMÉ DES CORRECTIONS
[Liste numérotée de TOUTES les modifications : corrections + ajouts de complétude]

===ARTICLE_CORRIGÉ===

[L'article complet corrigé et complété. Même formatage Markdown. Si rien à corriger, reproduis l'article tel quel.]"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        temperature=0.15,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system=system_prompt
    )
    
    result = response.content[0].text
    
    # Séparer le rapport et l'article corrigé
    report = ""
    corrected_article = ""
    
    if "===ARTICLE_CORRIGÉ===" in result:
        parts = result.split("===ARTICLE_CORRIGÉ===")
        report = parts[0].replace("===RAPPORT===", "").strip()
        corrected_article = parts[1].strip()
    elif "===ARTICLE_CORRIGE===" in result:
        parts = result.split("===ARTICLE_CORRIGE===")
        report = parts[0].replace("===RAPPORT===", "").strip()
        corrected_article = parts[1].strip()
    else:
        # Fallback : essayer de trouver une séparation
        report = result
        corrected_article = ""
    
    return report, corrected_article


def parse_fact_check_score(fc_result: str) -> Tuple[int, str, str]:
    """Parse le score et les compteurs du fact-check"""
    score = -1
    score_class = "fc-score-medium"
    
    score_match = re.search(r'(\d+)\s*/\s*10', fc_result)
    if score_match:
        score = int(score_match.group(1))
        if score >= 8:
            score_class = "fc-score-good"
        elif score >= 5:
            score_class = "fc-score-medium"
        else:
            score_class = "fc-score-bad"
    
    confirmed = len(re.findall(r'✅', fc_result))
    unsourced = len(re.findall(r'⚠️', fc_result))
    incorrect = len(re.findall(r'❌', fc_result))
    major_omissions = len(re.findall(r'🔴', fc_result))
    minor_omissions = len(re.findall(r'🟡', fc_result))
    
    parts = [
        f"{confirmed} confirmé{'s' if confirmed > 1 else ''}",
        f"{unsourced} non sourcé{'s' if unsourced > 1 else ''}",
        f"{incorrect} inexact{'s' if incorrect > 1 else ''}",
    ]
    if major_omissions > 0:
        parts.append(f"{major_omissions} omission{'s' if major_omissions > 1 else ''} majeure{'s' if major_omissions > 1 else ''}")
    if minor_omissions > 0:
        parts.append(f"{minor_omissions} omission{'s' if minor_omissions > 1 else ''} mineure{'s' if minor_omissions > 1 else ''}")
    
    score_line = " · ".join(parts)
    
    return score, score_class, score_line


def count_corrections(fc_report: str) -> int:
    """Compte le nombre de corrections et omissions détectées"""
    errors = len(re.findall(r'❌', fc_report))
    reformulated = len(re.findall(r'reformulé', fc_report, re.IGNORECASE))
    removed = len(re.findall(r'retiré', fc_report, re.IGNORECASE))
    # Compter les omissions majeures ajoutées
    major_omissions = len(re.findall(r'🔴', fc_report))
    return errors + reformulated + removed + major_omissions


# ============================================
# INTERFACE PRINCIPALE
# ============================================

# Header
st.markdown("""
<div class="app-header">
    <h1>✨ Discover Writer</h1>
    <p>Génère des articles optimisés pour Google Discover en quelques clics</p>
</div>
""", unsafe_allow_html=True)

# Configuration API (masquée si déjà configurée via secrets)
if not st.session_state.get('api_configured', False):
    with st.expander("⚙️ Configuration API", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            anthropic_key = st.text_input(
                "Clé API Anthropic",
                type="password",
                value=st.session_state.get('anthropic_key', ''),
                help="Récupère ta clé sur console.anthropic.com"
            )
        with col2:
            serper_key = st.text_input(
                "Clé API Serper",
                type="password",
                value=st.session_state.get('serper_key', ''),
                help="Récupère ta clé sur serper.dev (gratuit pour commencer)"
            )
        
        if anthropic_key and serper_key:
            st.session_state['anthropic_key'] = anthropic_key
            st.session_state['serper_key'] = serper_key
            st.session_state['api_configured'] = True
            st.rerun()

# Titre section principale
st.markdown('<div class="card-title" style="margin-top: 0.5rem;">📝 Nouveau contenu</div>', unsafe_allow_html=True)

# Sélecteur de mode
mode = st.radio(
    "Mode de sourcing",
    ["🔍 Recherche automatique", "🔗 URLs manuelles"],
    horizontal=True,
    help="Recherche auto : trouve les meilleures sources via Google. URLs manuelles : choisis tes propres sources."
)

# Variables
keyword = ""
manual_urls = []
num_sources = 5

if mode == "🔍 Recherche automatique":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea15, #764ba215); border-left: 4px solid #667eea; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">🎯 Thème à traiter</span>
    </div>
    """, unsafe_allow_html=True)
    keyword = st.text_input(
        "Thème à traiter",
        placeholder="Ex: tendances mode été 2026, recettes healthy rapides...",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        num_sources = st.slider("Nombre de sources à analyser", min_value=3, max_value=10, value=5)
    with col2:
        pass

else:
    st.markdown("**Colle entre 2 et 5 URLs sources :**")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea15, #764ba215); border-left: 4px solid #667eea; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">🎯 Thème à traiter</span>
    </div>
    """, unsafe_allow_html=True)
    keyword = st.text_input(
        "Thème à traiter",
        placeholder="Ex: comparatif smartphones 2026, guide débutant yoga...",
        help="Indique le sujet principal pour guider la rédaction",
        label_visibility="collapsed"
    )
    
    url_inputs = []
    for i in range(5):
        url = st.text_input(
            f"URL {i+1}" + (" (obligatoire)" if i < 2 else " (optionnel)"),
            placeholder=f"https://exemple.com/article-{i+1}",
            key=f"url_{i}",
            label_visibility="visible"
        )
        if url.strip():
            url_inputs.append(url.strip())
    
    manual_urls = url_inputs

# Longueur
article_length = st.slider("📏 Longueur de l'article (en mots)", min_value=300, max_value=2000, value=800, step=100)

# Fact-checking toggle
enable_fact_check = st.checkbox(
    "🔍 Activer le fact-checking + correction automatique",
    value=True,
    help="Vérifie chaque affirmation contre les sources, puis produit une version corrigée de l'article. Ajoute ~30-45s."
)

# Persona et consignes — LE champ central pour le style
st.markdown("""
<div style="background: linear-gradient(135deg, #f59e0b15, #d9740015); border-left: 4px solid #f59e0b; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin-bottom: 0.5rem;">
    <span style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">✍️ Persona & charte éditoriale</span>
    <span style="font-size: 0.85rem; color: #64748b; margin-left: 0.5rem;">pilote le style de l'article</span>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style="background: #f8fafc; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.75rem; font-size: 0.85rem; color: #64748b;">
    💡 <strong>C'est ici que tout se joue côté style.</strong> Collez votre persona, charte éditoriale, ton, registre, niveau de détail... Ces consignes priment sur tout le reste. Sans persona, l'outil applique un style développé et expert par défaut.
</div>
""", unsafe_allow_html=True)
custom_instructions = st.text_area(
    "Persona & charte éditoriale",
    placeholder="""Ex: Tu es Marie, blogueuse food passionnée de 35 ans. Tu tutoies ton lecteur. Ton chaleureux et complice, comme si tu parlais à une copine. Phrases longues et fluides, anecdotes perso, touches d'humour. Tu donnes toujours des astuces pratiques. Niveau de détail : très développé, chaque recette/conseil est expliqué en profondeur avec des variantes.

Autre ex: Expert SEO technique. Vouvoiement. Style concis et dense, pas de fioritures. Chaque phrase apporte une info actionnable. Données chiffrées prioritaires.""",
    height=180,
    label_visibility="collapsed"
)

# Bouton de génération
generate_button = st.button("✨ Générer l'article", use_container_width=True)

# ============================================
# LOGIQUE DE GÉNÉRATION
# ============================================

if generate_button:
    # Vérifications
    if mode == "🔍 Recherche automatique":
        if not st.session_state.get('anthropic_key') or not st.session_state.get('serper_key'):
            st.error("⚠️ Configure d'abord tes clés API dans les paramètres ci-dessus")
            st.stop()
        elif not keyword:
            st.warning("💡 Entre un mot-clé ou un sujet pour commencer")
            st.stop()
    else:
        if not st.session_state.get('anthropic_key'):
            st.error("⚠️ Configure d'abord ta clé API Anthropic dans les paramètres ci-dessus")
            st.stop()
        elif not keyword:
            st.warning("💡 Entre un sujet ou angle pour l'article")
            st.stop()
        elif len(manual_urls) < 2:
            st.warning("💡 Entre au moins 2 URLs sources")
            st.stop()
        invalid_urls = [u for u in manual_urls if not (u.startswith("http://") or u.startswith("https://"))]
        if invalid_urls:
            st.error(f"⚠️ URLs invalides : {', '.join(invalid_urls)}")
            st.stop()
    
    client = anthropic.Anthropic(api_key=st.session_state['anthropic_key'])
    progress_container = st.container()
    
    # === SOURCING ===
    if mode == "🔍 Recherche automatique":
        with progress_container:
            st.markdown("""
            <div class="step-indicator">
                <div class="step-dot"></div>
                <span class="step-text">Recherche des meilleures sources...</span>
            </div>
            """, unsafe_allow_html=True)
            try:
                sources = search_serper(keyword, st.session_state['serper_key'], num_sources)
                time.sleep(0.3)
            except Exception as e:
                st.error(f"Erreur lors de la recherche : {str(e)}")
                st.stop()
        
        progress_container.empty()
        with progress_container:
            st.markdown(f"""
            <div class="step-indicator">
                <div class="step-dot"></div>
                <span class="step-text">Analyse de {len(sources)} sources en cours...</span>
            </div>
            """, unsafe_allow_html=True)
            progress_bar = st.progress(0)
            contents = []
            for i, source in enumerate(sources):
                try:
                    content = fetch_content_jina(source['url'])
                    contents.append(content)
                except Exception as e:
                    contents.append(f"Contenu non disponible: {str(e)}")
                progress_bar.progress((i + 1) / len(sources))
                time.sleep(0.1)
    else:
        sources = [{"title": extract_title_from_url(url), "url": url, "snippet": ""} for url in manual_urls]
        with progress_container:
            st.markdown(f"""
            <div class="step-indicator">
                <div class="step-dot"></div>
                <span class="step-text">Analyse de {len(sources)} sources en cours...</span>
            </div>
            """, unsafe_allow_html=True)
            progress_bar = st.progress(0)
            contents = []
            for i, source in enumerate(sources):
                try:
                    content = fetch_content_jina(source['url'])
                    contents.append(content)
                    if content and not content.startswith("Erreur"):
                        first_lines = content.split('\n')[:5]
                        for line in first_lines:
                            line = line.strip()
                            if line and not line.startswith('http') and len(line) > 10 and len(line) < 200:
                                sources[i]['title'] = line[:80]
                                break
                except Exception as e:
                    contents.append(f"Contenu non disponible: {str(e)}")
                progress_bar.progress((i + 1) / len(sources))
                time.sleep(0.1)
    
    # === RÉDACTION ===
    progress_container.empty()
    with progress_container:
        st.markdown("""
        <div class="step-indicator">
            <div class="step-dot"></div>
            <span class="step-text">Rédaction de l'article...</span>
        </div>
        """, unsafe_allow_html=True)
        try:
            article = generate_article(
                client, keyword, sources, contents,
                custom_instructions, article_length
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération : {str(e)}")
            st.stop()
    
    # === FACT-CHECK + CORRECTION ===
    fc_report = None
    corrected_article = None
    news_sources_fc = None
    news_contents_fc = None
    if enable_fact_check:
        # Étape 3a : Recherche Google Actualités pour le fact-check
        if st.session_state.get('serper_key'):
            progress_container.empty()
            with progress_container:
                st.markdown("""
                <div class="step-indicator">
                    <div class="step-dot"></div>
                    <span class="step-text">Recherche de sources de vérification (SERP + Actualités)...</span>
                </div>
                """, unsafe_allow_html=True)
                try:
                    news_sources_fc, news_contents_fc = fetch_sources_for_fact_check(
                        keyword, st.session_state['serper_key']
                    )
                except Exception as e:
                    news_sources_fc = []
                    news_contents_fc = []
            
            # Étape 3b : Fact-check avec sources actu uniquement
            if news_sources_fc and len(news_sources_fc) > 0:
                progress_container.empty()
                with progress_container:
                    st.markdown(f"""
                    <div class="step-indicator">
                        <div class="step-dot"></div>
                        <span class="step-text">Vérification factuelle contre {len(news_sources_fc)} sources indépendantes...</span>
                    </div>
                    """, unsafe_allow_html=True)
                    try:
                        if "---" in article:
                            parts = article.split("---")
                            article_only = "---".join(parts[1:]).strip().replace("```", "").strip()
                        else:
                            article_only = article
                        
                        fc_report, corrected_article = fact_check_and_correct(
                            client, article_only, 
                            news_sources_fc, news_contents_fc,
                            keyword, custom_instructions
                        )
                    except Exception as e:
                        fc_report = f"⚠️ Erreur lors du fact-checking : {str(e)}"
                        corrected_article = None
            else:
                fc_report = "⚠️ Aucune source d'actualité trouvée pour le fact-checking. Vérification manuelle recommandée."
                corrected_article = None
        else:
            fc_report = "⚠️ Clé API Serper requise pour le fact-checking via Google Actualités."
            corrected_article = None
    
    # === AFFICHAGE ===
    progress_container.empty()
    
    # Parser les métadonnées
    def parse_result(result):
        meta = {"titres": [], "title_seo": "", "meta_desc": ""}
        article_content = result
        
        if "## TITRES" in result or "## TITRES (H1)" in result:
            try:
                titres_section = result.split("## TITLE SEO")[0]
                titres_section = titres_section.split("## TITRES")[-1]
                lines = [l.strip() for l in titres_section.strip().split("\n") if l.strip() and l.strip()[0].isdigit()]
                meta["titres"] = lines[:5]
            except:
                pass
        
        if "## TITLE SEO" in result:
            try:
                title_section = result.split("## TITLE SEO")[1].split("##")[0]
                meta["title_seo"] = title_section.strip().split("\n")[0].strip()
            except:
                pass
        
        if "## META DESCRIPTION" in result:
            try:
                meta_section = result.split("## META DESCRIPTION")[1].split("---")[0]
                meta["meta_desc"] = meta_section.strip().split("\n")[0].strip()
            except:
                pass
        
        if "---" in result:
            parts = result.split("---")
            if len(parts) > 1:
                article_content = "---".join(parts[1:]).strip()
                article_content = article_content.replace("```", "").strip()
        
        return meta, article_content
    
    meta, article_content = parse_result(article)
    
    # Déterminer quel article afficher en principal
    has_corrections = False
    nb_corrections = 0
    if fc_report and corrected_article:
        nb_corrections = count_corrections(fc_report)
        has_corrections = nb_corrections > 0
    
    # --- FACT-CHECK SUMMARY ---
    if fc_report and enable_fact_check:
        score, score_class, score_line = parse_fact_check_score(fc_report)
        score_display = f"{score}/10" if score >= 0 else "—"
        
        st.markdown(f"""
        <div class="fc-summary">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div class="fc-score {score_class}">{score_display}</div>
                <div>
                    <div style="font-weight: 600; color: #1e293b; font-size: 1.1rem;">🔍 Vérification factuelle</div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;">{score_line}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if has_corrections:
            st.markdown(f"""
            <div class="fc-corrections-banner">
                ✅ <strong>{nb_corrections} correction{'s' if nb_corrections > 1 else ''} appliquée{'s' if nb_corrections > 1 else ''}</strong> — L'article corrigé est affiché ci-dessous. L'original est disponible dans "Copier le contenu".
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="fc-corrections-banner">
                ✅ <strong>Aucune correction nécessaire</strong> — L'article est factuellement fiable au regard des sources.
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("📋 Voir le rapport complet de fact-checking", expanded=False):
            st.markdown(fc_report)
    
    # --- MÉTADONNÉES SEO ---
    st.markdown("""
    <div class="result-card">
        <div class="result-header">
            <span class="result-title">🎯 Métadonnées SEO</span>
            <span class="success-badge">✓ Prêt</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if meta["titres"]:
        st.markdown("**Propositions de titres H1 :**")
        for titre in meta["titres"]:
            st.markdown(f"- {titre}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Title SEO :**")
        if meta["title_seo"]:
            st.code(meta["title_seo"], language=None)
        else:
            st.info("Non détecté")
    with col2:
        st.markdown("**Meta Description :**")
        if meta["meta_desc"]:
            st.code(meta["meta_desc"], language=None)
        else:
            st.info("Non détectée")
    
    st.markdown("---")
    
    # --- ARTICLE (corrigé si dispo, sinon original) ---
    display_article = corrected_article if (has_corrections and corrected_article) else article_content
    display_label = "corrigé" if has_corrections else "original"
    
    word_count = len(display_article.split())
    
    if abs(word_count - article_length) <= article_length * 0.15:
        count_color = "#10b981"
        count_label = "✓"
    elif word_count > article_length:
        count_color = "#f59e0b"
        count_label = "⚠ long"
    else:
        count_color = "#f59e0b"
        count_label = "⚠ court"
    
    version_badge = ""
    if has_corrections:
        version_badge = '<span style="background: #10b981; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">✓ Corrigé</span>'
    
    st.markdown(f"""
    <div class="result-card">
        <div class="result-header">
            <span class="result-title">📄 Article</span>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                {version_badge}
                <span style="background: {count_color}; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">{word_count} mots {count_label}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(display_article)
    
    # Sources utilisées
    st.markdown("---")
    st.markdown("**📚 Sources de rédaction :**")
    for i, source in enumerate(sources, 1):
        st.markdown(f"{i}. **{source['title'][:60]}**  \n`{source['url']}`")
    
    # Sources fact-check
    if news_sources_fc and len(news_sources_fc) > 0:
        st.markdown("")
        st.markdown("**📰 Sources de vérification (fact-check) :**")
        for i, ns in enumerate(news_sources_fc, 1):
            date_tag = f" — {ns.get('date', '')}" if ns.get('date') else ""
            type_icon = "🔍" if ns.get('source_type') == 'serp' else "📰"
            st.markdown(f"{i}. {type_icon} **{ns['title'][:60]}**{date_tag}  \n`{ns['url']}`")
    
    # Copier le contenu
    with st.expander("📋 Copier le contenu"):
        if has_corrections and corrected_article:
            tab1, tab2, tab3, tab4 = st.tabs(["Article corrigé", "Article original", "Tout (méta + corrigé)", "Rapport fact-check"])
            with tab1:
                st.code(corrected_article, language="markdown")
            with tab2:
                st.code(article_content, language="markdown")
            with tab3:
                # Recombiner métadonnées + article corrigé
                meta_part = article.split("---")[0] if "---" in article else ""
                full_corrected = f"{meta_part}---\n\n{corrected_article}" if meta_part else corrected_article
                st.code(full_corrected, language="markdown")
            with tab4:
                st.code(fc_report if fc_report else "Fact-checking non disponible", language="markdown")
        else:
            tab1, tab2, tab3 = st.tabs(["Article seul", "Tout (méta + article)", "Rapport fact-check"])
            with tab1:
                st.code(article_content, language="markdown")
            with tab2:
                st.code(article, language="markdown")
            with tab3:
                if fc_report:
                    st.code(fc_report, language="markdown")
                else:
                    st.info("Fact-checking non activé pour cette génération")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: #94a3b8; font-size: 0.85rem;">
    Propulsé par Claude API & Serper • Made with 💜
</div>
""", unsafe_allow_html=True)
