import streamlit as st
import pandas as pd
import qrcode
import os
from io import BytesIO

# --- 🛡️ CONFIGURATION STRATÉGIQUE V41.0 ---
st.set_page_config(
    page_title="MBA-CONSULT | KMS Direction", 
    page_icon="📊", 
    layout="wide"
)

# --- 🛰️ NAVIGATION KMS ---
st.sidebar.title("🌐 SYSTÈME KMS")
st.sidebar.success("📊 MODULE : STRATÉGIE & FINANCE")
st.sidebar.markdown("---")
# LIEN VERS VOTRE APP DE PRODUCTION DÉJÀ EN LIGNE
st.sidebar.markdown("### 🏭 [RETOUR À LA PRODUCTION (QP)](https://mba-consult-qp-generator.streamlit.app)")
st.sidebar.markdown("---")

# --- 🖼️ LOGO ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=200)

# --- 🌍 VARIABLES MACRO (CONTEXTE 2026) ---
MACRO_FACTORS = {"PRIX_BARIL_USD": 120, "INFLATION_ACIER": 0.15, "PREMIUM_URGENCE": 0.25}

# --- 📊 MATRICE EMPIRIQUE ---
REAL_WEIGHTS = {"M-SHOP": 0.64, "D.SALES": 0.19, "MAIN": 0.17}
TARGET_EBITDA_GLOBAL = 22.0

# --- 🧠 FONCTIONS ---
def get_crisis_adjusted_ebitda(dept_key):
    weight = REAL_WEIGHTS.get(dept_key, 0.20)
    base_cont = TARGET_EBITDA_GLOBAL * weight
    if dept_key == "M-SHOP":
        return round(base_cont * (1 - MACRO_FACTORS["INFLATION_ACIER"]) * (1 + MACRO_FACTORS["PREMIUM_URGENCE"]), 2)
    return round(base_cont * 1.10, 2)

def simulateur_capex_mshop(ca_actuel, cout_machine, duree_amort, gain_ca_annuel):
    amortissement_annuel = cout_machine / duree_amort
    nouveau_ca_total = ca_actuel + gain_ca_annuel
    nouvel_ebitda_estim = (ca_actuel * 0.22) - amortissement_annuel + (gain_ca_annuel * 0.40)
    contribution_globale = (nouvel_ebitda_estim / nouveau_ca_total) * REAL_WEIGHTS["M-SHOP"]
    return contribution_globale >= 0.141, round(contribution_globale * 100, 2)

# --- 📱 INTERFACE ---
st.title("🌐 MBA-CONSULT | KMS STRATÉGIQUE V41.0")
st.info(f"🚀 Contexte 2026 : Baril à {MACRO_FACTORS['PRIX_BARIL_USD']}$ | Inflation Matière : +{MACRO_FACTORS['INFLATION_ACIER']*100}%")

tab1, tab2 = st.tabs(["📊 Performance EBITDA", "🛡️ Stress-Test Investissement (CAPEX)"])

with tab1:
    st.header("Analyse des Projections")
    res_data = []
    for dept, weight in REAL_WEIGHTS.items():
        res_data.append({
            "Département": dept,
            "Poids (TOT)": f"{weight*100}%",
            "EBITDA Cible 2026": f"{get_crisis_adjusted_ebitda(dept)}%",
            "Priorité": "CRITIQUE" if dept == "M-SHOP" else "LEV DE CASH"
        })
    st.table(pd.DataFrame(res_data))

with tab2:
    st.header("Validation d'Investissement Machine-Outil")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            val_achat = st.number_input("Prix de la machine (USD)", value=250000)
            duree = st.slider("Amortissement (Années)", 3, 10, 5)
        with c2:
            ca_mshop = st.number_input("CA Actuel M-Shop (USD)", value=1200000)
            ca_supp = st.number_input("CA Additionnel attendu (USD)", value=350000)
    
    if st.button("🔥 EXÉCUTER LE TEST DE DILUTION", type="primary", use_container_width=True):
        is_ok, score = simulateur_capex_mshop(ca_mshop, val_achat, duree, ca_supp)
        if is_ok:
            st.success(f"✅ INVESTISSEMENT VALIDÉ ({score}%).")
            st.balloons()
        else:
            st.error(f"❌ VETO : Rentabilité insuffisante ({score}%).")

st.divider()
st.caption("© 2026 MBA-CONSULT - Système de Management de la Connaissance (KMS)")
