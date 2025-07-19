import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import locale
locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')

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
# Tu JSON de ejemplo (normalmente lo traerías desde una API)

json_data = {
    "resumen_gastos_semanales": {
        "periodo": "12 al 19 de julio de 2025",
        "gasto_total_semana": 1097.67,
        "categorias": [
            {
                "nombre": "Compras Online/Tiendas por Departamento",
                "total_categoria": 801.90,
                "detalles": [
                    {"comercio": "DP *Falabellacom", "monto": 352.90, "fecha": "17 de julio"},
                    {"comercio": "DP *Falabellacom", "monto": 449.00, "fecha": "17 de julio"}
                ]
            },
            {
                "nombre": "Supermercado/Tiendas de Conveniencia",
                "total_categoria": 76.50,
                "detalles": [
                    {"comercio": "T2115 MEGA PLAZA", "monto": 29.80, "fecha": "17 de julio"},
                    {"comercio": "T2115 MEGA PLAZA", "monto": 26.80, "fecha": "17 de julio"},
                    {"comercio": "T2115 MEGA PLAZA", "monto": 19.90, "fecha": "17 de julio"}
                ]
            },
            {
                "nombre": "Comida/Restaurantes",
                "total_categoria": 152.00,
                "detalles": [
                    {"comercio": "SHIMAYA RAMEN _ Barranco", "monto": 152.00, "fecha": "15 de julio"}
                ]
            },
            {
                "nombre": "Comida Rápida/Snacks",
                "total_categoria": 27.00,
                "detalles": [
                    {"comercio": "PROBOCA MOLINA", "monto": 13.50, "fecha": "16 de julio"},
                    {"comercio": "PROBOCA MOLINA", "monto": 13.50, "fecha": "14 de julio"}
                ]
            },
            {
                "nombre": "Servicios de Delivery",
                "total_categoria": 31.87,
                "detalles": [
                    {"comercio": "DLC*RAPPI PERU", "monto": 27.19, "fecha": "12 de julio"},
                    {"comercio": "PYU*RAPPI", "monto": 4.68, "fecha": "12 de julio"}
                ]
            },
            {
                "nombre": "Otros/Varios",
                "total_categoria": 7.40,
                "detalles": [
                    {"comercio": "TAMBO UTEC", "monto": 7.40, "fecha": "19 de julio"}
                ]
            }
        ]
    }
}

# Procesar datos
categorias = json_data["resumen_gastos_semanales"]["categorias"]
datos = []

for cat in categorias:
    for item in cat["detalles"]:
        fecha_str = item["fecha"] + " 2025"
        fecha = datetime.strptime(fecha_str, "%d de %B %Y")
        datos.append({
            "Fecha": fecha,
            "Comercio": item["comercio"],
            "Monto (S/.)": item["monto"],
            "Categoría": cat["nombre"]
        })

df = pd.DataFrame(datos)

# Título
st.title("📊 Dashboard Financiero")
st.markdown(f"🗓️ **Periodo:** {json_data['resumen_gastos_semanales']['periodo']}")
st.markdown(f"💰 **Gasto total:** S/ {json_data['resumen_gastos_semanales']['gasto_total_semana']:.2f}")
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

# ✅ Descargar Excel
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

# ✅ Descargar PDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Resumen de Gastos Semanales", 0, 1, "C")

    def categoria_table(self, resumen):
        self.set_font("Arial", "", 12)
        for idx, row in resumen.iterrows():
            self.cell(100, 10, row["Categoría"], 1)
            self.cell(40, 10, f"S/ {row['Total (S/.)']:.2f}", 1, ln=True)

resumen_df = gasto_por_categoria.reset_index().rename(columns={"Monto (S/.)": "Total (S/.)"})
pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", "", 12)
pdf.cell(0, 10, f"Periodo: {json_data['resumen_gastos_semanales']['periodo']}", ln=True)
pdf.cell(0, 10, f"Gasto Total: S/ {json_data['resumen_gastos_semanales']['gasto_total_semana']:.2f}", ln=True)
pdf.ln(10)
pdf.categoria_table(resumen_df)

# 🛠️ Corregido: obtener PDF como bytes
pdf_bytes = pdf.output(dest='S').encode('latin1')

st.download_button(
    label="📄 Descargar PDF",
    data=pdf_bytes,
    file_name="resumen_gastos.pdf",
    mime="application/pdf"
)