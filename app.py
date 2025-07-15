import streamlit as st
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Přístup ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = {
    "type": "service_account",
    "client_email": st.secrets["gspread"]["email"],
    "private_key": st.secrets["gspread"]["private_key"].replace('\\n', '\n'),
}
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(st.secrets["gspread"]["sheet"])

# Načíst přihlašovací údaje
access_df = pd.DataFrame(sheet.worksheet("access").get_all_records())
data_ws = sheet.worksheet("data")

# Přihlašování
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Přihlášení")
    username = st.text_input("Uživatelské jméno")
    password = st.text_input("Heslo", type="password")
    if st.button("Přihlásit se"):
        user = access_df[(access_df["username"] == username) & (access_df["password"] == password)]
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Přihlášení úspěšné")
            #st.experimental_rerun()
        else:
            st.error("Neplatné jméno nebo heslo")
else:
    st.title(f"Vítej, {st.session_state.username}")

    # Záznam o odběru
    with st.form("novy_odber"):
        place = st.text_input("Místo odběru")
        date = st.date_input("Datum odběru")
        submitted = st.form_submit_button("Uložit záznam")
        if submitted:
            data_ws.append_row([st.session_state.username, str(date), place])
            st.success("Záznam uložen")

    # Statistiky
    data_df = pd.DataFrame(data_ws.get_all_records())
    user_data = data_df[data_df["username"] == st.session_state.username]
    user_data["date"] = pd.to_datetime(user_data["date"])
    if not user_data.empty:
        last_donation = user_data["date"].max()
        next_possible = last_donation + timedelta(weeks=10)
        st.subheader("Statistiky")
        st.write(f"Počet odběrů: {len(user_data)}")
        st.write(f"Poslední odběr: {last_donation.date()}")
        st.write(f"Další možný odběr: {next_possible.date()}")
    else:
        st.info("Zatím nemáte žádný záznam.")

    if st.button("Odhlásit se"):
        st.session_state.logged_in = False
        #st.experimental_rerun()
