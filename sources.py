"""Fonctions de sourcing : recherche Serper (SERP + News), scrapping Jina."""

import requests
from typing import List, Dict, Tuple
from config import JINA_MAX_CHARS


def search_serper(query: str, api_key: str, num_results: int = 10) -> List[Dict]:
    """Recherche via Serper.dev (SERP classique)."""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "gl": "fr", "hl": "fr", "num": num_results}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    return [
        {"title": item.get("title", ""), "url": item.get("link", ""), "snippet": item.get("snippet", "")}
        for item in data.get("organic", [])[:num_results]
    ]


def search_serper_news(query: str, api_key: str, num_results: int = 5) -> List[Dict]:
    """Recherche via Serper.dev endpoint News (Google Actualités)."""
    url = "https://google.serper.dev/news"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "gl": "fr", "hl": "fr", "num": num_results}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return [
            {"title": item.get("title", ""), "url": item.get("link", ""), "snippet": item.get("snippet", ""), "date": item.get("date", "")}
            for item in data.get("news", [])[:num_results]
        ]
    except Exception:
        return []


def fetch_content_jina(url: str, max_chars: int = JINA_MAX_CHARS) -> str:
    """Récupère le contenu d'une page via Jina Reader en Markdown (préserve les tableaux)."""
    jina_url = f"https://r.jina.ai/{url}"
    headers = {"Accept": "text/markdown", "X-Return-Format": "markdown"}

    try:
        response = requests.get(jina_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text[:max_chars]
    except Exception:
        try:
            response = requests.get(jina_url, headers={"Accept": "text/plain"}, timeout=30)
            response.raise_for_status()
            return response.text[:max_chars]
        except Exception as e:
            return f"Erreur lors de la récupération: {str(e)}"


def extract_title_from_url(url: str) -> str:
    """Extrait un titre simple depuis l'URL."""
    title = url.replace("https://", "").replace("http://", "").replace("www.", "")
    parts = title.split("/")
    if len(parts) > 1 and parts[1]:
        return f"{parts[0]} - {parts[1][:30]}"
    return parts[0]


def fetch_sources_for_fact_check(keyword: str, api_key: str) -> Tuple[List[Dict], List[str]]:
    """
    Récupère des sources indépendantes pour le fact-check en croisant SERP + News.
    Retourne jusqu'à 6 sources dédupliquées avec leur contenu.
    """
    all_sources = []
    seen_urls = set()

    # SERP classique
    for q in [f"{keyword} 2026 conditions éligibilité", f"{keyword} 2026 barème travaux éligibles"]:
        for r in search_serper(q, api_key, num_results=3):
            if r['url'] not in seen_urls:
                seen_urls.add(r['url'])
                r['source_type'] = 'serp'
                all_sources.append(r)

    # Google Actualités
    for q in [f"{keyword} 2026", f"{keyword} 2026 changements nouveautés"]:
        for r in search_serper_news(q, api_key, num_results=4):
            if r['url'] not in seen_urls:
                seen_urls.add(r['url'])
                r['source_type'] = 'news'
                all_sources.append(r)

    # 3 serp + 3 news, rééquilibrage si nécessaire
    serp = [s for s in all_sources if s.get('source_type') == 'serp']
    news = [s for s in all_sources if s.get('source_type') == 'news']
    final = serp[:3] + news[:3]
    remaining = 6 - len(final)
    if remaining > 0:
        final.extend([s for s in all_sources if s not in final][:remaining])
    final = final[:6]

    # Scrapper
    contents = []
    for source in final:
        try:
            contents.append(fetch_content_jina(source['url']))
        except Exception:
            contents.append("Contenu non disponible")

    return final, contents
