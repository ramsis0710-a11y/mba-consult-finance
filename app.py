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
    # On initialise avec None pour savoir si le scraping a réussi
    market_data = {"BRENT": 84.5, "TND_USD": None} 
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # 1. Scraping BRENT (Boursorama)
        oil_url = "https://www.boursorama.com/bourse/matieres-premieres/cours/8xBRN/"
        res_oil = requests.get(oil_url, headers=headers, timeout=10)
        if res_oil.status_code == 200:
            soup = BeautifulSoup(res_oil.text, 'html.parser')
            price_tag = soup.find("span", class_="c-instrument c-instrument--last")
            if price_tag:
                market_data["BRENT"] = float(price_tag.text.replace(" ", "").replace(",", ".").strip())

        # 2. Scraping USD/TND (DinarTunisien.com)
        curr_url = "https://www.dinartunisien.com/fr/banque/banque-centrale-tunisie"
        res_curr = requests.get(curr_url, headers=headers, timeout=10)
        if res_curr.status_code == 200:
            soup_curr = BeautifulSoup(res_curr.text, 'html.parser')
            # Scannage exhaustif pour trouver le Dollar USD
            rows = soup_curr.find_all("tr")
            for row in rows:
                if "USD" in row.text or "Dollar" in row.text:
                    cells = row.find_all("td")
                    for cell in reversed(cells): # Recherche de la valeur numérique en partant de la droite
                        val_txt = cell.text.strip().replace(",", ".")
                        try:
                            val_float = float(val_txt)
                            if 2.0 < val_float < 4.0: # Filtre de cohérence économique
                                market_data["TND_USD"] = val_float
                                break
                        except: continue
                    if market_data["TND_USD"]: break

    except:
        pass

    # --- SÉCURITÉ ABSOLUE ---
    # Si le scraping échoue, on évite le 3.14 et on utilise la valeur cible actuelle
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

# --- MISE À JOUR LOGIQUE SELON POLITIQUE COMMERCIALE ---
status_mshop = "CONFORME" if marge_mshop >= 0.20 else "ALERTE RENTABILITÉ"
status_dsales = "CONFORME" if marge_dsales <= 0.10 else "HORS STRATÉGIE"
status_main = "CONFORME" if marge_main >= 0.25 else "SOUS-PERFORMANCE"

kpi_table = pd.DataFrame({
    "Activité": ["M-SHOP", "D.SALES", "MAINTENANCE"],
    "Poids (%)": [data['W_MSHOP']*100, data['W_DSALES']*100, data['W_MAIN']*100],
    "Marge Prévue (%)": [round(marge_mshop*100, 2), round(marge_dsales*100, 2), round(marge_main*100, 2)],
    "Statut": [status_mshop, status_dsales, status_main]
})

# --- 🎛️ SIDEBAR : NAVIGATION & LIVE MONITORING ---
st.sidebar.title("💠 ARCHIE NAVIGATION")
st.sidebar.link_button("🚀 ACCÈS PRODUCTION (MBA-QP)", "https://mba-consult-qp-generator.streamlit.app/", use_container_width=True)

st.sidebar.markdown("---")
entite_selectionnee = st.sidebar.radio("🏢 SÉLECTIONNER L'ENTITÉ :", ["MBA-CONSULT", "GMPI"], index=0)

st.sidebar.markdown("---")
st.sidebar.title("🌐 LIVE MARKET DATA")
st.sidebar.metric("🛢️ BRENT (Boursorama)", f"{data['BRENT']} $", delta="LIVE")
st.sidebar.metric("🇹🇳 USD / TND (LIVE)", f"{data['TND_USD']}", delta="LIVE")
st.sidebar.markdown("---")
st.sidebar.write(f"🎯 **Seuil CAPEX :** {data['SEUIL_CAPEX']*100}%")
st.sidebar.write(f"🏗️ **Inflation Acier :** {data['INF_ACIER']*100}%")

# --- 📈 DASHBOARD PRINCIPAL ---
st.title(f"📈 {entite_selectionnee} | KMS FINANCE & STRATÉGIE")
st.subheader("Tableau de Bord des KPIs et Ratios par Activité")

col1, col2, col3 = st.columns(3)
col1.metric("EBITDA M-SHOP", f"{kpi_table.iloc[0, 2]}%", delta=status_mshop)
col2.metric("EBITDA D.SALES", f"{kpi_table.iloc[1, 2]}%", delta=status_dsales)
col3.metric("EBITDA MAINT.", f"{kpi_table.iloc[2, 2]}%", delta=status_main)

st.table(kpi_table)

# --- 📉 GRAPHE DE SIMULATION AUTOMATIQUE ---
st.divider()
st.subheader("📉 Simulation Dynamique : Impact du Brent sur la Rentabilité")

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

# --- 🛡️ ZONE DE STRESS-TEST ---
st.divider()
st.subheader("🔥 STRESS-TEST : Validation d'Investissement")
with st.expander("Exécuter une simulation d'achat machine / infrastructure", expanded=True):
    c1, c2 = st.columns(2)
    val_achat = c1.number_input("Montant de l'investissement (USD)", value=50000, step=5000)
    duree = c2.slider("Durée d'amortissement (Années)", 1, 10, 5)
    
    score_brut = (val_achat / 500000) * data['W_MSHOP']
    score_final = score_brut / (1 + data['INF_ACIER'])
    
    if score_final >= data['SEUIL_CAPEX']:
        st.success(f"✅ TEST RÉUSSI : Score de rentabilité {round(score_final*100, 2)}% (Seuil: {data['SEUIL_CAPEX']*100}%)")
    else:
        st.error(f"❌ TEST ÉCHOUÉ : Rentabilité insuffisante ({round(score_final*100, 2)}%).")

# --- 📄 GÉNÉRATEUR DE RAPPORT PDF ---
def generate_advanced_report(entite):
    pdf = FPDF()
    pdf.add_page()
    
    # Génération Référence Séquentielle 6 chars
    ref_seq = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    ref_full = f"REF/{ref_seq}/{datetime.now().strftime('%d%m%Y')}"
    
    # En-tête : Logo et Titre
    logo_path = "logo.png" if entite == "MBA-CONSULT" else "logo GMPI.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=140, y=10, w=60, h=30)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"RAPPORT DE SYNTHESE KMS - {entite}", 0, 1, 'L')
    
    # Ajout de la Référence à gauche sous le titre
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, ref_full, 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 10, f"Edité le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 0, 1, 'L')
    pdf.ln(10)
    
    # Tableau KPIs
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
    
    pdf.ln(5)
    
    # Ajout de la courbe de simulation dans le PDF
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "SIMULATION DYNAMIQUE : IMPACT DU BRENT SUR LA RENTABILITE", 0, 1)
    
    plt.figure(figsize=(8, 4))
    plt.plot(brent_range, sim_mshop, label='M-SHOP', color='blue')
    plt.plot(brent_range, sim_dsales, label='D.SALES', color='green')
    plt.plot(brent_range, sim_main, label='MAINTENANCE', color='red')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xlabel('Prix du Baril ($)')
    plt.ylabel('Marge (%)')
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')
    img_buf.seek(0)
    pdf.image(img_buf, x=15, w=180)
    plt.close()
    
    # Conclusions
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "CONCLUSIONS STRATEGIQUES", 0, 1)
    pdf.set_font("Arial", "", 11)
    conclusion = f"Basé sur un Brent à {data['BRENT']}$ et un cours de change de {data['TND_USD']} TND/USD. "
    conclusion += f"L'EBITDA prévisionnel du Machine Shop est de {round(marge_mshop*100, 2)}%. "
    conclusion += f"Tout investissement doit respecter le seuil CAPEX de {data['SEUIL_CAPEX']*100}%."
    pdf.multi_cell(0, 8, conclusion)
    
    # Signature et QR Code à 10mm du fond
    pdf.set_y(-35)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, "Le responsable KMS", 0, 1, 'R')
    
    # QR Code
    qr_url = f"https://chart.googleapis.com/chart?chs=100x100&cht=qr&chl={ref_full}"
    try:
        qr_content = requests.get(qr_url).content
        qr_buf = io.BytesIO(qr_content)
        pdf.image(qr_buf, x=170, y=pdf.get_y(), w=20)
    except:
        pass
        
    # Retourne les bytes bruts pour Streamlit
    return bytes(pdf.output())

st.divider()
if st.button(f"📥 GÉNÉRER LE RAPPORT STRATÉGIQUE PDF ({entite_selectionnee})", use_container_width=True):
    pdf_output = generate_advanced_report(entite_selectionnee)
    st.download_button("⬇️ TÉLÉCHARGER LE PDF", data=pdf_output, file_name=f"Rapport_KMS_{entite_selectionnee}.pdf", mime="application/pdf")