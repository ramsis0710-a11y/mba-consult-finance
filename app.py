import streamlit as st
import pandas as pd
import numpy as np
import os
from fpdf import FPDF
from datetime import datetime

# --- 🛡️ CONFIGURATION OMNI-GENESIS FINANCE V70 ---
VERSION_FINANCE = "V70-STRESS-TEST-INTEGRATED"
st.set_page_config(page_title=f"MBA-CONSULT {VERSION_FINANCE}", layout="wide")

# --- 📁 MOTEUR DE DONNÉES (SYNC EXCEL) ---
def load_internal_kpis():
    file_path = "kms_data.xlsx"
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            return df.set_index('Indicateur')['Valeur'].to_dict()
        except: pass
    return {
        "W_MSHOP": 0.64, "W_DSALES": 0.19, "W_MAIN": 0.17, 
        "SEUIL_CAPEX": 0.141, "INF_ACIER": 0.12, "BRENT": 84.5, "TND_USD": 3.14
    }

data = load_internal_kpis()

# --- 📊 LOGIQUE DE CALCUL DES KPIs PAR ACTIVITÉ ---
# Calcul des marges théoriques basées sur l'environnement
marge_mshop = (0.22 * (data['BRENT']/80)) - data['INF_ACIER']
marge_dsales = 0.15 * (1 / data['TND_USD'] * 3.1)
marge_main = 0.18 + (data['INF_ACIER'] * 0.2)

kpi_table = pd.DataFrame({
    "Activité": ["M-SHOP", "D.SALES", "MAINTENANCE"],
    "Poids (%)": [data['W_MSHOP']*100, data['W_DSALES']*100, data['W_MAIN']*100],
    "Marge Prévue (%)": [round(marge_mshop*100, 2), round(marge_dsales*100, 2), round(marge_main*100, 2)],
    "Statut": ["CRITIQUE" if marge_mshop < 0.10 else "NOMINAL", "STABLE", "CROISSANCE"]
})

# --- 🎛️ INTERFACE : TABLEAU DES INDICATEURS ---
st.title("📈 MBA-CONSULT | KMS FINANCE & STRATÉGIE")
st.subheader("Tableau de Bord des KPIs et Ratios par Activité")

col1, col2, col3 = st.columns(3)
col1.metric("EBITDA M-SHOP", f"{kpi_table.iloc[0, 2]}%", delta="-0.5%", delta_color="inverse")
col2.metric("EBITDA D.SALES", f"{kpi_table.iloc[1, 2]}%", delta="Stable")
col3.metric("EBITDA MAINT.", f"{kpi_table.iloc[2, 2]}%", delta="+1.2%")

st.table(kpi_table)

# --- 🛡️ ZONE DE STRESS-TEST (SIMULATEUR CAPEX) ---
st.divider()
st.subheader("🔥 STRESS-TEST : Validation d'Investissement")
with st.expander("Exécuter une simulation d'achat machine / infrastructure", expanded=True):
    c1, c2 = st.columns(2)
    val_achat = c1.number_input("Montant de l'investissement (USD)", value=50000, step=5000)
    duree = c2.slider("Durée d'amortissement (Années)", 1, 10, 5)
    
    # Formule de Stress-Test MBA-CONSULT
    score_brut = (val_achat / 500000) * data['W_MSHOP']
    score_final = score_brut / (1 + data['INF_ACIER'])
    
    if score_final >= data['SEUIL_CAPEX']:
        st.success(f"✅ TEST RÉUSSI : Score de rentabilité {round(score_final*100, 2)}% (Seuil: {data['SEUIL_CAPEX']*100}%)")
    else:
        st.error(f"❌ TEST ÉCHOUÉ : Rentabilité insuffisante ({round(score_final*100, 2)}%). Réviser le CAPEX.")

# --- 📄 GÉNÉRATEUR DE RAPPORT PDF AVEC LOGO ---
def generate_advanced_report():
    pdf = FPDF()
    pdf.add_page()
    
    # Insertion du LOGO (A droite, 3x6 cm)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=140, y=10, w=60, h=30) # Ajusté pour 6cm de large
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RAPPORT DE SYNTHESE KMS", 0, 1, 'L')
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Généré le {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'L')
    pdf.ln(15)
    
    # Tableau Récapitulatif des KPIs
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, "TABLEAU RÉCAPITULATIF DES KPIs PAR ACTIVITÉ", 1, 1, 'C', fill=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 10, "Activite", 1)
    pdf.cell(60, 10, "Poids (%)", 1)
    pdf.cell(70, 10, "Marge Prevue (%)", 1, 1)
    
    pdf.set_font("Arial", "", 10)
    for index, row in kpi_table.iterrows():
        pdf.cell(60, 10, str(row['Activité']), 1)
        pdf.cell(60, 10, str(row['Poids (%)']), 1)
        pdf.cell(70, 10, str(row['Marge Prévue (%)']), 1, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "CONCLUSION DU STRESS-TEST", 0, 1)
    pdf.set_font("Arial", "", 11)
    conclusion = f"L'analyse de rentabilite globale montre un score moyen de {round(kpi_table['Marge Prévue (%)'].mean(), 2)}%. "
    conclusion += f"L'impact de l'inflation de l'acier ({data['INF_ACIER']*100}%) est sous controle pour le secteur Energie."
    pdf.multi_cell(0, 10, conclusion)
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button("📥 GÉNÉRER LE RAPPORT STRATÉGIQUE PDF", use_container_width=True):
    pdf_output = generate_advanced_report()
    st.download_button("⬇️ TÉLÉCHARGER LE PDF", data=pdf_output, file_name="Rapport_KMS_Final.pdf", mime="application/pdf")