"""Configuration : CSS, constantes et styles de l'application."""

APP_TITLE = "Discover Writer"
APP_ICON = "✨"
APP_SUBTITLE = "Génère des articles optimisés pour Google Discover en quelques clics"

# Limites
MAX_SOURCES_REDACTION = 10
MAX_SOURCES_FACTCHECK = 6
JINA_MAX_CHARS = 25000
SOURCE_TRUNCATE_CHARS = 12000

# Modèle
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
GENERATION_TEMPERATURE = 0.8
FACTCHECK_TEMPERATURE = 0.15
GENERATION_MAX_TOKENS = 6000
FACTCHECK_MAX_TOKENS = 8000

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #fafafa 0%, #f0f4f8 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
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
    
    .stSelectbox > div > div { border-radius: 12px !important; }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
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
    
    .stButton > button:active { transform: translateY(0); }
    
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
    
    .success-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .fc-summary {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
    }
    
    .fc-corrections-banner {
        background: linear-gradient(135deg, #10b98115, #05966915);
        border: 1px solid #10b98140;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        font-size: 0.9rem;
        color: #065f46;
    }
    
    .streamlit-expanderHeader {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        color: #475569 !important;
        background: #f8fafc !important;
        border-radius: 12px !important;
    }
    
    .stAlert { border-radius: 12px !important; }
    
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
    
    .stRadio > div > label:hover { border-color: #667eea; }
    
    .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
</style>
"""
