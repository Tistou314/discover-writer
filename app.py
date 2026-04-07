"""Discover Writer — Interface Streamlit."""

import streamlit as st
import anthropic
import time

from config import CSS, APP_TITLE, APP_ICON, APP_SUBTITLE
from sources import search_serper, fetch_content_jina, extract_title_from_url, fetch_sources_for_fact_check
from generator import generate_article
from fact_checker import fact_check_and_correct, parse_fact_check_score, count_corrections
from utils import parse_article_result, extract_article_only

# ============================================
# INIT
# ============================================

if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
    st.session_state['anthropic_key'] = st.secrets['ANTHROPIC_API_KEY']
    st.session_state['serper_key'] = st.secrets['SERPER_API_KEY']
    st.session_state['api_configured'] = True

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="centered", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================

st.markdown(f"""
<div class="app-header">
    <h1>{APP_ICON} {APP_TITLE}</h1>
    <p>{APP_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# CONFIG API
# ============================================

if not st.session_state.get('api_configured', False):
    with st.expander("⚙️ Configuration API", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            anthropic_key = st.text_input("Clé API Anthropic", type="password", value=st.session_state.get('anthropic_key', ''), help="console.anthropic.com")
        with col2:
            serper_key = st.text_input("Clé API Serper", type="password", value=st.session_state.get('serper_key', ''), help="serper.dev")
        if anthropic_key and serper_key:
            st.session_state['anthropic_key'] = anthropic_key
            st.session_state['serper_key'] = serper_key
            st.session_state['api_configured'] = True
            st.rerun()

# ============================================
# FORMULAIRE
# ============================================

st.markdown('<div class="card-title" style="margin-top: 0.5rem;">📝 Nouveau contenu</div>', unsafe_allow_html=True)

mode = st.radio("Mode de sourcing", ["🔍 Recherche automatique", "🔗 URLs manuelles"], horizontal=True,
                help="Recherche auto : trouve les meilleures sources via Google. URLs manuelles : choisis tes propres sources.")

keyword = ""
manual_urls = []
num_sources = 5

if mode == "🔍 Recherche automatique":
    st.markdown("""<div style="background: linear-gradient(135deg, #667eea15, #764ba215); border-left: 4px solid #667eea; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">🎯 Thème à traiter</span></div>""", unsafe_allow_html=True)
    keyword = st.text_input("Thème", placeholder="Ex: tendances mode été 2026, recettes healthy rapides...", label_visibility="collapsed")
    col1, col2 = st.columns(2)
    with col1:
        num_sources = st.slider("Nombre de sources à analyser", min_value=3, max_value=10, value=5)
else:
    st.markdown("**Colle entre 2 et 5 URLs sources :**")
    st.markdown("""<div style="background: linear-gradient(135deg, #667eea15, #764ba215); border-left: 4px solid #667eea; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">🎯 Thème à traiter</span></div>""", unsafe_allow_html=True)
    keyword = st.text_input("Thème", placeholder="Ex: comparatif smartphones 2026...", help="Sujet principal", label_visibility="collapsed")
    url_inputs = []
    for i in range(5):
        url = st.text_input(f"URL {i+1}" + (" (obligatoire)" if i < 2 else " (optionnel)"), placeholder=f"https://exemple.com/article-{i+1}", key=f"url_{i}")
        if url.strip():
            url_inputs.append(url.strip())
    manual_urls = url_inputs

article_length = st.slider("📏 Longueur de l'article (en mots)", min_value=300, max_value=2000, value=800, step=100)

enable_fact_check = st.checkbox("🔍 Activer le fact-checking + correction automatique", value=True,
                                help="Vérifie chaque affirmation contre des sources indépendantes. Ajoute ~30-45s.")

st.markdown("""<div style="background: linear-gradient(135deg, #f59e0b15, #d9740015); border-left: 4px solid #f59e0b; border-radius: 0 12px 12px 0; padding: 1rem 1.25rem; margin-bottom: 0.5rem;">
    <span style="font-size: 1.1rem; font-weight: 600; color: #1e293b;">✍️ Persona & charte éditoriale</span>
    <span style="font-size: 0.85rem; color: #64748b; margin-left: 0.5rem;">pilote le style de l'article</span></div>""", unsafe_allow_html=True)
st.markdown("""<div style="background: #f8fafc; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.75rem; font-size: 0.85rem; color: #64748b;">
    💡 <strong>C'est ici que tout se joue côté style.</strong> Collez votre persona, charte éditoriale, ton, registre... Ces consignes priment sur tout le reste.</div>""", unsafe_allow_html=True)
custom_instructions = st.text_area("Persona", placeholder="Ex: Tu es Marie, blogueuse food. Tutoiement, ton chaleureux...", height=180, label_visibility="collapsed")

generate_button = st.button("✨ Générer l'article", use_container_width=True)

# ============================================
# GÉNÉRATION
# ============================================

if generate_button:
    # Validations
    if mode == "🔍 Recherche automatique":
        if not st.session_state.get('anthropic_key') or not st.session_state.get('serper_key'):
            st.error("⚠️ Configure d'abord tes clés API"); st.stop()
        elif not keyword:
            st.warning("💡 Entre un mot-clé ou un sujet"); st.stop()
    else:
        if not st.session_state.get('anthropic_key'):
            st.error("⚠️ Configure d'abord ta clé API Anthropic"); st.stop()
        elif not keyword:
            st.warning("💡 Entre un sujet"); st.stop()
        elif len(manual_urls) < 2:
            st.warning("💡 Entre au moins 2 URLs"); st.stop()
        invalid = [u for u in manual_urls if not (u.startswith("http://") or u.startswith("https://"))]
        if invalid:
            st.error(f"⚠️ URLs invalides : {', '.join(invalid)}"); st.stop()

    client = anthropic.Anthropic(api_key=st.session_state['anthropic_key'])
    progress = st.container()

    # --- SOURCING ---
    if mode == "🔍 Recherche automatique":
        with progress:
            st.markdown('<div class="step-indicator"><div class="step-dot"></div><span class="step-text">Recherche des meilleures sources...</span></div>', unsafe_allow_html=True)
            try:
                sources = search_serper(keyword, st.session_state['serper_key'], num_sources)
            except Exception as e:
                st.error(f"Erreur recherche : {e}"); st.stop()
        progress.empty()
        with progress:
            st.markdown(f'<div class="step-indicator"><div class="step-dot"></div><span class="step-text">Analyse de {len(sources)} sources...</span></div>', unsafe_allow_html=True)
            bar = st.progress(0)
            contents = []
            for i, source in enumerate(sources):
                try:
                    contents.append(fetch_content_jina(source['url']))
                except Exception as e:
                    contents.append(f"Contenu non disponible: {e}")
                bar.progress((i + 1) / len(sources))
    else:
        sources = [{"title": extract_title_from_url(url), "url": url, "snippet": ""} for url in manual_urls]
        with progress:
            st.markdown(f'<div class="step-indicator"><div class="step-dot"></div><span class="step-text">Analyse de {len(sources)} sources...</span></div>', unsafe_allow_html=True)
            bar = st.progress(0)
            contents = []
            for i, source in enumerate(sources):
                try:
                    content = fetch_content_jina(source['url'])
                    contents.append(content)
                    if content and not content.startswith("Erreur"):
                        for line in content.split('\n')[:5]:
                            line = line.strip()
                            if line and not line.startswith('http') and 10 < len(line) < 200:
                                sources[i]['title'] = line[:80]; break
                except Exception as e:
                    contents.append(f"Contenu non disponible: {e}")
                bar.progress((i + 1) / len(sources))

    # --- RÉDACTION ---
    progress.empty()
    with progress:
        st.markdown('<div class="step-indicator"><div class="step-dot"></div><span class="step-text">Rédaction de l\'article...</span></div>', unsafe_allow_html=True)
        try:
            article = generate_article(client, keyword, sources, contents, custom_instructions, article_length)
        except Exception as e:
            st.error(f"Erreur génération : {e}"); st.stop()

    # --- FACT-CHECK ---
    fc_report = None
    corrected_article = None
    fc_sources = None
    if enable_fact_check and st.session_state.get('serper_key'):
        progress.empty()
        with progress:
            st.markdown('<div class="step-indicator"><div class="step-dot"></div><span class="step-text">Recherche de sources de vérification (SERP + Actualités)...</span></div>', unsafe_allow_html=True)
            try:
                fc_sources, fc_contents = fetch_sources_for_fact_check(keyword, st.session_state['serper_key'])
            except Exception:
                fc_sources, fc_contents = [], []

        if fc_sources:
            progress.empty()
            with progress:
                st.markdown(f'<div class="step-indicator"><div class="step-dot"></div><span class="step-text">Vérification factuelle contre {len(fc_sources)} sources indépendantes...</span></div>', unsafe_allow_html=True)
                try:
                    article_only = extract_article_only(article)
                    fc_report, corrected_article = fact_check_and_correct(client, article_only, fc_sources, fc_contents, keyword, custom_instructions)
                except Exception as e:
                    fc_report = f"⚠️ Erreur fact-checking : {e}"
                    corrected_article = None

    # --- AFFICHAGE ---
    progress.empty()
    meta, article_content = parse_article_result(article)

    has_corrections = False
    nb_corrections = 0
    if fc_report and corrected_article:
        nb_corrections = count_corrections(fc_report)
        has_corrections = nb_corrections > 0

    # Fact-check summary
    if fc_report and enable_fact_check:
        score, score_class, score_line = parse_fact_check_score(fc_report)
        if has_corrections:
            st.markdown(f"""<div class="fc-summary"><div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="font-size: 2rem;">✅</div><div>
                <div style="font-weight: 600; color: #1e293b; font-size: 1.1rem;">Article vérifié et corrigé automatiquement</div>
                <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;">{nb_corrections} correction{'s' if nb_corrections > 1 else ''} appliquée{'s' if nb_corrections > 1 else ''} · {score_line}</div>
                </div></div></div>""", unsafe_allow_html=True)
            st.markdown("""<div class="fc-corrections-banner">💡 <strong>L'article ci-dessous intègre déjà toutes les corrections.</strong> Le rapport détaillé liste ce qui a été modifié par rapport à la version initiale.</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="fc-summary"><div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="font-size: 2rem;">✅</div><div>
                <div style="font-weight: 600; color: #1e293b; font-size: 1.1rem;">Article vérifié, aucune correction nécessaire</div>
                <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;">{score_line}</div>
                </div></div></div>""", unsafe_allow_html=True)
        with st.expander("📋 Voir le détail des vérifications et corrections apportées", expanded=False):
            st.markdown(fc_report)

    # Métadonnées SEO
    st.markdown("""<div class="result-card"><div class="result-header">
        <span class="result-title">🎯 Métadonnées SEO</span>
        <span class="success-badge">✓ Prêt</span></div></div>""", unsafe_allow_html=True)
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

    # Article
    display_article = corrected_article if (has_corrections and corrected_article) else article_content
    word_count = len(display_article.split())
    if abs(word_count - article_length) <= article_length * 0.15:
        count_color, count_label = "#10b981", "✓"
    elif word_count > article_length:
        count_color, count_label = "#f59e0b", "⚠ long"
    else:
        count_color, count_label = "#f59e0b", "⚠ court"

    version_badge = '<span style="background: #10b981; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">✓ Corrigé</span>' if has_corrections else ""
    st.markdown(f"""<div class="result-card"><div class="result-header">
        <span class="result-title">📄 Article</span>
        <div style="display: flex; gap: 0.5rem; align-items: center;">{version_badge}
        <span style="background: {count_color}; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">{word_count} mots {count_label}</span>
        </div></div></div>""", unsafe_allow_html=True)
    st.markdown(display_article)

    # Sources
    st.markdown("---")
    st.markdown("**📚 Sources de rédaction :**")
    for i, source in enumerate(sources, 1):
        st.markdown(f"{i}. **{source['title'][:60]}**  \n`{source['url']}`")

    if fc_sources and len(fc_sources) > 0:
        st.markdown("")
        st.markdown("**📰 Sources de vérification (fact-check) :**")
        for i, ns in enumerate(fc_sources, 1):
            date_tag = f" — {ns.get('date', '')}" if ns.get('date') else ""
            icon = "🔍" if ns.get('source_type') == 'serp' else "📰"
            st.markdown(f"{i}. {icon} **{ns['title'][:60]}**{date_tag}  \n`{ns['url']}`")

    # Copier
    with st.expander("📋 Copier le contenu"):
        if has_corrections and corrected_article:
            tab1, tab2, tab3, tab4 = st.tabs(["Article corrigé", "Article original", "Tout (méta + corrigé)", "Rapport fact-check"])
            with tab1: st.code(corrected_article, language="markdown")
            with tab2: st.code(article_content, language="markdown")
            with tab3:
                meta_part = article.split("---")[0] if "---" in article else ""
                st.code(f"{meta_part}---\n\n{corrected_article}" if meta_part else corrected_article, language="markdown")
            with tab4: st.code(fc_report or "Non disponible", language="markdown")
        else:
            tab1, tab2, tab3 = st.tabs(["Article seul", "Tout (méta + article)", "Rapport fact-check"])
            with tab1: st.code(article_content, language="markdown")
            with tab2: st.code(article, language="markdown")
            with tab3:
                if fc_report:
                    st.code(fc_report, language="markdown")
                else:
                    st.info("Fact-checking non activé")

# Footer
st.markdown('<div style="text-align: center; margin-top: 3rem; color: #94a3b8; font-size: 0.85rem;">Propulsé par Claude API & Serper</div>', unsafe_allow_html=True)
