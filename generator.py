"""Génération d'article via Claude + nettoyage post-traitement."""

import re
import anthropic
from typing import List, Dict
from config import CLAUDE_MODEL, GENERATION_TEMPERATURE, GENERATION_MAX_TOKENS, SOURCE_TRUNCATE_CHARS
from prompts import build_generation_system_prompt, build_generation_user_prompt


def clean_ai_markers(text: str) -> str:
    """Nettoie les marqueurs typographiques trahissant l'IA en post-traitement."""
    # Tirets quadratins et demi-cadratins → virgule
    for dash in [' — ', ' —', '— ', '—', ' – ', ' –', '– ', '–']:
        text = text.replace(dash, ', ' if dash.startswith(' ') or dash.endswith(' ') else ',')
    
    # Fix : remplacement plus propre
    text = text.replace(' — ', ', ')
    text = text.replace(' —', ',')
    text = text.replace('— ', ', ')
    text = text.replace('—', ', ')
    text = text.replace(' – ', ', ')
    text = text.replace(' –', ',')
    text = text.replace('– ', ', ')
    text = text.replace('–', ', ')

    # Guillemets anglais → français
    text = re.sub(r'"([^"]+)"', r'« \1 »', text)

    # Nettoyage doubles virgules et espaces multiples
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'  +', ' ', text)

    return text


def generate_article(
    client: anthropic.Anthropic,
    keyword: str,
    sources: List[Dict],
    contents: List[str],
    custom_instructions: str = "",
    article_length: int = 800
) -> str:
    """Génère l'article via Claude et nettoie les marqueurs IA."""

    # Préparer le contexte des sources
    sources_context = ""
    for i, (source, content) in enumerate(zip(sources, contents), 1):
        sources_context += f"""
--- SOURCE {i} ---
Titre: {source['title']}
URL: {source['url']}
Contenu:
{content[:SOURCE_TRUNCATE_CHARS]}

"""

    system_prompt = build_generation_system_prompt(custom_instructions, article_length)
    user_prompt = build_generation_user_prompt(keyword, sources_context, custom_instructions, article_length)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=GENERATION_MAX_TOKENS,
        temperature=GENERATION_TEMPERATURE,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt
    )

    return clean_ai_markers(response.content[0].text)
