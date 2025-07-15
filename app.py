import streamlit as st
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Konfigurace přístupu ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Vytvoření credentials z tajných údajů
creds_dict = {
    "type": "service_account",
    "project_id": st.secrets["gspread"]["project_id"],
    "private_key_id": st.secrets["gspread"]["private_key_id"],
    "private_key": st.secrets["gspread"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["gspread"]["client_email"],
    "client_id": st.secrets["gspread"]["client_id"],
    "auth_uri": st.secrets["gspread"]["auth_uri"],
    "token_uri": st.secrets["gspread"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gspread"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gspread"]["client_x509_cert_url"]
}

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(st.secrets["gspread"]["sheet"])

# Přístup k jednotlivým listům
access_df = pd.DataFrame(sheet.worksheet("access").get_all_records())
data_ws = pd.DataFrame(sheet.worksheet("data").get_all_records())

# Přihlašování
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:
    params = st.query_params

    st.title("Přihlášení")
    username = st.text_input("Uživatelské jméno")
    password = st.text_input("Heslo", type="password")
    if st.button("Přihlásit se"):
        user = access_df[(access_df["username"] == username) & (access_df["password"] == password)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Přihlášení úspěšné")
            st.rerun()
            
        else:
            st.error("Neplatné jméno nebo heslo")
else:
    params = st.query_params

    st.title(f"Vítej, {st.session_state.username}")

    # Formulář pro nový odběr
    with st.form("novy_odber"):
        place = st.text_input("Místo odběru")
        date = st.date_input("Datum odběru")
        submitted = st.form_submit_button("Uložit záznam")
        if submitted:
            if place.strip() == "":
                st.error("Zadej místo odběru")
            else:
                today = datetime.today().date()
                sheet.worksheet("data").append_row([st.session_state.username, place, str(today)])
                st.success("Záznam uložen")

    # Statistiky
    records = sheet.worksheet("data").get_all_records()
    if not records:
        st.info("Zatím nejsou žádná data.")
    else:
        data_df = pd.DataFrame(records)
        user_data = data_df[data_df["username"] == st.session_state.username]
        user_data["date"] = pd.to_datetime(user_data["date"], errors='coerce')
        user_data = user_data.dropna(subset=["date"])
        
        if not user_data.empty:
            last_donation = user_data["date"].max()
            next_possible = last_donation + timedelta(weeks=10)
            st.subheader("Statistiky")
            st.write(f"Počet odběrů: {len(user_data)}")
            st.write(f"Poslední odběr: {last_donation.date()}")
            st.write(f"Další možný odběr: {next_possible.date()}")
            awards = [
                {"emoji": "🩸", "name": "Krůpěj krve", "needed": 1},
                {"emoji": "🥉", "name": "Bronzová medaile Jana Janského", "needed": 10},
                {"emoji": "🥈", "name": "Stříbrná medaile Jana Janského", "needed": 20},
                {"emoji": "🥇", "name": "Zlatá medaile Jana Janského", "needed": 40},
                {"emoji": "✝️", "name": "Zlatý kříž ČČK 3. třídy", "needed": 80},
                {"emoji": "✝️", "name": "Zlatý kříž ČČK 2. třídy", "needed": 120},
                {"emoji": "✝️", "name": "Zlatý kříž ČČK 1. třídy", "needed": 160},
                {"emoji": "🏅", "name": "Plaketa ČČK Dar života", "needed": 250},
            ]

            total_donations = len(user_data)  # počet odběrů uživatele
            
            st.title("Ocenění dárců krve a tvůj postup")
            
            cols = st.columns(2)
            
            for i, award in enumerate(awards):
                col = cols[i % 2]
            
                with col:
                    #st.image(award["img"], width=50)
                    st.markdown(f"### {award['emoji']} {award['name']}")
            
                    remaining = max(0, award["needed"] - total_donations)
                    progress = min(total_donations / award["needed"], 1.0)
            
                    if progress == 1.0:
                        st.success("🎉 Ocenění splněno!")
                    else:
                        st.info(f"Zbývá {remaining} odběrů")
            
                    st.progress(progress)
                    st.markdown("---")
        else:
            st.info("Nemáte žádný validní záznam.")

    if st.button("Odhlásit se"):
        st.session_state.logged_in = False
        st.rerun()
