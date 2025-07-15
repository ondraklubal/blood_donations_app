import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import streamlit as st

# Převést tajemství z .secrets na dict
creds_dict = dict(st.secrets["gspread"])

# Gspread potřebuje credentials jako objekt, nikoliv dict
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

gc = gspread.authorize(credentials)

sheet = client.open("blood_donations").sheet1  # název tabulky

def add_donation(username, location, date):
    sheet.append_row([username, location, date])

def get_user_donations(username):
    data = sheet.get_all_records()
    return [row for row in data if row["username"] == username]

# UI
st.title("🩸 Evidence odběrů krve")

if 'username' not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.subheader("Přihlášení")
    username = st.text_input("Uživatelské jméno")
    if st.button("Přihlásit"):
        if username.strip() != "":
            st.session_state.username = username
            st.experimental_rerun()
else:
    st.success(f"Přihlášen jako **{st.session_state.username}**")
    if st.button("Odhlásit se"):
        st.session_state.username = None
        st.experimental_rerun()

    st.subheader("Nový odběr")
    with st.form("add_form"):
        location = st.text_input("Místo darování")
        date = st.date_input("Datum", value=datetime.date.today())
        submitted = st.form_submit_button("Přidat odběr")
        if submitted and location.strip():
            add_donation(st.session_state.username, location.strip(), date.isoformat())
            st.success("Záznam přidán.")
    
    donations = get_user_donations(st.session_state.username)
    if donations:
        st.subheader("Statistika odběrů")
        st.write(f"🔢 Počet odběrů: **{len(donations)}**")
        last_date = datetime.date.fromisoformat(donations[-1]["date"])
        next_possible = last_date + datetime.timedelta(weeks=10)
        st.write(f"🗓 Poslední odběr: **{last_date}**")
        st.write(f"✅ Možný další odběr: **{next_possible}**")

        st.subheader("Historie odběrů")
        for row in donations:
            st.write(f"- {row['date']} – {row['location']}")
    else:
        st.info("Zatím nemáte žádný záznam.")
