import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime
import re
import matplotlib.pyplot as plt
import io
import random
import string

# --- 🛡️ CONFIGURATION OMNI-GENESIS FINANCE V85 ---
VERSION_FINANCE = "V85-LIVE-BCT-INTEGRATED"
st.set_page_config(page_title=f"MBA-CONSULT {VERSION_FINANCE}", layout="wide")

# --- 🌐 MOTEUR DE SCRAPING BOURSORAMA & DINAR TUNISIEN (TEMPS RÉEL) ---
def get_live_market_data():
    market_data = {"BRENT": 84.5, "TND_USD": None} 
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        oil_url = "https://www.boursorama.com/bourse/matieres-premieres/cours/8xBRN/"
        res_oil = requests.get(oil_url, headers=headers, timeout=10)
        if res_oil.status_code == 200:
            soup = BeautifulSoup(res_oil.text, 'html.parser')
            price_tag = soup.find("span", class_="c-instrument c-instrument--last")
            if price_tag:
                market_data["BRENT"] = float(price_tag.text.replace(" ", "").replace(",", ".").strip())

        curr_url = "https://www.dinartunisien.com/fr/banque/banque-centrale-tunisie"
        res_curr = requests.get(curr_url, headers=headers, timeout=10)
        if res_curr.status_code == 200:
            soup_curr = BeautifulSoup(res_curr.text, 'html.parser')
            rows = soup_curr.find_all("tr")
            for row in rows:
                if "USD" in row.text or "Dollar" in row.text:
                    cells = row.find_all("td")
                    for cell in reversed(cells):
                        val_txt = cell.text.strip().replace(",", ".")
                        try:
                            val_float = float(val_txt)
                            if 2.0 < val_float < 4.0:
                                market_data["TND_USD"] = val_float
                                break
                        except: continue
                    if market_data["TND_USD"]: break
    except:
        pass
    if market_data["TND_USD"] is None:
        market_data["TND_USD"] = 2.9281 
    return market_data

live_market = get_live_market_data()

# --- 📁 MOTEUR DE DONNÉES (SYNC EXCEL & BACKUP SÉCURITÉ) ---
def load_internal_kpis():
    file_path = "kms_data.xlsx"
    base_kpis = {
        "W_MSHOP": 0.64, "W_DSALES": 0.19, "W_MAIN": 0.17, 
        "SEUIL_CAPEX": 0.141, "INF_ACIER": 0.12, 
        "BRENT": live_market["BRENT"], "TND_USD": live_market["TND_USD"]
    }
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            excel_data = df.set_index('Indicateur')['Valeur'].to_dict()
            excel_data["BRENT"] = live_market["BRENT"]
            excel_data["TND_USD"] = live_market["TND_USD"]
            return excel_data
        except:
            return base_kpis
    return base_kpis

data = load_internal_kpis()

# --- 📊 LOGIQUE DE CALCUL DES KPIs PAR ACTIVITÉ ---
marge_mshop = (0.22 * (data['BRENT']/80)) - data['INF_ACIER']
marge_dsales = 0.15 * (1 / data['TND_USD'] * 3.1)
marge_main = 0.18 + (data['INF_ACIER'] * 0.2)

status_mshop = "CONFORME" if marge_mshop >= 0.20 else "ALERTE RENTABILITÉ"
status_dsales = "CONFORME" if marge_dsales <= 0.10 else "HORS STRATÉGIE"
status_main = "CONFORME" if marge_main >= 0.25 else "SOUS-PERFORMANCE"

kpi_table = pd.DataFrame({
    "Activité": ["M-SHOP", "D.SALES", "MAINTENANCE"],
    "Poids (%)": [data['W_MSHOP']*100, data['W_DSALES']*100, data['W_MAIN']*100],
    "Marge Prévue (%)": [round(marge_mshop*100, 2), round(marge_dsales*100, 2), round(marge_main*100, 2)],
    "Statut": [status_mshop, status_dsales, status_main]
})

# --- 🎛️ SIDEBAR ---
st.sidebar.title("💠 ARCHIE NAVIGATION")
st.sidebar.link_button("🚀 ACCÈS PRODUCTION (MBA-QP)", "https://mba-consult-qp-generator.streamlit.app/", use_container_width=True)
st.sidebar.markdown("---")
entite_selectionnee = st.sidebar.radio("🏢 SÉLECTIONNER L'ENTITÉ :", ["MBA-CONSULT", "GMPI"], index=0)
st.sidebar.markdown("---")
st.sidebar.title("🌐 LIVE MARKET DATA")
st.sidebar.metric("🛢️ BRENT (Boursorama)", f"{data['BRENT']} $", delta="LIVE")
st.sidebar.metric("🇹🇳 USD / TND (LIVE)", f"{data['TND_USD']}", delta="LIVE")

# --- 📈 DASHBOARD ---
st.title(f"📈 {entite_selectionnee} | KMS FINANCE & STRATÉGIE")
st.table(kpi_table)

# --- 📉 GRAPHES ---
st.divider()
brent_range = np.linspace(data['BRENT'] * 0.7, data['BRENT'] * 1.3, 15)
sim_mshop = [(0.22 * (p/80) - data['INF_ACIER']) * 100 for p in brent_range]
sim_dsales = [round(marge_dsales*100, 2)] * len(brent_range)
sim_main = [round(marge_main*100, 2)] * len(brent_range)

df_sim = pd.DataFrame({
    'Prix du Baril ($)': brent_range,
    'M-SHOP (%)': sim_mshop,
    'D.SALES (%)': sim_dsales,
    'MAINTENANCE (%)': sim_main
})
st.line_chart(df_sim.set_index('Prix du Baril ($)'))

# --- 🛡️ STRESS-TEST ---
st.divider()
with st.expander("🔥 STRESS-TEST : Validation d'Investissement", expanded=True):
    val_achat = st.number_input("Montant de l'investissement (USD)", value=50000)
    score_final = ((val_achat / 500000) * data['W_MSHOP']) / (1 + data['INF_ACIER'])
    if score_final >= data['SEUIL_CAPEX']:
        st.success(f"✅ TEST RÉUSSI : {round(score_final*100, 2)}% (Seuil: {data['SEUIL_CAPEX']*100}%)")
    else:
        st.error(f"❌ TEST ÉCHOUÉ : Rentabilité insuffisante.")

# --- 📄 GÉNÉRATEUR DE RAPPORT PDF AMÉLIORÉ ---
def generate_advanced_report(entite):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Génération de la Référence Unique
    ref_seq = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    date_str = datetime.now().strftime('%d%m%Y')
    ref_rapport = f"REF/{ref_seq}/{date_str}"
    
    # 2. En-tête (Titre + Réf à gauche, Logo à droite)
    logo_path = "logo.png" if entite == "MBA-CONSULT" else "logo GMPI.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=140, y=10, w=60, h=30)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"RAPPORT DE SYNTHESE KMS - {entite}", 0, 1, 'L')
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, ref_rapport, 0, 1, 'L') # Référence sous le titre à gauche
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    
    # 3. Tableau des KPIs
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, "TABLEAU RÉCAPITULATIF DES KPIs PAR ACTIVITÉ", 1, 1, 'C', fill=True)
    pdf.set_font("Arial", "B", 10)
    cols = [("Activite", 60), ("Poids (%)", 60), ("Marge Prevue (%)", 70)]
    for txt, w in cols: pdf.cell(w, 10, txt, 1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    for index, row in kpi_table.iterrows():
        pdf.cell(60, 10, str(row['Activité']), 1)
        pdf.cell(60, 10, str(row['Poids (%)']), 1)
        pdf.cell(70, 10, str(row['Marge Prévue (%)']), 1, 1)

    # 4. Insertion de la Courbe Dynamique
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "SIMULATION DYNAMIQUE : IMPACT DU BRENT", 0, 1)
    
    plt.figure(figsize=(10, 5))
    plt.plot(df_sim['Prix du Baril ($)'], df_sim['M-SHOP (%)'], label='M-SHOP')
    plt.plot(df_sim['Prix du Baril ($)'], df_sim['D.SALES (%)'], label='D.SALES')
    plt.plot(df_sim['Prix du Baril ($)'], df_sim['MAINTENANCE (%)'], label='MAINTENANCE')
    plt.grid(True, linestyle='--')
    plt.legend()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')
    pdf.image(img_buf, x=15, w=180)
    plt.close()

    # 5. Signature et QR Code (10mm du fond)
    pdf.set_y(-40)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(130, 10, "Le Responsable KMS", 0, 0, 'L')
    
    # QR Code (Simulation via URL MBA-CONSULT)
    qr_url = f"https://chart.googleapis.com/chart?chs=150x150&cht=qr&chl=KMS-{ref_seq}-VERIFIED"
    try:
        qr_data = requests.get(qr_url).content
        qr_buf = io.BytesIO(qr_data)
        pdf.image(qr_buf, x=160, y=pdf.get_y()-5, w=25)
    except: pass
    
    return pdf.output(dest='S').encode('latin-1')

st.divider()
if st.button(f"📥 GÉNÉRER LE RAPPORT STRATÉGIQUE PDF ({entite_selectionnee})", use_container_width=True):
    pdf_output = generate_advanced_report(entite_selectionnee)
    st.download_button("⬇️ TÉLÉCHARGER LE PDF", data=pdf_output, file_name=f"Rapport_KMS_{entite_selectionnee}.pdf")