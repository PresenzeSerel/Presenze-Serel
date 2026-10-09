import streamlit as st
import pandas as pd
import datetime
import json
import math
import os
from datetime import date

# Set page config
st.set_page_config(
    page_title="SEREL srl - Gestione Presenze & Cantieri - SEREL srl",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for SEREL srl Branding & Catchy UI
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary-color: #1E3B8A;
        --secondary-color: #2563EB;
        --accent-color: #D97706;
        --bg-light: #F8FAFC;
        --text-dark: #0F172A;
    }
    
    /* Top Header Banner */
    .serel-header {
        background: linear-gradient(135deg, #1E3B8A 0%, #1E293B 100%);
        padding: 20px 25px;
        border-radius: 14px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(30, 59, 138, 0.25);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .serel-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #FFFFFF;
        margin: 0;
        padding: 0;
    }
    .serel-subtitle {
        font-size: 14px;
        color: #F59E0B;
        font-weight: 600;
        margin-top: 4px;
    }
    .serel-logo-badge {
        background-color: #F59E0B;
        color: #1E3B8A;
        font-weight: 900;
        font-size: 22px;
        padding: 8px 18px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Custom Sidebar Header */
    .sidebar-brand {
        text-align: center;
        padding: 15px 10px;
        background: #1E3B8A;
        border-radius: 10px;
        color: white;
        margin-bottom: 15px;
    }
    
    /* Cards for Reparti and Dipendenti */
    .stExpander {
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
        margin-bottom: 12px !important;
    }
    
    /* Button Styling */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# File Paths
DATA_FILE = "presenze_db.json"
CANTIERI_FILE = "cantieri_db.json"
PASSWORDS_FILE = "passwords_db.json"
DIPENDENTI_FILE = "dipendenti_db.json"

# Default Cantieri
DEFAULT_CANTIERI = {
    "Sede Centrale / Ufficio": {"lat": 40.8518, "lon": 14.2681, "address": "Sede Aziendale SEREL srl - Via Nuova Poggioreale"},
    "Cantiere Napoli Centro": {"lat": 40.8359, "lon": 14.2488, "address": "Via Toledo, Napoli"},
    "Cantiere Caserta Industriale": {"lat": 41.0821, "lon": 14.3342, "address": "Zona Industriale, Caserta"},
    "Cantiere Salerno Porto": {"lat": 40.6780, "lon": 14.7557, "address": "Area Portuale, Salerno"},
    "Cantiere Pozzuoli": {"lat": 40.8231, "lon": 14.1221, "address": "Pozzuoli (NA)"},
    "Depositi / Magazzino": {"lat": 40.8700, "lon": 14.2900, "address": "Magazzino Principale SEREL"}
}

# Default 24 Dipendenti
DEFAULT_DIPENDENTI = {
    "Ufficio": [
        "Sorbolino Francesco", "Iacovelli Ivan", "Testa Maria Concetta", 
        "Dordei Alfredo", "Amato Simonetti"
    ],
    "Metalmeccanici Operai": [
        "De Risi Giovanni", "Fusco Felice", "Rendina Carlo", "Del Sorbo Raffaele", 
        "Pizza Michele", "Pietro De Crescenzo", "Ferrante Gennaro", "Pepe Saverio"
    ],
    "Magazziniere Autista": [
        "Luigi Esposito", "Miranda Giovanni"
    ],
    "Edili Operai": [
        "Boemio Antonio", "Boemio Raffaele", "Nannino Massimo", "Dounbia Issa", 
        "Donnarumma Ciro", "Picaro Gianluca Salvatore", "Antonio Del Mastro", 
        "Titas Ciro", "El Hayt Farid"
    ]
}

# Default Passwords
DEFAULT_PASSWORDS = {
    "_admin_": "admin2026",
    "_capocantiere_": "cantiere2026"
}

FESTIVI_2026 = [
    "2026-01-01", "2026-01-06", "2026-04-05", "2026-04-06", "2026-04-25",
    "2026-05-01", "2026-06-02", "2026-08-15", "2026-11-01", "2026-12-08",
    "2026-12-25", "2026-12-26"
]

def load_data(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_data(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Load databases
db_presenze = load_data(DATA_FILE, {})
db_cantieri = load_data(CANTIERI_FILE, DEFAULT_CANTIERI)
db_dipendenti = load_data(DIPENDENTI_FILE, DEFAULT_DIPENDENTI)
db_passwords = load_data(PASSWORDS_FILE, DEFAULT_PASSWORDS)

# Dynamic list of all dipendenti
ALL_DIPENDENTI = [d for sub in db_dipendenti.values() for d in sub]

# Ensure password entries
updated_pass = False
for d in ALL_DIPENDENTI:
    if d not in db_passwords:
        db_passwords[d] = "12345"
        updated_pass = True
if updated_pass:
    save_data(PASSWORDS_FILE, db_passwords)

def get_day_info(dt):
    dt_str = dt.strftime("%Y-%m-%d")
    is_weekend = dt.weekday() in [5, 6]
    is_holiday = dt_str in FESTIVI_2026
    day_name = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"][dt.weekday()]
    return dt_str, day_name, is_weekend, is_holiday

# ---------------------------------------------------------
# HEADER AZIENDALE SEREL SRL
# ---------------------------------------------------------
st.markdown("""
<div class="serel-header">
    <div>
        <div class="serel-title">SEREL S.R.L.</div>
        <div class="serel-subtitle">🏗️ Gestione Integrata Presenze, Cantieri & Timbrature GPS</div>
    </div>
    <div class="serel-logo-badge">SEREL</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SISTEMA DI LOGIN E AUTENTICAZIONE
# ---------------------------------------------------------
st.sidebar.markdown("""
<div class="sidebar-brand">
    <h3 style="margin:0; padding:0; color:#F59E0B;">SEREL srl</h3>
    <small>Portale Presenze Digital</small>
</div>
""", unsafe_allow_html=True)

if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "logged_user" not in st.session_state:
    st.session_state["logged_user"] = None

if st.session_state["user_role"] is None:
    st.info("🔐 **Accesso Riservato Personale**: Seleziona il tuo profilo di accesso per procedere.")
    
    col_l1, col_l2, col_l3 = st.columns(3)
    
    with col_l1:
        st.subheader("👑 Amministratore")
        pass_admin = st.text_input("Password Amministratore:", type="password", key="login_admin_p")
        if st.button("Accedi come Amministratore", type="primary", use_container_width=True):
            if pass_admin == db_passwords.get("_admin_", "admin2026"):
                st.session_state["user_role"] = "Admin"
                st.session_state["logged_user"] = "Amministratore"
                st.rerun()
            else:
                st.error("❌ Password Amministratore errata.")

    with col_l2:
        st.subheader("👷 Capocantiere")
        pass_capo = st.text_input("Password Capocantiere:", type="password", key="login_capo_p")
        if st.button("Accedi come Capocantiere", use_container_width=True):
            if pass_capo == db_passwords.get("_capocantiere_", "cantiere2026"):
                st.session_state["user_role"] = "Capocantiere"
                st.session_state["logged_user"] = "Capocantiere"
                st.rerun()
            else:
                st.error("❌ Password Capocantiere errata.")

    with col_l3:
        st.subheader("👤 Singolo Dipendente")
        if ALL_DIPENDENTI:
            dip_login = st.selectbox("Seleziona il tuo Nome:", ALL_DIPENDENTI)
            pass_dip = st.text_input("Inserisci la tua Password:", type="password", key="login_dip_p")
            if st.button("Accedi come Dipendente", use_container_width=True):
                correct_pass = db_passwords.get(dip_login, "12345")
                if pass_dip == correct_pass:
                    st.session_state["user_role"] = "Dipendente"
                    st.session_state["logged_user"] = dip_login
                    st.rerun()
                else:
                    st.error("❌ Password errata per il dipendente selezionato.")
        else:
            st.warning("Nessun dipendente registrato nell'organigramma.")

    st.stop()

# Logout button
st.sidebar.markdown(f"**Utente Connesso:** `{st.session_state['logged_user']}`")
st.sidebar.caption(f"Ruolo: **{st.session_state['user_role']}**")
if st.sidebar.button("🚪 Disconnetti / Logout", use_container_width=True):
    st.session_state["user_role"] = None
    st.session_state["logged_user"] = None
    st.rerun()

# ---------------------------------------------------------
# PROFILO DIPENDENTE (VISTA LIMITATA ED ESCLUSIVA)
# ---------------------------------------------------------
if st.session_state["user_role"] == "Dipendente":
    dipendente_attuale = st.session_state["logged_user"]
    reparto_attuale = "Generale"
    for r, l in db_dipendenti.items():
        if dipendente_attuale in l:
            reparto_attuale = r
            break
    
    st.subheader(f"👤 Scheda Presenza Personale: **{dipendente_attuale}**")
    st.caption(f"Azienda: **SEREL srl** | Reparto: **{reparto_attuale}**")
    st.markdown("---")
    
    dt_today = st.date_input("Seleziona Data di Registrazione/Modifica:", value=date.today())
    dt_str, day_name, is_weekend, is_holiday = get_day_info(dt_today)
    
    if is_holiday or is_weekend:
        st.warning(f"🔴 **{day_name} {dt_str}** - Giorno Festivo / Weekend (Registrazione Straordinario/Festivo)")
    else:
        st.success(f"🟢 **{day_name} {dt_str}** - Giorno Lavorativo Ordinario")
    
    prev_record = db_presenze.get(dt_str, {}).get(dipendente_attuale, {})
    has_submitted = bool(prev_record)
    if has_submitted:
        st.warning("🔒 **Scheda già registrata per questa data**: Le modifiche e le correzioni possono essere effettuate esclusivamente dall'Amministratore. Di seguito sono riportati i dati inseriti.")
    
    col1, col2 = st.columns(2)
    with col1:
        cant_list = list(db_cantieri.keys())
        prev_cant = prev_record.get("cantiere", cant_list[0])
        idx_cant = cant_list.index(prev_cant) if prev_cant in cant_list else 0
        cantiere_scelto = st.selectbox("📍 Cantiere di Lavoro:", cant_list, index=idx_cant)
        
        info_cant = db_cantieri.get(cantiere_scelto, {"lat": 40.8518, "lon": 14.2681, "address": "N.D."})
        st.caption(f"Indirizzo Cantiere: **{info_cant.get('address', '')}**")
        
    with col2:
        stati = ["Presente (8h)", "Ferie", "Permesso", "Malattia", "Infortunio"]
        prev_st = prev_record.get("stato", "Presente (8h)")
        idx_st = stati.index(prev_st) if prev_st in stati else 0
        stato_scelto = st.selectbox("📋 Stato Presenza:", stati, index=idx_st)

    st.markdown("---")
    st.subheader("📍 Timbratura Georeferenziata GPS (Ingresso / Uscita)")
    
    t_type = st.radio("Azione Timbratura:", ["🏁 Timbra Ingresso Cantiere", "🚪 Timbra Uscita Cantiere"], horizontal=True)
    
    c_lat, c_lon = st.columns(2)
    user_lat = c_lat.number_input("Latitudine GPS Rilevata:", value=float(info_cant['lat']), format="%.6f")
    user_lon = c_lon.number_input("Longitudine GPS Rilevata:", value=float(info_cant['lon']), format="%.6f")
    
    distanza = haversine_distance(user_lat, user_lon, info_cant['lat'], info_cant['lon'])
    in_range = distanza <= 200
    
    st.write(f"📏 Distanza calcolata dal cantiere SEREL: **{int(distanza)} metri**")
    if in_range:
        st.success("✅ **Posizione Conforme**: Ti trovi all'interno del cantiere!")
    else:
        st.warning("⚠️ **Fuori Cantiere**: Attenzione, distanza superiore a 200m.")
        
    timb_gps = prev_record.get("timbratura_gps", {})
    
    if st.button("📲 REGISTRA TIMBRATURA GPS ORA", type="primary"):
        ora_attuale = datetime.datetime.now().strftime("%H:%M:%S")
        if "Ingresso" in t_type:
            timb_gps["ingresso"] = {
                "ora": ora_attuale, "lat": user_lat, "lon": user_lon,
                "distanza_m": int(distanza), "esito": "OK - In Cantiere" if in_range else "ALLARME - Fuori Cantiere"
            }
        else:
            timb_gps["uscita"] = {
                "ora": ora_attuale, "lat": user_lat, "lon": user_lon,
                "distanza_m": int(distanza), "esito": "OK - In Cantiere" if in_range else "ALLARME - Fuori Cantiere"
            }
            
        if dt_str not in db_presenze:
            db_presenze[dt_str] = {}
        if dipendente_attuale not in db_presenze[dt_str]:
            db_presenze[dt_str][dipendente_attuale] = {
                "reparto": reparto_attuale, "cantiere": cantiere_scelto, "stato": stato_scelto,
                "straordinario": 0, "trasferta": True, "acconto": 0
            }
        db_presenze[dt_str][dipendente_attuale]["timbratura_gps"] = timb_gps
        save_data(DATA_FILE, db_presenze)
        st.success(f"🎉 Timbratura registrata con successo alle ore {ora_attuale}!")

    ing_ora = timb_gps.get("ingresso", {}).get("ora", "Non ancora timbrato")
    usc_ora = timb_gps.get("uscita", {}).get("ora", "Non ancora timbrato")
    
    st.info(f"⏱️ **Orario Ingresso Registrato**: {ing_ora} | ⏱️ **Orario Uscita Registrato**: {usc_ora}")

    st.markdown("---")
    st.subheader("⏱️ Dichiarazione e Correzione Ore Lavorate")
    
    col_h1, col_h2, col_h3 = st.columns(3)
    prev_str = float(prev_record.get("straordinario", 0.0))
    ore_ord = col_h1.number_input("Ore Ordinarie:", min_value=0.0, max_value=8.0, value=8.0 if "Presente" in stato_scelto else 0.0, step=0.5)
    ore_str = col_h2.number_input("Ore Straordinario:", min_value=0.0, max_value=12.0, value=prev_str, step=0.5)
    flag_trasf = col_h3.checkbox("Diritto a Trasferta Cantiere", value=prev_record.get("trasferta", True))

    if ing_ora != "Non ancora timbrato" and usc_ora != "Non ancora timbrato":
        try:
            t1 = datetime.datetime.strptime(ing_ora, "%H:%M:%S")
            t2 = datetime.datetime.strptime(usc_ora, "%H:%M:%S")
            diff_ore = (t2 - t1).total_seconds() / 3600.0
            tot_dichiarato = ore_ord + ore_str
            
            st.write(f"📊 Tempo trascorso tra Ingresso e Uscita: **{diff_ore:.2f} ore** | Totale Dichiarato: **{tot_dichiarato:.2f} ore**")
            if abs(diff_ore - tot_dichiarato) > 0.5:
                st.warning("⚠️ **Attenzione**: Le ore totali dichiarate differiscono dall'orario di timbratura GPS registrato.")
            else:
                st.success("✅ **Coincidenza Verificata**: Ore dichiarate in linea con la timbratura GPS!")
        except Exception:
            pass

    if has_submitted:
        st.info("🔒 **Registrazione Bloccata**: Se hai riscontrato un errore nel caricamento, contatta l'Amministratore per effettuare la correzione.")
    else:
        if st.button("💾 Invia Presenza del Giorno", type="primary", use_container_width=True):
            if dt_str not in db_presenze:
                db_presenze[dt_str] = {}
                
            db_presenze[dt_str][dipendente_attuale] = {
                "reparto": reparto_attuale,
                "cantiere": cantiere_scelto,
                "stato": stato_scelto,
                "straordinario": ore_str,
                "trasferta": flag_trasf,
                "acconto": prev_record.get("acconto", 0),
                "timbratura_gps": timb_gps
            }
            save_data(DATA_FILE, db_presenze)
            st.success("✅ Scheda presenze registrata con successo! I dati sono stati trasmessi all'ufficio SEREL srl.")
            st.rerun()

    st.stop()

# ---------------------------------------------------------
# MENU PER AMMINISTRATORE E CAPOCANTIERE
# ---------------------------------------------------------
menu_options = [
    "📲 Compilazione Presenze Giorno",
    "📍 Timbratura GPS & Mappa Live",
    "🗺️ Mappa Interattiva Cantieri",
    "📊 Storico & Dettaglio Cantieri"
]

if st.session_state["user_role"] == "Admin":
    menu_options.extend([
        "✏️ Modifica & Correzione Registro",
        "🖨️ Report Mese per Consulente",
        "👥 Gestione Organigramma & Dipendenti",
        "🔑 Gestione Passwords & Accessi",
        "💾 Backup & Ripristino Database",
        "⚙️ Gestione Cantieri & GPS"
    ])

menu = st.sidebar.radio("Seleziona Funzione:", menu_options)

# -----------------------------------------------------------------
# MENU 1: COMPILAZIONE PRESENZE GIORNO (TUTTA LA SQUADRA)
# -----------------------------------------------------------------
if menu == "📲 Compilazione Presenze Giorno":
    st.subheader("📲 Inserimento Presenze e Cantiere della Squadra SEREL")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        data_sel = st.date_input("Seleziona Data:", value=date.today())
        dt_str, day_name, is_weekend, is_holiday = get_day_info(data_sel)
        
        if is_holiday or is_weekend:
            st.error(f"🔴 **{day_name} {dt_str}** - FESTIVO / WEEKEND")
        else:
            st.success(f"🟢 **{day_name} {dt_str}** - Giorno Lavorativo Ordinario")
            
    with col2:
        cantiere_default = st.selectbox("Cantiere Rapido (Applica a tutti se selezionato):", ["-- Seleziona Singolarmente --"] + list(db_cantieri.keys()))

    st.markdown("---")
    
    new_records = {}
    record_esistente = db_presenze.get(dt_str, {})

    for reparto, lista_dip in db_dipendenti.items():
        with st.expander(f"📁 **Reparto: {reparto}** ({len(lista_dip)} Lavoratori)", expanded=True):
            for dip in lista_dip:
                st.markdown(f"**👤 {dip}**")
                c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1, 1])
                
                prev_dip = record_esistente.get(dip, {})
                
                cant_list = list(db_cantieri.keys())
                default_c_idx = 0
                if prev_dip.get("cantiere") in cant_list:
                    default_c_idx = cant_list.index(prev_dip.get("cantiere"))
                elif cantiere_default != "-- Seleziona Singolarmente --":
                    default_c_idx = cant_list.index(cantiere_default)
                    
                cant = c1.selectbox(f"Cantiere ({dip})", cant_list, index=default_c_idx, key=f"cant_{dip}_{dt_str}", label_visibility="collapsed")
                
                stati = ["Presente (8h)", "Ferie", "Permesso", "Malattia", "Infortunio", "Assente"]
                prev_stat = prev_dip.get("stato", "Presente (8h)")
                stat_idx = stati.index(prev_stat) if prev_stat in stati else 0
                stato = c2.selectbox(f"Stato ({dip})", stati, index=stat_idx, key=f"stat_{dip}_{dt_str}", label_visibility="collapsed")
                
                prev_straord = float(prev_dip.get("straordinario", 0.0))
                straord = c3.number_input("Ore Straord.", min_value=0.0, max_value=12.0, value=prev_straord, step=0.5, key=f"str_{dip}_{dt_str}")
                
                prev_trasf = prev_dip.get("trasferta", False)
                trasferta = c4.checkbox("Trasferta", value=prev_trasf, key=f"tr_{dip}_{dt_str}")
                
                prev_acc = float(prev_dip.get("acconto", 0.0))
                acconto = c5.number_input("Acconto (€)", min_value=0.0, max_value=2000.0, value=prev_acc, step=10.0, key=f"acc_{dip}_{dt_str}")
                
                new_records[dip] = {
                    "reparto": reparto,
                    "cantiere": cant,
                    "stato": stato,
                    "straordinario": straord,
                    "trasferta": trasferta,
                    "acconto": acconto,
                    "timbratura_gps": prev_dip.get("timbratura_gps", None)
                }

    st.markdown("---")
    if st.button("💾 Salva Presenze della Squadra", type="primary", use_container_width=True):
        db_presenze[dt_str] = new_records
        save_data(DATA_FILE, db_presenze)
        st.success(f"✅ Presenze per il giorno {dt_str} salvate con successo nel database SEREL srl!")

# -----------------------------------------------------------------
# MENU 2: MODIFICA & CORREZIONE REGISTRO (CORREZIONE ERRORI)
# -----------------------------------------------------------------
elif menu == "✏️ Modifica & Correzione Registro":
    st.subheader("✏️ Correzione e Modifica Inserimenti Registrati")
    st.info("💡 **Gestione Errori**: Seleziona la data e il dipendente per correggere cantiere, ore, straordinari, trasferte o timbrature GPS.")
    
    col_e1, col_e2 = st.columns(2)
    dt_corr = col_e1.date_input("Data da Modificare:", value=date.today(), key="corr_dt")
    dt_corr_str = dt_corr.strftime("%Y-%m-%d")
    
    records_giorno = db_presenze.get(dt_corr_str, {})
    
    if not records_giorno:
        st.warning(f"Nessun registro presenze trovato per la data {dt_corr_str}.")
    else:
        dip_corr = col_e2.selectbox("Seleziona Dipendente da Correggere:", list(records_giorno.keys()))
        rec_dip = records_giorno.get(dip_corr, {})
        
        st.markdown(f"### Modifica Registro di: **{dip_corr}** ({dt_corr_str})")
        
        c1, c2, c3 = st.columns(3)
        
        cant_list = list(db_cantieri.keys())
        curr_c = rec_dip.get("cantiere", cant_list[0])
        idx_c = cant_list.index(curr_c) if curr_c in cant_list else 0
        mod_cant = c1.selectbox("Cantiere Assegnato:", cant_list, index=idx_c, key="mod_c")
        
        stati = ["Presente (8h)", "Ferie", "Permesso", "Malattia", "Infortunio", "Assente"]
        curr_s = rec_dip.get("stato", "Presente (8h)")
        idx_s = stati.index(curr_s) if curr_s in stati else 0
        mod_stat = c2.selectbox("Stato Presenza:", stati, index=idx_s, key="mod_s")
        
        mod_straord = c3.number_input("Ore Straordinario:", min_value=0.0, max_value=12.0, value=float(rec_dip.get("straordinario", 0.0)), step=0.5, key="mod_str")
        
        c4, c5 = st.columns(2)
        mod_trasf = c4.checkbox("Trasferta Attiva", value=rec_dip.get("trasferta", False), key="mod_tr")
        mod_acc = c5.number_input("Acconto Errore/Busta (€):", min_value=0.0, max_value=2000.0, value=float(rec_dip.get("acconto", 0.0)), step=10.0, key="mod_acc")
        
        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        
        if col_btn1.button("💾 Salva Correzione Registro", type="primary", use_container_width=True):
            db_presenze[dt_corr_str][dip_corr]["cantiere"] = mod_cant
            db_presenze[dt_corr_str][dip_corr]["stato"] = mod_stat
            db_presenze[dt_corr_str][dip_corr]["straordinario"] = mod_straord
            db_presenze[dt_corr_str][dip_corr]["trasferta"] = mod_trasf
            db_presenze[dt_corr_str][dip_corr]["acconto"] = mod_acc
            
            save_data(DATA_FILE, db_presenze)
            st.success(f"🎉 Registro di {dip_corr} del {dt_corr_str} corretto con successo!")
            st.rerun()
            
        if col_btn2.button("🗑️ Elimina Questa Registrazione", type="secondary", use_container_width=True):
            del db_presenze[dt_corr_str][dip_corr]
            if not db_presenze[dt_corr_str]:
                del db_presenze[dt_corr_str]
            save_data(DATA_FILE, db_presenze)
            st.success(f"🗑️ Registrazione di {dip_corr} eliminata con successo.")
            st.rerun()

# -----------------------------------------------------------------
# MENU 3: TIMBRATURA GPS & MAPPA LIVE
# -----------------------------------------------------------------
elif menu == "📍 Timbratura GPS & Mappa Live":
    st.subheader("📍 Timbratura Georeferenziata GPS Cantiere")
    
    col_a, col_b = st.columns(2)
    with col_a:
        dt_timb = st.date_input("Data Timbratura:", value=date.today())
        dt_str_t, _, _, _ = get_day_info(dt_timb)
    with col_b:
        dip_sel = st.selectbox("Seleziona Lavoratore:", ALL_DIPENDENTI)
        
    cantiere_assegnato = db_presenze.get(dt_str_t, {}).get(dip_sel, {}).get("cantiere", list(db_cantieri.keys())[0])
    st.write(f"Cantiere Assegnato: **{cantiere_assegnato}**")
    
    info_cant = db_cantieri.get(cantiere_assegnato, {"lat": 40.8518, "lon": 14.2681, "address": "N.D."})
    st.caption(f"📍 Coordinate Cantiere SEREL Target: Lat {info_cant['lat']}, Lon {info_cant['lon']} ({info_cant.get('address', '')})")

    st.markdown("---")
    st.write("### ⏱️ Modulo Timbratura Digitale & Posizione GPS")
    
    t_type = st.radio("Tipo Operazione:", ["🏁 Ingresso / Arrivo Cantiere", "🚪 Uscita / Partenza Cantiere"], horizontal=True)
    
    col_lat, col_lon, col_rag = st.columns(3)
    user_lat = col_lat.number_input("Latitudine Rilevata GPS:", value=float(info_cant['lat']), format="%.6f")
    user_lon = col_lon.number_input("Longitudine Rilevata GPS:", value=float(info_cant['lon']), format="%.6f")
    max_dist = col_rag.number_input("Raggio Tolleranza (Metri):", value=200, step=10)
    
    distanza = haversine_distance(user_lat, user_lon, info_cant['lat'], info_cant['lon'])
    in_range = distanza <= max_dist
    
    map_df = pd.DataFrame([
        {"latitude": info_cant['lat'], "longitude": info_cant['lon'], "Punto": "Cantiere Target"},
        {"latitude": user_lat, "longitude": user_lon, "Punto": "Posizione Timbratura"}
    ])
    st.map(map_df, zoom=14)

    st.write(f"📏 Distanza calcolata dal centro cantiere: **{int(distanza)} metri**")
    if in_range:
        st.success("✅ **Posizione Conforme**: Il lavoratore è all'interno del cantiere!")
    else:
        st.warning(f"⚠️ **Fuori Cantiere**: Distanza superiore al raggio di tolleranza di {max_dist}m.")
        
    if st.button("📍 REGISTRA TIMBRATURA ORA", type="primary"):
        ora_attuale = datetime.datetime.now().strftime("%H:%M:%S")
        
        if dt_str_t not in db_presenze:
            db_presenze[dt_str_t] = {}
        if dip_sel not in db_presenze[dt_str_t]:
            rep_found = "Generale"
            for r, l in db_dipendenti.items():
                if dip_sel in l:
                    rep_found = r
                    break
            db_presenze[dt_str_t][dip_sel] = {
                "reparto": rep_found,
                "cantiere": cantiere_assegnato,
                "stato": "Presente (8h)",
                "straordinario": 0,
                "trasferta": True,
                "acconto": 0
            }
            
        timb_log = db_presenze[dt_str_t][dip_sel].get("timbratura_gps", {})
        
        if "Ingresso" in t_type:
            timb_log["ingresso"] = {
                "ora": ora_attuale, "lat": user_lat, "lon": user_lon, 
                "distanza_m": int(distanza), "esito": "OK - In Cantiere" if in_range else "ALLARME - Fuori Cantiere"
            }
        else:
            timb_log["uscita"] = {
                "ora": ora_attuale, "lat": user_lat, "lon": user_lon, 
                "distanza_m": int(distanza), "esito": "OK - In Cantiere" if in_range else "ALLARME - Fuori Cantiere"
            }
            
        db_presenze[dt_str_t][dip_sel]["timbratura_gps"] = timb_log
        save_data(DATA_FILE, db_presenze)
        st.success(f"🎉 Timbratura registrata alle ore {ora_attuale} per {dip_sel}!")

# -----------------------------------------------------------------
# MENU 4: MAPPA INTERATTIVA CANTIERI
# -----------------------------------------------------------------
elif menu == "🗺️ Mappa Interattiva Cantieri":
    st.subheader("🗺️ Mappa Generale Cantieri SEREL srl")
    
    cant_map_data = []
    for nome, data in db_cantieri.items():
        cant_map_data.append({
            "Cantiere": nome,
            "latitude": data["lat"],
            "longitude": data["lon"],
            "Indirizzo": data.get("address", "")
        })
        
    df_cant_map = pd.DataFrame(cant_map_data)
    st.map(df_cant_map, zoom=10, use_container_width=True)
    st.dataframe(df_cant_map[["Cantiere", "Indirizzo", "latitude", "longitude"]], use_container_width=True)

# -----------------------------------------------------------------
# MENU 5: STORICO & DETTAGLIO CANTIERI
# -----------------------------------------------------------------
elif menu == "📊 Storico & Dettaglio Cantieri":
    st.subheader("📊 Storico Registrazioni & Presenze nei Cantieri SEREL")
    
    rows = []
    for d_str, dip_dict in db_presenze.items():
        for dip_n, val in dip_dict.items():
            timb = val.get("timbratura_gps", {})
            ing = timb.get("ingresso", {}).get("ora", "-")
            usc = timb.get("uscita", {}).get("ora", "-")
            esito_gps = timb.get("ingresso", {}).get("esito", "Non Timbrato")
            
            rows.append({
                "Data": d_str,
                "Dipendente": dip_n,
                "Reparto": val.get("reparto", "-"),
                "Cantiere": val.get("cantiere", "-"),
                "Stato": val.get("stato", "-"),
                "Ora Ingresso": ing,
                "Ora Uscita": usc,
                "Verifica GPS": esito_gps,
                "Ore Straordinario": val.get("straordinario", 0),
                "Trasferta": "Sì" if val.get("trasferta") else "No",
                "Acconto (€)": val.get("acconto", 0)
            })
            
    if rows:
        df_hist = pd.DataFrame(rows)
        c_filter1, c_filter2 = st.columns(2)
        cant_f = c_filter1.selectbox("Filtra per Cantiere:", ["Tutti i Cantieri"] + list(db_cantieri.keys()))
        dip_f = c_filter2.selectbox("Filtra per Dipendente:", ["Tutti i Dipendenti"] + ALL_DIPENDENTI)
        
        if cant_f != "Tutti i Cantieri":
            df_hist = df_hist[df_hist["Cantiere"] == cant_f]
        if dip_f != "Tutti i Dipendenti":
            df_hist = df_hist[df_hist["Dipendente"] == dip_f]
            
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Nessuna registrazione salvata.")

# -----------------------------------------------------------------
# MENU 6: REPORT MESE PER CONSULENTE (SOLO ADMIN)
# -----------------------------------------------------------------
elif menu == "🖨️ Report Mese per Consulente":
    st.subheader("🖨️ Prospetto Mensile per Consulente del Lavoro")
    
    col_m, col_y = st.columns(2)
    mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    m_sel = col_m.selectbox("Seleziona Mese:", mesi, index=9)
    m_idx = mesi.index(m_sel) + 1
    
    st.markdown(f"### Elenco Presenze SEREL srl: **{m_sel} 2026**")
    
    rep_data = []
    for rep, dip_l in db_dipendenti.items():
        for dip in dip_l:
            gg_lav = 0
            gg_ferie = 0
            ore_perm = 0
            gg_trasf = 0
            tot_straord = 0.0
            tot_acconti = 0.0
            cantieri_frequentati = set()
            
            for d_str, dip_dict in db_presenze.items():
                try:
                    dt_obj = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                    if dt_obj.month == m_idx and dt_obj.year == 2026:
                        if dip in dip_dict:
                            info = dip_dict[dip]
                            st_val = info.get("stato", "")
                            if "Presente" in st_val:
                                gg_lav += 1
                            elif "Ferie" in st_val:
                                gg_ferie += 1
                            elif "Permesso" in st_val:
                                ore_perm += 8
                                
                            if info.get("trasferta"):
                                gg_trasf += 1
                                
                            tot_straord += float(info.get("straordinario", 0.0))
                            tot_acconti += float(info.get("acconto", 0.0))
                            if info.get("cantiere"):
                                cantieri_frequentati.add(info.get("cantiere"))
                except Exception:
                    pass
                    
            rep_data.append({
                "Reparto": rep,
                "Dipendente": dip,
                "GG Lavorati": gg_lav,
                "GG Ferie": gg_ferie,
                "Ore Permesso": ore_perm,
                "GG Trasferta": gg_trasf,
                "Ore Straordinario": tot_straord,
                "Acconti in Busta (€)": tot_acconti,
                "Cantieri Principali": ", ".join(list(cantieri_frequentati)[:2]) if cantieri_frequentati else "N.D."
            })
            
    df_report = pd.DataFrame(rep_data)
    st.dataframe(df_report, use_container_width=True)
    
    file_out = f"Report_Consulente_SEREL_{m_sel}_2026.xlsx"
    df_report.to_excel(file_out, index=False)
    
    with open(file_out, "rb") as f:
        st.download_button(
            label=f"📥 SCARICA EXCEL SEREL PER CONSULENTE ({m_sel} 2026)",
            data=f,
            file_name=file_out,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

# -----------------------------------------------------------------
# MENU 7: GESTIONE ORGANIGRAMMA & DIPENDENTI (SOLO ADMIN)
# -----------------------------------------------------------------
elif menu == "👥 Gestione Organigramma & Dipendenti":
    st.subheader("👥 Gestione Personale & Organigramma SEREL srl")
    st.info("Aggiungi nuovi operai/impiegati o rimuovi lavoratori dall'organigramma aziendale.")
    
    st.write("### ➕ Aggiungi Nuovo Lavoratore")
    col_n1, col_n2, col_n3 = st.columns(3)
    
    nuovo_nome = col_n1.text_input("Nome e Cognome Lavoratore:")
    reparto_sel = col_n2.selectbox("Seleziona Reparto:", list(db_dipendenti.keys()) + ["+ Crea Nuovo Reparto"])
    if reparto_sel == "+ Crea Nuovo Reparto":
        reparto_sel = col_n2.text_input("Nome Nuovo Reparto:")
        
    pass_inenziale = col_n3.text_input("Password Iniziale Accesso:", value="12345")
    
    if st.button("➕ Aggiungi Lavoratore all'Organigramma", type="primary"):
        if nuovo_nome and reparto_sel:
            if reparto_sel not in db_dipendenti:
                db_dipendenti[reparto_sel] = []
            if nuovo_nome not in db_dipendenti[reparto_sel]:
                db_dipendenti[reparto_sel].append(nuovo_nome)
                save_data(DIPENDENTI_FILE, db_dipendenti)
                
                db_passwords[nuovo_nome] = pass_inenziale
                save_data(PASSWORDS_FILE, db_passwords)
                
                st.success(f"🎉 Lavoratore '{nuovo_nome}' inserito nel reparto '{reparto_sel}' con successo!")
                st.rerun()
            else:
                st.warning("⚠️ Il lavoratore è già presente nell'organigramma.")

    st.markdown("---")
    st.write("### 🗑️ Rimuovi / Elimina Lavoratore")
    col_d1, col_d2 = st.columns([2, 1])
    dip_da_eliminare = col_d1.selectbox("Seleziona Lavoratore da Rimuovere:", ALL_DIPENDENTI)
    
    if col_d2.button("🗑️ Conferma ed Elimina Lavoratore"):
        if dip_da_eliminare:
            for rep, lista in db_dipendenti.items():
                if dip_da_eliminare in lista:
                    lista.remove(dip_da_eliminare)
            save_data(DIPENDENTI_FILE, db_dipendenti)
            
            if dip_da_eliminare in db_passwords:
                del db_passwords[dip_da_eliminare]
                save_data(PASSWORDS_FILE, db_passwords)
                
            st.success(f"🗑️ Lavoratore '{dip_da_eliminare}' rimosso dall'organigramma.")
            st.rerun()

# -----------------------------------------------------------------
# MENU 8: GESTIONE PASSWORDS & ACCESSI (SOLO ADMIN)
# -----------------------------------------------------------------
elif menu == "🔑 Gestione Passwords & Accessi":
    st.subheader("🔑 Gestione Passwords e Credenziali SEREL srl")
    
    st.write("### ⚙️ Password Ruoli Generali")
    col_p1, col_p2 = st.columns(2)
    p_admin_new = col_p1.text_input("Password Amministratore:", value=db_passwords.get("_admin_", "admin2026"), type="password")
    p_capo_new = col_p2.text_input("Password Capocantiere:", value=db_passwords.get("_capocantiere_", "cantiere2026"), type="password")
    
    st.markdown("---")
    st.write("### 👥 Passwords Personali Singoli Dipendenti")
    
    pass_updates = {}
    for rep, lista_dip in db_dipendenti.items():
        with st.expander(f"📁 **Reparto: {rep}**", expanded=True):
            for dip in lista_dip:
                curr_pass = db_passwords.get(dip, "12345")
                p_val = st.text_input(f"🔑 Password per {dip}:", value=curr_pass, key=f"p_dip_{dip}")
                pass_updates[dip] = p_val

    if st.button("💾 Salva Tutte le Passwords", type="primary", use_container_width=True):
        db_passwords["_admin_"] = p_admin_new
        db_passwords["_capocantiere_"] = p_capo_new
        for dip, p in pass_updates.items():
            db_passwords[dip] = p
        save_data(PASSWORDS_FILE, db_passwords)
        st.success("✅ Tutte le password sono state aggiornate con successo nel database!")

# -----------------------------------------------------------------
# MENU 9: BACKUP & RIPRISTINO DATABASE (SOLO ADMIN)
# -----------------------------------------------------------------
elif menu == "💾 Backup & Ripristino Database":
    st.subheader("💾 Backup e Ripristino Dati Database SEREL srl")
    st.info("Scarica un pacchetto di sicurezza completo o ripristina i dati per non perdere mai le informazioni durante aggiornamenti del programma.")
    
    full_backup_data = {
        "presenze": db_presenze,
        "cantieri": db_cantieri,
        "dipendenti": db_dipendenti,
        "passwords": db_passwords,
        "backup_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    backup_json_str = json.dumps(full_backup_data, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="📥 SCARICA DATABASE COMPLETO SEREL (.JSON)",
        data=backup_json_str,
        file_name=f"backup_SEREL_full_{date.today().strftime('%Y%m%d')}.json",
        mime="application/json",
        type="primary"
    )
    
    st.markdown("---")
    st.write("### 📤 Import / Carica Backup Database")
    uploaded_backup = st.file_uploader("Seleziona un file di backup (.json) da ripristinare:", type=["json"])
    
    if uploaded_backup is not None:
        try:
            imported_content = json.load(uploaded_backup)
            if "presenze" in imported_content and "cantieri" in imported_content and "passwords" in imported_content:
                st.write(f"📅 Data creazione backup: **{imported_content.get('backup_date', 'Sconosciuta')}**")
                if st.button("⚠️ CONFERMA RIPRISTINO DATABASE"):
                    save_data(DATA_FILE, imported_content["presenze"])
                    save_data(CANTIERI_FILE, imported_content["cantieri"])
                    save_data(PASSWORDS_FILE, imported_content["passwords"])
                    if "dipendenti" in imported_content:
                        save_data(DIPENDENTI_FILE, imported_content["dipendenti"])
                    st.success("🎉 Database SEREL ripristinato con successo! Ricarico la pagina...")
                    st.rerun()
            else:
                st.error("❌ File di backup non valido (chiavi mancanti).")
        except Exception as e:
            st.error(f"❌ Errore nella lettura del file: {e}")

# -----------------------------------------------------------------
# MENU 10: GESTIONE CANTIERI & GPS
# -----------------------------------------------------------------
elif menu == "⚙️ Gestione Cantieri & GPS":
    st.subheader("⚙️ Anagrafica Cantieri SEREL e Coordinate GPS Target")
    
    st.write("### Cantieri Registrati:")
    df_c = pd.DataFrame([
        {"Nome Cantiere": k, "Latitudine": v["lat"], "Longitudine": v["lon"], "Indirizzo": v.get("address", "")}
        for k, v in db_cantieri.items()
    ])
    st.dataframe(df_c, use_container_width=True)
    
    st.markdown("---")
    st.write("### ➕ Aggiungi Nuovo Cantiere SEREL")
    c1, c2, c3 = st.columns(3)
    n_nome = c1.text_input("Nome Cantiere:")
    n_lat = c2.number_input("Latitudine GPS:", value=40.850000, format="%.6f")
    n_lon = c3.number_input("Longitudine GPS:", value=14.260000, format="%.6f")
    n_ind = st.text_input("Indirizzo / Note Cantiere:")
    
    if st.button("➕ Salva Nuovo Cantiere", type="primary"):
        if n_nome:
            db_cantieri[n_nome] = {"lat": n_lat, "lon": n_lon, "address": n_ind}
            save_data(CANTIERI_FILE, db_cantieri)
            st.success(f"Cantiere '{n_nome}' aggiunto con successo!")
            st.rerun()
