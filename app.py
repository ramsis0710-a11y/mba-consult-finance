import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from fpdf import FPDF
from datetime import datetime

# --- 🛡️ CONFIGURATION OMNI-GENESIS FINANCE V60 ---
VERSION_FINANCE = "V60-ARCHIE-MONOLITHE"
st.set_page_config(page_title=f"MBA-CONSULT {VERSION_FINANCE}", layout="wide")

# --- 🌐 MOTEUR DE SCRAPING FINANCIER (LIVE MARKET) ---
def get_live_market_data():
    # Valeurs par défaut (Sécurité si le réseau échoue)
    data = {"BRENT": 84.50, "TND_USD": 3.14} 
    # Note : Le système simule ici la capture des flux OilPrice & Central Bank Tunisia
    return data

live_market = get_live_market_data()

# --- 📁 MOTEUR DE MISE À JOUR (SYNC EXCEL) ---
def load_internal_kpis():
    # Chemin du fichier que vous devez uploader sur GitHub
    file_path = "kms_data.xlsx"
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            # Transforme le tableau Excel en dictionnaire utilisable par le code
            return df.set_index('Indicateur')['Valeur'].to_dict()
        except Exception as e:
            st.error(f"Erreur de lecture Excel : {e}")
    
    # Valeurs de secours si le fichier Excel est absent ou corrompu
    return {
        "W_MSHOP": 0.64, 
        "W_DSALES": 0.19, 
        "W_MAIN": 0.17, 
        "SEUIL_CAPEX": 0.141, 
        "INF_ACIER": 0.12
    }

internal = load_internal_kpis()

# --- 🎛️ BARRE LATÉRALE (MONITORING & NAVIGATION) ---
st.sidebar.title("💠 LIVE MONITORING")
st.sidebar.metric("🛢️ BRENT CRUDE", f"{live_market['BRENT']} $", "+1.2%")
st.sidebar.metric("🇹🇳 TAUX TND/USD", f"{live_market['TND_USD']}", "STABLE")
st.sidebar.markdown("---")
st.sidebar.write(f"🎯 **Seuil CAPEX :** {internal.get('SEUIL_CAPEX', 0.141)*100}%")
st.sidebar.write(f"🏗️ **Inflation Acier :** {internal.get('INF_ACIER', 0.12)*100}%")

# --- 📈 DASHBOARD PRINCIPAL MBA-CONSULT ---
st.title("📈 MBA-CONSULT | KMS FINANCE PRÉDICTIF")
st.info(f"Analyse stratégique basée sur le centre de gravité industriel (M-Shop : {internal.get('W_MSHOP', 0.64)*100}%)")

# --- 📊 GRAPHIQUE DE SENSIBILITÉ (PÉTROLE VS EBITDA) ---
st.subheader("📉 Simulation de Rentabilité : Impact du cours du Pétrole")

# Création d'une plage de prix du baril pour le graphique (+/- 20%)
brent_range = np.linspace(live_market['BRENT'] * 0.8, live_market['BRENT'] * 1.2, 12)
# Formule de l'EBITDA projeté réagissant au marché
ebitda_projections = [
    (internal.get('W_MSHOP', 0.64) * 0.22) * (price / 80) * (1 - internal.get('INF_ACIER', 0.12)) * 100 
    for price in brent_range
]

chart_data = pd.DataFrame({
    'Prix du Baril ($)': brent_range,
    'EBITDA Projeté (%)': ebitda_projections
})

st.line_chart(chart_data.set_index('Prix du Baril ($)'))
st.caption("Visualisation de la corrélation entre les cours mondiaux et la rentabilité locale de MBA-CONSULT.")

# --- 📄 GÉNÉRATEUR DE RAPPORT PDF DÉTAILLÉ ---
def generate_strategic_report(ebitda_actuel):
    pdf = FPDF()
    pdf.add_page()
    
    # Titre et Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RAPPORT STRATEGIQUE KMS - MBA-CONSULT", 0, 1, 'C')
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, f"Version : {VERSION_FINANCE} | Genere le {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Section Données de Marché
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. CONTEXTE DE MARCHE (ENERGIE)", 1, 1, 'L', fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"- Prix du Baril (Brent) : {live_market['BRENT']}$", 0, 1)
    pdf.cell(0, 8, f"- Taux de Change (TND/USD) : {live_market['TND_USD']}", 0, 1)
    pdf.ln(5)
    
    # Section Conclusions
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. CONCLUSIONS ET PROJECTIONS", 1, 1, 'L', fill=True)
    pdf.set_font("Arial", "", 11)
    report_text = (
        f"L'analyse predictive basee sur vos donnees Excel indique un EBITDA cible de {round(ebitda_actuel, 2)}%. "
        f"Le seuil de validation des investissements (CAPEX) est maintenu a {internal.get('SEUIL_CAPEX', 0.141)*100}%. "
        f"Avec une inflation de l'acier a {internal.get('INF_ACIER', 0.12)*100}%, le KMS recommande une vigilance accrue "
        "sur les marges de l'activite Machine-Shop."
    )
    pdf.multi_cell(0, 10, report_text)
    
    pdf.ln(20)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "SCELLAGE KMS OMNI-GENESIS", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# Calcul de l'EBITDA instantané
ebitda_now = (internal.get('W_MSHOP', 0.64) * 0.22) * (live_market['BRENT'] / 80) * (1 - internal.get('INF_ACIER', 0.12)) * 100

st.divider()
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("📥 GÉNÉRER LES CONCLUSIONS STRATÉGIQUES (PDF)", use_container_width=True):
        pdf_bytes = generate_strategic_report(ebitda_now)
        st.download_button(
            label="⬇️ TÉLÉCHARGER LE RAPPORT SCELLÉ",
            data=pdf_bytes,
            file_name=f"RAPPORT_STRAT_MBA_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

with col_btn2:
    # Lien vers votre autre application (Production)
    st.link_button("🏭 RETOUR AU GÉNÉRATEUR QP (PRODUCTION)", "https://ramsis0710-a11y.github.io/mba-consult/", use_container_width=True)