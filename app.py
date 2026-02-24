import streamlit as st
import requests
import json
import anthropic
from typing import List, Dict
import time

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


def fetch_content_jina(url: str) -> str:
    """Récupère le contenu d'une page via Jina Reader (gratuit)"""
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "Accept": "text/plain"
    }
    
    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()
        # Limiter la taille du contenu
        content = response.text[:15000]
        return content
    except Exception as e:
        return f"Erreur lors de la récupération: {str(e)}"


def extract_title_from_url(url: str) -> str:
    """Extrait un titre simple depuis l'URL"""
    # Enlever le protocole et www
    title = url.replace("https://", "").replace("http://", "").replace("www.", "")
    # Prendre le domaine + début du path
    parts = title.split("/")
    if len(parts) > 1 and parts[1]:
        return f"{parts[0]} - {parts[1][:30]}"
    return parts[0]


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
{content[:8000]}

"""
    
    system_prompt = f"""Tu es un rédacteur web senior avec 15 ans d'expérience. Tu écris comme un humain, pas comme une IA. Tes textes sont fluides, chaleureux et agréables à lire.

## RÈGLE N°1 : PERSONA ET CONSIGNES DE L'UTILISATEUR

Si l'utilisateur fournit des instructions de style, un persona, une charte éditoriale ou un ton spécifique, c'est ta PRIORITÉ ABSOLUE. Tu adoptes ce ton et ce style à 100%, il prime sur toutes les autres consignes ci-dessous.

## RÈGLE N°2 : VARIANCE STRUCTURELLE

Un humain n'écrit jamais des sections de longueur identique. Tu dois :

- Varier la longueur des sections : certaines font 2-3 phrases, d'autres 8-10
- Varier la longueur des paragraphes : alterne entre paragraphes courts et plus développés
- Ne commence jamais deux H2 consécutifs de la même façon (question, affirmation, chiffre, anecdote...)
- Varie le formatage entre sections : prose seule, puis une liste, puis un tableau si pertinent

INTERDIT : que deux sections consécutives aient la même structure interne.

## FLUIDITÉ ET TRANSITIONS

C'est essentiel. Ton texte doit COULER naturellement d'une idée à l'autre :

- Chaque paragraphe doit s'enchaîner logiquement avec le précédent. Le lecteur ne doit jamais sentir de rupture brutale.
- Utilise des transitions variées et naturelles : reformulations-ponts ("Ce qui explique pourquoi...", "Et c'est précisément là que..."), rebonds sur l'idée précédente, questions qui amènent la suite.
- Alterne entre transitions explicites et enchaînements implicites (parfois le lien logique suffit, pas besoin de connecteur).
- Évite les connecteurs mécaniques répétitifs. Varie : "D'autant que", "Résultat", "Le hic", "Autre point notable", "Ce qui change la donne", "Côté pratique", "Et pour cause"...
- Les fins de section doivent donner envie de lire la suite, pas tomber à plat.

## ACCROCHE

- Ancrage contextuel dès la première phrase (actualité, tendance, chiffre marquant, saison...)
- Le lecteur doit comprendre pourquoi lire ça MAINTENANT
- Pas d'intro bateau de type "Le [sujet] est devenu incontournable ces dernières années"

## RYTHME ET STYLE

- Écris avec un style incarné et engageant, comme un expert passionné qui s'adresse à son lecteur
- Mélange phrases courtes et phrases plus développées pour créer du rythme, mais ne sacrifie jamais la fluidité pour la brièveté
- Le texte doit se lire à voix haute sans accrocher. Si une phrase sonne mécanique ou hachée, reformule-la.
- Ajoute de la couleur : comparaisons, métaphores légères, touches d'humour quand le sujet s'y prête
- Questions rhétoriques avec parcimonie (1-2 max dans tout l'article)

## FORMATAGE

- **Gras** sur les mots-clés stratégiques uniquement (pas les phrases entières)
- Listes à puces UNIQUEMENT pour les énumérations concrètes, et PAS dans chaque section
- Tableau Markdown UNIQUEMENT si données chiffrées comparables
- En cas de doute entre liste et prose → prose

## ENRICHISSEMENT SÉMANTIQUE

- Intègre naturellement les entités liées au sujet (personnes, lieux, marques, concepts techniques)
- Données chiffrées quand disponibles
- Montre une expertise qui va au-delà des mots-clés évidents

## TON

- Expert mais chaleureux et accessible, jamais scolaire ni robotique
- Vouvoiement naturel
- Le lecteur doit sentir qu'un humain passionné lui parle, pas qu'une machine débite des infos
- Conclusion mémorable (jamais "En conclusion...", "Pour résumer...", "En définitive...")

## LONGUEUR

L'article doit faire environ {article_length} mots. C'est une cible, pas un minimum à atteindre coûte que coûte. Si le sujet est couvert en moins, arrête-toi. Ne remplis JAMAIS pour atteindre une longueur.

## À BANNIR ABSOLUMENT

- Tournures IA : "Il est important de noter", "Dans cet article", "N'hésitez pas", "Il convient de", "Force est de constater", "À l'heure où"
- Style télégraphique froid : ne hache pas les phrases au point de perdre la fluidité
- Structures symétriques (3 sections de même taille, 3 paragraphes miroirs)
- Intros génériques sans accroche
- Remplissage et reformulations qui n'apportent rien
- Liens et URLs : jamais de [texte](url), jamais d'URL brute, jamais de "source" cliquable
- Commencer un paragraphe par "Il est" ou "Il faut"
- Utiliser "Certes... mais" plus d'une fois dans un article
- Enchaîner des phrases sans lien logique entre elles

## CONTEXTE TEMPOREL

Nous sommes en 2026. Adapte toutes les références temporelles en conséquence. Ne mentionne jamais 2025 comme étant l'année en cours."""

    user_prompt = f"""Analyse ces {len(sources)} sources sur "{keyword}" et rédige un article optimisé Discover.

{sources_context}

CONSIGNES :
1. Identifie les infos clés, données chiffrées, angles différenciants
2. Repère les entités importantes à intégrer (personnes, marques, concepts...)

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

{f"Instructions supplémentaires : {custom_instructions}" if custom_instructions else ""}

CONTRAINTE DE LONGUEUR : L'article (hors métadonnées) doit faire environ {article_length} mots. Vise cette cible précisément. Si tu es au-dessus, coupe. Si tu es en dessous sans remplissage possible, c'est OK.

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
        max_tokens=5000,
        temperature=0.7,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system=system_prompt
    )
    
    return response.content[0].text


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

# Variables pour stocker les inputs selon le mode
keyword = ""
manual_urls = []
num_sources = 5

if mode == "🔍 Recherche automatique":
    # Mode recherche : input topic + slider nombre de sources
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
        pass  # Espace pour équilibrer

else:
    # Mode URLs manuelles
    st.markdown("**Colle entre 2 et 5 URLs sources :**")
    
    # Sujet/angle pour l'article (obligatoire en mode manuel)
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
    
    # Champs URLs dynamiques
    url_inputs = []
    for i in range(5):
        url = st.text_input(
            f"URL {i+1}" + (" (obligatoire)" if i < 2 else " (optionnel)"),
            placeholder=f"https://exemple.com/article-{i+1}",
            key=f"url_{i}",
            label_visibility="visible" if i < 2 else "visible"
        )
        if url.strip():
            url_inputs.append(url.strip())
    
    manual_urls = url_inputs

# Longueur de l'article - commun aux deux modes
article_length = st.slider("📏 Longueur de l'article (en mots)", min_value=300, max_value=2000, value=800, step=100)

# Persona et consignes complémentaires - commun aux deux modes
st.markdown("""
<div style="background: linear-gradient(135deg, #f59e0b15, #d9740015); border-left: 4px solid #f59e0b; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin-bottom: 0.5rem;">
    <span style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">✍️ Persona et consignes complémentaires</span>
    <span style="font-size: 0.85rem; color: #64748b; margin-left: 0.5rem;">optionnel</span>
</div>
""", unsafe_allow_html=True)
custom_instructions = st.text_area(
    "Persona et consignes complémentaires",
    placeholder="Ex: Tu es un expert nutrition sportive. Ton décontracté, tutoiement, mentionner les prix...",
    height=100,
    label_visibility="collapsed"
)


# Bouton de génération
generate_button = st.button("✨ Générer l'article", use_container_width=True)

# ============================================
# LOGIQUE DE GÉNÉRATION
# ============================================

if generate_button:
    # Vérifications selon le mode
    if mode == "🔍 Recherche automatique":
        if not st.session_state.get('anthropic_key') or not st.session_state.get('serper_key'):
            st.error("⚠️ Configure d'abord tes clés API dans les paramètres ci-dessus")
            st.stop()
        elif not keyword:
            st.warning("💡 Entre un mot-clé ou un sujet pour commencer")
            st.stop()
    else:
        # Mode URLs manuelles
        if not st.session_state.get('anthropic_key'):
            st.error("⚠️ Configure d'abord ta clé API Anthropic dans les paramètres ci-dessus")
            st.stop()
        elif not keyword:
            st.warning("💡 Entre un sujet ou angle pour l'article")
            st.stop()
        elif len(manual_urls) < 2:
            st.warning("💡 Entre au moins 2 URLs sources")
            st.stop()
        # Validation basique des URLs
        invalid_urls = [u for u in manual_urls if not (u.startswith("http://") or u.startswith("https://"))]
        if invalid_urls:
            st.error(f"⚠️ URLs invalides (doivent commencer par http:// ou https://) : {', '.join(invalid_urls)}")
            st.stop()
    
    # Initialiser le client Anthropic
    client = anthropic.Anthropic(api_key=st.session_state['anthropic_key'])
    
    # Container pour les étapes
    progress_container = st.container()
    
    if mode == "🔍 Recherche automatique":
        # === MODE RECHERCHE AUTOMATIQUE ===
        with progress_container:
            # Étape 1 : Recherche
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
        
        # Clear et afficher étape 2
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
        # === MODE URLs MANUELLES ===
        # Construire la liste des sources à partir des URLs
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
                    # Mettre à jour le titre avec celui extrait du contenu si possible
                    if content and not content.startswith("Erreur"):
                        # Essayer d'extraire le titre du contenu Jina (généralement en première ligne)
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
    
    # Clear et afficher étape génération (commun aux deux modes)
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
                client,
                keyword,
                sources,
                contents,
                custom_instructions,
                article_length
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération : {str(e)}")
            st.stop()
    
    # Clear progress et afficher résultat
    progress_container.empty()
    
    # Parser le résultat pour séparer métadonnées et article
    def parse_result(result):
        """Sépare les métadonnées SEO de l'article"""
        meta = {"titres": [], "title_seo": "", "meta_desc": ""}
        article_content = result
        
        # Extraire les titres H1
        if "## TITRES" in result or "## TITRES (H1)" in result:
            try:
                titres_section = result.split("## TITLE SEO")[0]
                titres_section = titres_section.split("## TITRES")[-1]
                lines = [l.strip() for l in titres_section.strip().split("\n") if l.strip() and l.strip()[0].isdigit()]
                meta["titres"] = lines[:5]
            except:
                pass
        
        # Extraire le title SEO
        if "## TITLE SEO" in result:
            try:
                title_section = result.split("## TITLE SEO")[1].split("##")[0]
                meta["title_seo"] = title_section.strip().split("\n")[0].strip()
            except:
                pass
        
        # Extraire la meta description
        if "## META DESCRIPTION" in result:
            try:
                meta_section = result.split("## META DESCRIPTION")[1].split("---")[0]
                meta["meta_desc"] = meta_section.strip().split("\n")[0].strip()
            except:
                pass
        
        # Extraire l'article (après le ---)
        if "---" in result:
            parts = result.split("---")
            if len(parts) > 1:
                article_content = "---".join(parts[1:]).strip()
                # Nettoyer les éventuels ``` résiduels
                article_content = article_content.replace("```", "").strip()
        
        return meta, article_content
    
    meta, article_content = parse_result(article)
    
    # Affichage des métadonnées SEO
    st.markdown("""
    <div class="result-card">
        <div class="result-header">
            <span class="result-title">🎯 Métadonnées SEO</span>
            <span class="success-badge">✓ Prêt</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Titres H1
    if meta["titres"]:
        st.markdown("**Propositions de titres H1 :**")
        for titre in meta["titres"]:
            st.markdown(f"- {titre}")
    
    # Title SEO et Meta Description côte à côte
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
    
    # Affichage de l'article avec compteur de mots
    word_count = len(article_content.split())
    
    # Couleur du badge selon écart à la cible
    if abs(word_count - article_length) <= article_length * 0.15:
        count_color = "#10b981"  # vert
        count_label = "✓"
    elif word_count > article_length:
        count_color = "#f59e0b"  # orange
        count_label = "⚠ long"
    else:
        count_color = "#f59e0b"  # orange
        count_label = "⚠ court"
    
    st.markdown(f"""
    <div class="result-card">
        <div class="result-header">
            <span class="result-title">📄 Article</span>
            <span style="background: {count_color}; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">{word_count} mots {count_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(article_content)
    
    # Sources utilisées
    st.markdown("---")
    st.markdown("**Sources analysées :**")
    sources_html = ""
    for source in sources:
        sources_html += f'<span class="source-pill">{source["title"][:40]}...</span>'
    st.markdown(f'<div style="margin-top: 0.5rem;">{sources_html}</div>', unsafe_allow_html=True)
    
    # Boutons copier
    with st.expander("📋 Copier le contenu"):
        tab1, tab2 = st.tabs(["Article seul", "Tout (métadonnées + article)"])
        with tab1:
            st.code(article_content, language="markdown")
        with tab2:
            st.code(article, language="markdown")

# Footer discret
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: #94a3b8; font-size: 0.85rem;">
    Propulsé par Claude API & Serper • Made with 💜
</div>
""", unsafe_allow_html=True)
