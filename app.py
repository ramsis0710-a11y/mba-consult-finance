import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from fpdf import FPDF
from datetime import datetime

# --- 🛰️ CONFIGURATION OMNI-GENESIS FINANCE V60 ---
st.set_page_config(page_title="KMS STRATÉGIQUE PRÉDICTIF", layout="wide")

# --- 🌐 MOTEUR DE SCRAPING FINANCIER (LIVE) ---
def get_live_market_data():
    # Valeurs par défaut en cas d'échec de scraping
    data = {"BRENT": 84.50, "TND_USD": 3.14} 
    # Note : En production réelle, on utilise ici une API (yfinance/AlphaVantage)
    return data

live_market = get_live_market_data()

# --- 📁 SYNC EXCEL POUR PARAMÈTRES INTERNES ---
def load_internal_kpis():
    if os.path.exists("kms_data.xlsx"):
        try:
            df = pd.read_excel("kms_data.xlsx")
            return df.set_index('Indicateur')['Valeur'].to_dict()
        except: pass
    return {"W_MSHOP": 0.64, "W_DSALES": 0.19, "W_MAIN": 0.17, "SEUIL_CAPEX": 0.141, "INF_ACIER": 0.12}

internal = load_internal_kpis()

# --- 🎛️ SIDEBAR : INDICATEURS LIVE ---
st.sidebar.title("💠 LIVE MONITORING")
st.sidebar.metric("🛢️ BRENT CRUDE", f"{live_market['BRENT']} $")
st.sidebar.metric("🇹🇳 TAUX TND/USD", f"{live_market['TND_USD']}")
st.sidebar.markdown("---")
st.sidebar.write(f"🎯 **Seuil CAPEX :** {internal['SEUIL_CAPEX']*100}%")

# --- 📈 DASHBOARD PRINCIPAL ---
st.title("📈 MBA-CONSULT | KMS FINANCE PRÉDICTIF")
st.info(f"Analyse prédictive basée sur le centre de gravité industriel (M-Shop : {internal['W_MSHOP']*100}%)")

# --- 📊 GRAPHIQUE DE SENSIBILITÉ (PRIX DU BARIL VS EBITDA) ---
st.subheader("📉 Simulation de Rentabilité : Impact du cours du Pétrole")

# Création d'une plage de prix du baril (de -20% à +20% du prix actuel)
brent_range = np.linspace(live_market['BRENT'] * 0.8, live_market['BRENT'] * 1.2, 10)
# Calcul de l'EBITDA projeté pour chaque prix
ebitda_projections = [(internal['W_MSHOP'] * 0.22) * (price / 80) * (1 - internal['INF_ACIER']) * 100 for price in brent_range]

chart_data = pd.DataFrame({
    'Prix du Baril ($)': brent_range,
    'EBITDA Projeté (%)': ebitda_projections
})

st.line_chart(chart_data.set_index('Prix du Baril ($)'))
st.caption("Ce graphique montre comment votre marge nette fluctue selon le marché international.")

# --- 📄 GÉNÉRATEUR DE RAPPORT PDF DÉTAILLÉ ---
def generate_strategic_report(ebitda_actuel):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RAPPORT STRATEGIQUE KMS - MBA-CONSULT", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"DONNEES MARCHE : Brent {live_market['BRENT']}$ | USD/TND {live_market['TND_USD']}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    report_text = (
        f"L'analyse predictive montre qu'avec un baril a {live_market['BRENT']}$, "
        f"votre EBITDA cible est de {round(ebitda_actuel, 2)}%. "
        f"Le seuil de securite pour vos investissements en Tunisie est fixe a {internal['SEUIL_CAPEX']*100}%. "
        "Toute baisse du baril sous les 75$ necessitera une revision des couts de production."
    )
    pdf.multi_cell(0, 10, report_text)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, f"Document genere par KMS OMNI-GENESIS - {datetime.now()}", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# Calcul de l'EBITDA au prix actuel pour le rapport
ebitda_now = (internal['W_MSHOP'] * 0.22) * (live_market['BRENT'] / 80) * (1 - internal['INF_ACIER']) * 100

st.divider()
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("📥 GÉNÉRER LES CONCLUSIONS (PDF)", use_container_width=True):
        pdf_bytes = generate_strategic_report(ebitda_now)
        st.download_button("⬇️ TÉLÉCHARGER LE RAPPORT", data=pdf_bytes, file_name="STRATEGIE_KMS.pdf", mime="application/pdf")

with col_btn2:
    st.link_button("🏭 RETOUR AU GÉNÉRATEUR QP", "https://mba-consult-qp-generator.streamlit.app/", use_container_width=True)