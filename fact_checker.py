"""Fact-checking et correction automatique via Claude."""

import re
import anthropic
from typing import List, Dict, Tuple
from config import CLAUDE_MODEL, FACTCHECK_TEMPERATURE, FACTCHECK_MAX_TOKENS, SOURCE_TRUNCATE_CHARS
from prompts import FACTCHECK_SYSTEM_PROMPT, build_factcheck_user_prompt
from generator import clean_ai_markers


def fact_check_and_correct(
    client: anthropic.Anthropic,
    article: str,
    fc_sources: List[Dict],
    fc_contents: List[str],
    keyword: str,
    custom_instructions: str = ""
) -> Tuple[str, str]:
    """
    Vérifie les faits de l'article contre des sources indépendantes (SERP + News).
    Retourne (rapport_fact_check, article_corrigé).
    """

    # Contexte des sources de vérification
    sources_context = ""
    for i, (source, content) in enumerate(zip(fc_sources, fc_contents), 1):
        date_info = f" ({source.get('date', '')})" if source.get('date') else ""
        sources_context += f"""
--- SOURCE {i} : {source['title']}{date_info} ---
URL: {source['url']}
Contenu:
{content[:SOURCE_TRUNCATE_CHARS]}

"""

    user_prompt = build_factcheck_user_prompt(article, sources_context, keyword, custom_instructions)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=FACTCHECK_MAX_TOKENS,
        temperature=FACTCHECK_TEMPERATURE,
        messages=[{"role": "user", "content": user_prompt}],
        system=FACTCHECK_SYSTEM_PROMPT
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
        report = result
        corrected_article = ""

    if corrected_article:
        return report, clean_ai_markers(corrected_article)
    return report, corrected_article


def parse_fact_check_score(fc_result: str) -> Tuple[int, str, str]:
    """Parse le score et les compteurs du fact-check."""
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

    return score, score_class, " · ".join(parts)


def count_corrections(fc_report: str) -> int:
    """Compte le nombre de corrections et omissions détectées."""
    errors = len(re.findall(r'❌', fc_report))
    reformulated = len(re.findall(r'reformulé', fc_report, re.IGNORECASE))
    removed = len(re.findall(r'retiré', fc_report, re.IGNORECASE))
    major_omissions = len(re.findall(r'🔴', fc_report))
    return errors + reformulated + removed + major_omissions
