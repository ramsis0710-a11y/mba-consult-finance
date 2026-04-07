import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="MBA-CONSULT | KMS Finance", page_icon="📊", layout="wide")

# --- NAVIGATION ---
st.sidebar.title("🌐 SYSTÈME KMS")
st.sidebar.success("📊 MODULE : STRATÉGIE & FINANCE")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏭 [RETOUR PRODUCTION](https://mba-consult-qp-generator.streamlit.app)")

# --- LOGO ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=200)

# --- LOGIQUE FINANCIÈRE ---
MACRO_FACTORS = {"BARIL": 120, "ACIER": 0.15}
REAL_WEIGHTS = {"M-SHOP": 0.64, "D.SALES": 0.19, "MAIN": 0.17}

def check_capex(ca_mshop, prix_machine, amort, ca_plus):
    ebitda_estim = (ca_mshop * 0.22) - (prix_machine / amort) + (ca_plus * 0.40)
    score = (ebitda_estim / (ca_mshop + ca_plus)) * 0.64
    return score >= 0.141, round(score * 100, 2)

# --- INTERFACE ---
st.title("🌐 MBA-CONSULT | KMS STRATÉGIQUE")
t1, t2 = st.tabs(["📊 EBITDA", "🛡️ STRESS-TEST CAPEX"])

with t1:
    st.write("Analyse des pondérations réelles (Centre de gravité : 64% M-Shop)")
    df = pd.DataFrame([{"Dept": k, "Poids": f"{v*100}%"} for k, v in REAL_WEIGHTS.items()])
    st.table(df)

with t2:
    st.header("Validation Investissement")
    c1, c2 = st.columns(2)
    p_mach = c1.number_input("Prix Machine (USD)", value=250000)
    ca_m = c2.number_input("CA M-Shop Actuel", value=1200000)
    if st.button("🔥 TESTER LA RENTABILITÉ"):
        ok, res = check_capex(ca_m, p_mach, 5, 350000)
        if ok: st.success(f"✅ VALIDÉ : {res}%")
        else: st.error(f"❌ VÉTO : {res}% (Seuil 14.1% non atteint)")
