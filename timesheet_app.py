import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Trasformatore Timesheet", layout="wide")
st.title("🗂️ Trasformatore Timesheet Mensile")

uploaded_file = st.file_uploader("Carica il file Excel (.xlsx) con il foglio 'Entries'", type="xlsx")

def trasforma_timesheet(file):
    xls = pd.ExcelFile(file)
    df = pd.read_excel(xls, sheet_name="Entries")

    # Selezione colonne e creazione colonna "Nome"
    df = df[['First Name', 'Last Name', 'Date', 'Regular']].copy()
    df['Nome'] = df['First Name'] + " " + df['Last Name']
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # Raggruppa ore lavorate per Nome e Giorno
    df_grouped = df.groupby(['Nome', 'Date'])['Regular'].sum().reset_index()

    # Crea lista di tutte le date del mese
    prima_data = min(df_grouped['Date'])
    mese_anno = prima_data.replace(day=1)
    fine_mese = pd.date_range(start=mese_anno, periods=1, freq='M')[0].date()
    date_mese = pd.date_range(start=mese_anno, end=fine_mese).date

    # Crea tabella pivot con 0.0 nei giorni mancanti
    df_pivot = (
        df_grouped
        .pivot(index='Nome', columns='Date', values='Regular')
        .reindex(columns=date_mese, fill_value=0.0)
    )

    # Riempie eventuali NaN
    df_pivot = df_pivot.fillna(0.0)

    # Calcola la somma delle ore
    df_pivot['Ore Totali'] = df_pivot.sum(axis=1)

    # Formatta i numeri con virgola
    df_pivot = df_pivot.applymap(lambda x: f"{x:.2f}".replace('.', ','))

    return df_pivot

# Interfaccia utente
if uploaded_file:
    try:
        df_result = trasforma_timesheet(uploaded_file)
        st.success("✅ Timesheet trasformato con successo!")
        st.dataframe(df_result, use_container_width=True)

        # Esportazione del file Excel
        output = io.BytesIO()
        df_result.to_excel(output, index=True)
        output.seek(0)
        st.download_button(
            label="📥 Scarica il file trasformato",
            data=output,
            file_name="Timesheet_Trasformato.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"❌ Errore nella trasformazione: {e}")
