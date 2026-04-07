import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="MBA-CONSULT | KMS Finance", 
    page_icon="📊", 
    layout="wide"
)

# --- 2. NAVIGATION LATÉRALE (SIDEBAR) ---
st.sidebar.title("🌐 SYSTÈME KMS")
st.sidebar.success("📊 MODULE : STRATÉGIE & FINANCE")
st.sidebar.markdown("---")

# LIEN VERS VOTRE APPLICATION DE PRODUCTION DÉJÀ EXISTANTE
st.sidebar.markdown("### 🏭 [RETOUR À LA PRODUCTION (QP)](https://mba-consult-qp-generator.streamlit.app)")
st.sidebar.markdown("---")

# Affichage du logo si présent dans le dépôt
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

# --- 3. LOGIQUE MÉTIER & VARIABLES 2026 ---
# Paramètres macro-économiques
MACRO_FACTORS = {
    "PRIX_BARIL_USD": 120, 
    "INFLATION_ACIER": 0.15, 
    "PREMIUM_URGENCE": 0.25
}

# Pondération réelle du chiffre d'affaires (Centre de gravité : M-Shop)
REAL_WEIGHTS = {
    "M-SHOP": 0.64,   
    "D.SALES": 0.19,  
    "MAIN": 0.17      
}

TARGET_EBITDA_GLOBAL = 22.0 # Objectif stratégique global (%)

# --- 4. FONCTIONS DE CALCUL ---
def calculer_score_capex(ca_mshop, prix_machine, amort_annees, ca_additionnel):
    """Calcule si l'investissement respecte le seuil critique de 14.1%."""
    amortissement_annuel = prix_machine / amort_annees
    nouveau_ca_total = ca_mshop + ca_additionnel
    
    # Estimation EBITDA : (Marge existante 22%) - Amortissement + (Marge nouveau CA 40%)
    ebitda_estime = (ca_mshop * 0.22) - amortissement_annuel + (ca_additionnel * 0.40)
    
    # Contribution pondérée au groupe (Focus M-Shop)
    score_final = (ebitda_estime / nouveau_ca_total) * REAL_WEIGHTS["M-SHOP"]
    return score_final >= 0.141, round(score_final * 100, 2)

# --- 5. INTERFACE UTILISATEUR (MAIN UI) ---
st.title("🌐 MBA-CONSULT | KMS STRATÉGIQUE V41.0")
st.info(f"🚀 Contexte 2026 : Baril à {MACRO_FACTORS['PRIX_BARIL_USD']}$ | Inflation Acier : +{MACRO_FACTORS['INFLATION_ACIER']*100}%")

tab1, tab2 = st.tabs(["📊 Performance EBITDA", "🛡️ Stress-Test Investissement (CAPEX)"])

# --- ONGLET 1 : ANALYSE DE PERFORMANCE ---
with tab1:
    st.header("Analyse des Projections (Pondération Réelle)")
    st.markdown("Répartition de l'activité basée sur le centre de gravité industriel (64% Machine-Shop).")
    
    data_performance = []
    for dept, weight in REAL_WEIGHTS.items():
        # Calcul simplifié de l'EBITDA ajusté
        ebitda_cible = TARGET_EBITDA_GLOBAL * weight * 1.15 if dept == "M-SHOP" else TARGET_EBITDA_GLOBAL * weight
        data_performance.append({
            "Département": dept,
            "Poids (TOT)": f"{weight*100}%",
            "EBITDA Cible": f"{round(ebitda_cible, 2)}%",
            "Priorité": "CRITIQUE" if dept == "M-SHOP" else "LEV DE CASH"
        })
    
    st.table(pd.DataFrame(data_performance))
    st.warning("⚠️ Le Machine-Shop doit maintenir une contribution de 14.1% pour valider la structure de coûts.")

# --- ONGLET 2 : SIMULATEUR D'INVESTISSEMENT ---
with tab2:
    st.header("Validation d'Investissement Machine-Outil")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            val_achat = st.number_input("Prix d'achat machine (USD)", value=250000, step=5000)
            duree = st.slider("Durée d'amortissement (Années)", 3, 10, 5)
        with col2:
            ca_actuel = st.number_input("CA Actuel M-Shop (USD)", value=1200000, step=10000)
            ca_futur = st.number_input("Gain de CA annuel attendu (USD)", value=350000, step=10000)
    
    if st.button("🔥 EXÉCUTER LE TEST DE DILUTION", type="primary", use_container_width=True):
        est_valide, resultat = calculer_score_capex(ca_actuel, val_achat, duree, ca_futur)
        
        if est_valide:
            st.success(f"✅ INVESTISSEMENT VALIDÉ. Contribution projetée : {resultat}% (Seuil : 14.1%).")
            st.balloons()
        else:
            st.error(f"❌ VETO STRATÉGIQUE : L'investissement dilue la rentabilité à {resultat}%.")
            st.markdown("> **Conseil :** Augmentez la durée d'amortissement ou négociez le prix d'achat sous les **210,000 USD**.")

st.divider()
st.caption("© 2026 MBA-CONSULT - Système de Management de la Connaissance (KMS)")