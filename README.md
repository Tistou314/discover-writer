# ✨ Discover Writer

Application de génération d'articles optimisés pour Google Discover.

## Fonctionnement

1. Entre un mot-clé ou sujet
2. L'app recherche les 5-10 meilleures sources sur Google
3. Elle analyse le contenu de chaque page
4. Claude génère un article original optimisé Discover

## Prérequis

Tu as besoin de deux clés API :

### 1. Clé Anthropic
- Va sur [console.anthropic.com](https://console.anthropic.com)
- Crée un compte si nécessaire
- Génère une clé API

### 2. Clé Serper (recherche Google)
- Va sur [serper.dev](https://serper.dev)
- Crée un compte (gratuit : 2500 requêtes offertes)
- Copie ta clé API

## Déploiement sur Streamlit Cloud (Recommandé)

### Étape 1 : Push sur GitHub

```bash
# Clone ce dossier ou crée un nouveau repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/TON-USERNAME/discover-writer.git
git push -u origin main
```

### Étape 2 : Déployer

1. Va sur [share.streamlit.io](https://share.streamlit.io)
2. Connecte ton compte GitHub
3. Clique "New app"
4. Sélectionne ton repo `discover-writer`
5. Branch: `main`
6. Main file path: `app.py`
7. Clique "Deploy"

### Étape 3 : C'est prêt !

Partage l'URL avec ton équipe. Chacun entre ses clés API dans l'interface.

---

## Alternative : Secrets partagés

Si tu veux pré-configurer les clés API pour ton équipe :

1. Dans Streamlit Cloud, va dans "Settings" > "Secrets"
2. Ajoute :

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
SERPER_API_KEY = "..."
```

3. Modifie `app.py` pour lire les secrets :

```python
import os

# Au début du fichier, après les imports
if 'ANTHROPIC_API_KEY' in st.secrets:
    st.session_state['anthropic_key'] = st.secrets['ANTHROPIC_API_KEY']
    st.session_state['serper_key'] = st.secrets['SERPER_API_KEY']
    st.session_state['api_configured'] = True
```

---

## Lancer en local

```bash
# Installe les dépendances
pip install -r requirements.txt

# Lance l'app
streamlit run app.py
```

L'app s'ouvre sur http://localhost:8501

---

## Structure des coûts

| Service | Coût |
|---------|------|
| Serper | 2500 requêtes gratuites, puis ~$50/50k requêtes |
| Claude API | ~$0.003/1K tokens input, ~$0.015/1K tokens output |
| Jina Reader | Gratuit |
| Streamlit Cloud | Gratuit (apps publiques) ou $25/mois (privées) |

**Estimation par article** : ~$0.02-0.05 selon la longueur

---

## Personnalisation

### Changer le modèle Claude

Dans `app.py`, ligne ~180, remplace :
```python
model="claude-sonnet-4-20250514"
```

Par `claude-opus-4-20250514` pour plus de qualité (mais plus cher).

### Modifier le prompt

Le prompt système est dans la fonction `generate_article()`. Adapte-le à ton style éditorial.

---

## Support

Des questions ? Contacte l'équipe ECF.
