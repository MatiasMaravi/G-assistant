import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from fpdf import FPDF
from datetime import datetime
from dateutil import parser
from io import BytesIO
import locale
import json
locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')

with open("consumo.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

'''
API_URL = "http://localhost:8000/dashboard-semanal"

@st.cache_data(ttl=300)
def obtener_datos():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al obtener datos del servidor: {e}")
        return None

json_data = obtener_datos()

if not json_data:
    st.stop()

'''

# === Procesar datos ===
datos = []
for item in json_data["todos_los_consumos"]:
    fecha = parser.parse(item["fecha"])
    #fecha = datetime.strptime(item["fecha"], "%a, %d %b %Y %H:%M:%S %z (%Z)")
    datos.append({
        "Fecha": fecha,
        "Comercio": item["empresa"],
        "Monto (S/.)": item["monto_numerico"],
        "Categoría": item["categoria"],
        "Tipo de Tarjeta": item["tipo_tarjeta"],
        "Justificación": item["justificacion"],
        "Leído": item["leido"]
    })

df = pd.DataFrame(datos)
# Parsear la fecha y quitar zona horaria
df["Fecha"] = pd.to_datetime(df["Fecha"], format="%a, %d %b %Y %H:%M:%S", utc=True)
df["Fecha"] = df["Fecha"].dt.tz_localize(None)  # Eliminar zona horaria

periodo_raw = json_data['metadata']['periodo_datos']
periodo_dt = datetime.fromisoformat(periodo_raw.replace("Z", ""))  # quitar la Z que indica UTC

# Formatear como quieras mostrarlo, por ejemplo:
periodo_legible = periodo_dt.strftime("%d/%m/%Y %H:%M")

# === Dashboard Streamlit ===
st.set_page_config(page_title="Dashboard Financiero", layout="centered")
st.title("📊 Dashboard Financiero")

st.markdown(f"🗓️ **Periodo de datos:** {periodo_legible}")
st.markdown(f"💳 **Total de consumos:** {json_data['metadata']['total_consumos']}")
st.markdown(f"💰 **Total gastado:** S/ {json_data['metadata']['total_gastado']:.2f}")
st.markdown("---")

# Gráfico de pastel por categoría
st.subheader("🥧 Gasto por categoría")
gasto_por_categoria = df.groupby("Categoría")["Monto (S/.)"].sum()
fig1, ax1 = plt.subplots()
ax1.pie(gasto_por_categoria, labels=gasto_por_categoria.index, autopct='%1.1f%%', startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# Gráfico de barras por día
st.subheader("📅 Gasto por día")
gasto_por_dia = df.groupby(df["Fecha"].dt.strftime('%d-%b'))["Monto (S/.)"].sum()
fig2, ax2 = plt.subplots()
gasto_por_dia.plot(kind='bar', ax=ax2, color="#34a853")
ax2.set_ylabel("Monto (S/.)")
ax2.set_xlabel("Fecha")
ax2.set_title("Gasto diario")
st.pyplot(fig2)

# Tabla resumen por categoría
st.subheader("📋 Resumen por categoría")
st.dataframe(gasto_por_categoria.reset_index().rename(columns={"Monto (S/.)": "Total (S/.)"}))

# Tabla detallada
st.subheader("🧾 Detalle de gastos")
st.dataframe(df.sort_values("Fecha"))

st.markdown("---")

# Descargar como Excel
st.subheader("⬇️ Descargar datos")
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Detalle', index=False)
    pd.DataFrame(gasto_por_categoria).reset_index().to_excel(writer, sheet_name='Resumen', index=False)

st.download_button(
    label="📥 Descargar Excel",
    data=excel_buffer.getvalue(),
    file_name="reporte_gastos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Descargar como PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Resumen de Gastos", 0, 1, "C")

    def categoria_table(self, resumen):
        self.set_font("Arial", "", 12)
        for idx, row in resumen.iterrows():
            self.cell(100, 10, row["Categoría"], 1)
            self.cell(40, 10, f"S/ {row['Total (S/.)']:.2f}", 1, ln=True)

resumen_df = gasto_por_categoria.reset_index().rename(columns={"Monto (S/.)": "Total (S/.)"})
pdf = PDF()
pdf.add_page()
# Obtener la fecha ISO del JSON
fecha_iso = json_data['metadata']['periodo_datos']  # "2025-07-19T23:07:38.773Z"

# Convertir la fecha ISO a datetime y formatearla
fecha_dt = datetime.strptime(fecha_iso.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
fecha_formateada = fecha_dt.strftime("%d de %B de %Y")  # Ejemplo: "19 de julio de 2025"
pdf.set_font("Arial", "", 12)
pdf.cell(0, 10, f"Periodo: {fecha_formateada}", ln=True)
pdf.cell(0, 10, f"Gasto Total: S/ {json_data['metadata']['total_gastado']:.2f}", ln=True)
pdf.ln(10)
pdf.categoria_table(resumen_df)

pdf_bytes = pdf.output(dest='S').encode('latin1')

st.download_button(
    label="📄 Descargar PDF",
    data=pdf_bytes,
    file_name="resumen_gastos.pdf",
    mime="application/pdf"
)
