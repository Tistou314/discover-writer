"""Fonctions utilitaires : parsing des résultats, helpers."""


def parse_article_result(result: str) -> tuple:
    """Sépare les métadonnées SEO de l'article généré."""
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


def extract_article_only(article: str) -> str:
    """Extrait uniquement le contenu article (sans métadonnées)."""
    if "---" in article:
        parts = article.split("---")
        return "---".join(parts[1:]).strip().replace("```", "").strip()
    return article
