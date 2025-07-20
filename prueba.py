import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from fpdf import FPDF
from datetime import datetime
from dateutil import parser
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
# === JSON embebido ===
json_data = {
  "metadata": {
    "fecha_proceso": "2025-07-19T19:18:15.510148",
    "total_consumos": 15,
    "total_gastado": 1123.12,
    "periodo_datos": "2025-07-19T23:07:38.773Z",
    "fuente": "BCP - Consumos últimos 7 días"
  },
  "resumen_categorias": {
    "ALIMENTACIÓN": {
      "cantidad": 6,
      "total": 218.27,
      "emoji": "🍕"
    },
    "BANCARIO": {
      "cantidad": 2,
      "total": 20.0,
      "emoji": "💳"
    },
    "COMPRAS": {
      "cantidad": 5,
      "total": 878.4,
      "emoji": "🛒"
    },
    "ENTRETENIMIENTO": {
      "cantidad": 1,
      "total": 2.0,
      "emoji": "🎮"
    },
    "SERVICIOS": {
      "cantidad": 1,
      "total": 4.45,
      "emoji": "🏠"
    }
  },
  "consumos_por_categoria": {
    "ALIMENTACIÓN": {
      "emoji": "🍕",
      "total_categoria": 218.27,
      "cantidad_consumos": 6,
      "consumos": [
        {
          "fecha": "Sat, 19 Jul 2025 18:51:50 +0000 (UTC)",
          "empresa": "TAMBO UTEC",
          "monto": "S/ 7.40",
          "monto_numerico": 7.4,
          "tipo_tarjeta": "Crédito",
          "justificacion": "TAMBO es una tienda de conveniencia.",
          "email_id": "198240740c9e3ac8",
          "leido": "TRUE"
        },
        {
          "fecha": "Wed, 16 Jul 2025 18:26:07 +0000 (UTC)",
          "empresa": "PROBOCA MOLINA",
          "monto": "S/ 13.50",
          "monto_numerico": 13.5,
          "tipo_tarjeta": "Crédito",
          "justificacion": "Proboca es una panadería/pastelería.",
          "email_id": "198147c9dbd48b3a",
          "leido": "FALSE"
        },
        {
          "fecha": "Tue, 15 Jul 2025 20:57:59 +0000 (UTC)",
          "empresa": "SHIMAYA RAMEN _ Barranco",
          "monto": "S/ 152.00",
          "monto_numerico": 152.0,
          "tipo_tarjeta": "Crédito",
          "justificacion": "Shimaya Ramen es un restaurante.",
          "email_id": "1980fe14cf14eab9",
          "leido": "FALSE"
        },
        {
          "fecha": "Mon, 14 Jul 2025 18:35:04 +0000 (UTC)",
          "empresa": "PROBOCA MOLINA",
          "monto": "S/ 13.50",
          "monto_numerico": 13.5,
          "tipo_tarjeta": "Crédito",
          "justificacion": "Proboca es una panadería/pastelería.",
          "email_id": "1980a381b28a8249",
          "leido": "FALSE"
        },
        {
          "fecha": "Sun, 13 Jul 2025 00:19:16 +0000 (UTC)",
          "empresa": "DLC*RAPPI PERU",
          "monto": "S/ 27.19",
          "monto_numerico": 27.19,
          "tipo_tarjeta": "Crédito",
          "justificacion": "RAPPI es un servicio de delivery de comida.",
          "email_id": "19801268060ec87a",
          "leido": "FALSE"
        },
        {
          "fecha": "Sun, 13 Jul 2025 00:14:50 +0000 (UTC)",
          "empresa": "PYU*RAPPI",
          "monto": "S/ 4.68",
          "monto_numerico": 4.68,
          "tipo_tarjeta": "Crédito",
          "justificacion": "RAPPI es un servicio de delivery de comida.",
          "email_id": "198012274cfc3313",
          "leido": "FALSE"
        }
      ]
    },
    "BANCARIO": {
      "emoji": "💳",
      "total_categoria": 20.0,
      "cantidad_consumos": 2,
      "consumos": [
        {
          "fecha": "Wed, 16 Jul 2025 23:36:56 +0000 (UTC)",
          "empresa": "PLIN-LEONARDO DANIEL IS",
          "monto": "S/ 10.00",
          "monto_numerico": 10.0,
          "tipo_tarjeta": "Débito",
          "justificacion": "PLIN es un servicio de transferencia bancaria.",
          "email_id": "19815992f7b35984",
          "leido": "FALSE"
        },
        {
          "fecha": "Sat, 12 Jul 2025 00:42:40 +0000 (UTC)",
          "empresa": "PLIN-LEONARDO DANIEL IS",
          "monto": "S/ 10.00",
          "monto_numerico": 10.0,
          "tipo_tarjeta": "Débito",
          "justificacion": "PLIN es un servicio de transferencia bancaria.",
          "email_id": "197fc15938a20878",
          "leido": "FALSE"
        }
      ]
    },
    "COMPRAS": {
      "emoji": "🛒",
      "total_categoria": 878.4,
      "cantidad_consumos": 5,
      "consumos": [
        {
          "fecha": "Fri, 18 Jul 2025 01:43:58 +0000 (UTC)",
          "empresa": "DP *Falabellacom",
          "monto": "S/ 449.00",
          "monto_numerico": 449.0,
          "tipo_tarjeta": "Crédito",
          "justificacion": "Falabella es una tienda por departamento.",
          "email_id": "1981b33dd1b294ef",
          "leido": "FALSE"
        },
        {
          "fecha": "Fri, 18 Jul 2025 00:06:54 +0000 (UTC)",
          "empresa": "T2115 MEGA PLAZA",
          "monto": "S/ 19.90",
          "monto_numerico": 19.9,
          "tipo_tarjeta": "Crédito",
          "justificacion": "MEGA PLAZA es un centro comercial.",
          "email_id": "1981adaf89bb54ec",
          "leido": "FALSE"
        },
        {
          "fecha": "Fri, 18 Jul 2025 00:05:53 +0000 (UTC)",
          "empresa": "T2115 MEGA PLAZA",
          "monto": "S/ 26.80",
          "monto_numerico": 26.8,
          "tipo_tarjeta": "Crédito",
          "justificacion": "MEGA PLAZA es un centro comercial.",
          "email_id": "1981ada0f8a8efbb",
          "leido": "FALSE"
        },
        {
          "fecha": "Fri, 18 Jul 2025 00:04:49 +0000 (UTC)",
          "empresa": "T2115 MEGA PLAZA",
          "monto": "S/ 29.80",
          "monto_numerico": 29.8,
          "tipo_tarjeta": "Crédito",
          "justificacion": "MEGA PLAZA es un centro comercial.",
          "email_id": "1981ad912d8d3785",
          "leido": "FALSE"
        },
        {
          "fecha": "Thu, 17 Jul 2025 23:29:32 +0000 (UTC)",
          "empresa": "DP *Falabellacom",
          "monto": "S/ 352.90",
          "monto_numerico": 352.9,
          "tipo_tarjeta": "Crédito",
          "justificacion": "Falabella es una tienda por departamento.",
          "email_id": "1981ab8c2098a95a",
          "leido": "FALSE"
        }
      ]
    },
    "ENTRETENIMIENTO": {
      "emoji": "🎮",
      "total_categoria": 2.0,
      "cantidad_consumos": 1,
      "consumos": [
        {
          "fecha": "Sat, 12 Jul 2025 04:15:55 +0000 (UTC)",
          "empresa": "PayUCINEMARK PERU",
          "monto": "S/ 2.00",
          "monto_numerico": 2.0,
          "tipo_tarjeta": "Débito",
          "justificacion": "CINEMARK es una cadena de cines.",
          "email_id": "197fcd8cfb15e42f",
          "leido": "FALSE"
        }
      ]
    },
    "SERVICIOS": {
      "emoji": "🏠",
      "total_categoria": 4.45,
      "cantidad_consumos": 1,
      "consumos": [
        {
          "fecha": "Sat, 19 Jul 2025 19:04:23 +0000 (UTC)",
          "empresa": "GOOGLE *ZGZ 832661",
          "monto": "S/ 4.45",
          "monto_numerico": 4.45,
          "tipo_tarjeta": "Débito",
          "justificacion": "GOOGLE es una suscripción digital.",
          "email_id": "1982412bc4ee7b77",
          "leido": "TRUE"
        }
      ]
    },
    "TRANSPORTE": {
      "emoji": "🚗",
      "total_categoria": 0.0,
      "cantidad_consumos": 0,
      "consumos": []
    }
  },
  "todos_los_consumos": [
    {
      "fecha": "Sat, 19 Jul 2025 19:04:23 +0000 (UTC)",
      "empresa": "GOOGLE *ZGZ 832661",
      "monto": "S/ 4.45",
      "monto_numerico": 4.45,
      "tipo_tarjeta": "Débito",
      "justificacion": "GOOGLE es una suscripción digital.",
      "email_id": "1982412bc4ee7b77",
      "leido": "TRUE",
      "categoria": "SERVICIOS"
    },
    {
      "fecha": "Sat, 19 Jul 2025 18:51:50 +0000 (UTC)",
      "empresa": "TAMBO UTEC",
      "monto": "S/ 7.40",
      "monto_numerico": 7.4,
      "tipo_tarjeta": "Crédito",
      "justificacion": "TAMBO es una tienda de conveniencia.",
      "email_id": "198240740c9e3ac8",
      "leido": "TRUE",
      "categoria": "ALIMENTACIÓN"
    },
    {
      "fecha": "Fri, 18 Jul 2025 01:43:58 +0000 (UTC)",
      "empresa": "DP *Falabellacom",
      "monto": "S/ 449.00",
      "monto_numerico": 449.0,
      "tipo_tarjeta": "Crédito",
      "justificacion": "Falabella es una tienda por departamento.",
      "email_id": "1981b33dd1b294ef",
      "leido": "FALSE",
      "categoria": "COMPRAS"
    },
    {
      "fecha": "Fri, 18 Jul 2025 00:06:54 +0000 (UTC)",
      "empresa": "T2115 MEGA PLAZA",
      "monto": "S/ 19.90",
      "monto_numerico": 19.9,
      "tipo_tarjeta": "Crédito",
      "justificacion": "MEGA PLAZA es un centro comercial.",
      "email_id": "1981adaf89bb54ec",
      "leido": "FALSE",
      "categoria": "COMPRAS"
    },
    {
      "fecha": "Fri, 18 Jul 2025 00:05:53 +0000 (UTC)",
      "empresa": "T2115 MEGA PLAZA",
      "monto": "S/ 26.80",
      "monto_numerico": 26.8,
      "tipo_tarjeta": "Crédito",
      "justificacion": "MEGA PLAZA es un centro comercial.",
      "email_id": "1981ada0f8a8efbb",
      "leido": "FALSE",
      "categoria": "COMPRAS"
    },
    {
      "fecha": "Fri, 18 Jul 2025 00:04:49 +0000 (UTC)",
      "empresa": "T2115 MEGA PLAZA",
      "monto": "S/ 29.80",
      "monto_numerico": 29.8,
      "tipo_tarjeta": "Crédito",
      "justificacion": "MEGA PLAZA es un centro comercial.",
      "email_id": "1981ad912d8d3785",
      "leido": "FALSE",
      "categoria": "COMPRAS"
    },
    {
      "fecha": "Thu, 17 Jul 2025 23:29:32 +0000 (UTC)",
      "empresa": "DP *Falabellacom",
      "monto": "S/ 352.90",
      "monto_numerico": 352.9,
      "tipo_tarjeta": "Crédito",
      "justificacion": "Falabella es una tienda por departamento.",
      "email_id": "1981ab8c2098a95a",
      "leido": "FALSE",
      "categoria": "COMPRAS"
    },
    {
      "fecha": "Wed, 16 Jul 2025 23:36:56 +0000 (UTC)",
      "empresa": "PLIN-LEONARDO DANIEL IS",
      "monto": "S/ 10.00",
      "monto_numerico": 10.0,
      "tipo_tarjeta": "Débito",
      "justificacion": "PLIN es un servicio de transferencia bancaria.",
      "email_id": "19815992f7b35984",
      "leido": "FALSE",
      "categoria": "BANCARIO"
    },
    {
      "fecha": "Wed, 16 Jul 2025 18:26:07 +0000 (UTC)",
      "empresa": "PROBOCA MOLINA",
      "monto": "S/ 13.50",
      "monto_numerico": 13.5,
      "tipo_tarjeta": "Crédito",
      "justificacion": "Proboca es una panadería/pastelería.",
      "email_id": "198147c9dbd48b3a",
      "leido": "FALSE",
      "categoria": "ALIMENTACIÓN"
    },
    {
      "fecha": "Tue, 15 Jul 2025 20:57:59 +0000 (UTC)",
      "empresa": "SHIMAYA RAMEN _ Barranco",
      "monto": "S/ 152.00",
      "monto_numerico": 152.0,
      "tipo_tarjeta": "Crédito",
      "justificacion": "Shimaya Ramen es un restaurante.",
      "email_id": "1980fe14cf14eab9",
      "leido": "FALSE",
      "categoria": "ALIMENTACIÓN"
    },
    {
      "fecha": "Mon, 14 Jul 2025 18:35:04 +0000 (UTC)",
      "empresa": "PROBOCA MOLINA",
      "monto": "S/ 13.50",
      "monto_numerico": 13.5,
      "tipo_tarjeta": "Crédito",
      "justificacion": "Proboca es una panadería/pastelería.",
      "email_id": "1980a381b28a8249",
      "leido": "FALSE",
      "categoria": "ALIMENTACIÓN"
    },
    {
      "fecha": "Sun, 13 Jul 2025 00:19:16 +0000 (UTC)",
      "empresa": "DLC*RAPPI PERU",
      "monto": "S/ 27.19",
      "monto_numerico": 27.19,
      "tipo_tarjeta": "Crédito",
      "justificacion": "RAPPI es un servicio de delivery de comida.",
      "email_id": "19801268060ec87a",
      "leido": "FALSE",
      "categoria": "ALIMENTACIÓN"
    },
    {
      "fecha": "Sun, 13 Jul 2025 00:14:50 +0000 (UTC)",
      "empresa": "PYU*RAPPI",
      "monto": "S/ 4.68",
      "monto_numerico": 4.68,
      "tipo_tarjeta": "Crédito",
      "justificacion": "RAPPI es un servicio de delivery de comida.",
      "email_id": "198012274cfc3313",
      "leido": "FALSE",
      "categoria": "ALIMENTACIÓN"
    },
    {
      "fecha": "Sat, 12 Jul 2025 04:15:55 +0000 (UTC)",
      "empresa": "PayUCINEMARK PERU",
      "monto": "S/ 2.00",
      "monto_numerico": 2.0,
      "tipo_tarjeta": "Débito",
      "justificacion": "CINEMARK es una cadena de cines.",
      "email_id": "197fcd8cfb15e42f",
      "leido": "FALSE",
      "categoria": "ENTRETENIMIENTO"
    },
    {
      "fecha": "Sat, 12 Jul 2025 00:42:40 +0000 (UTC)",
      "empresa": "PLIN-LEONARDO DANIEL IS",
      "monto": "S/ 10.00",
      "monto_numerico": 10.0,
      "tipo_tarjeta": "Débito",
      "justificacion": "PLIN es un servicio de transferencia bancaria.",
      "email_id": "197fc15938a20878",
      "leido": "FALSE",
      "categoria": "BANCARIO"
    }
  ]
}

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

# === Dashboard Streamlit ===
st.set_page_config(page_title="Dashboard Financiero", layout="centered")
st.title("📊 Dashboard Financiero")

st.markdown(f"🗓️ **Periodo de datos:** {json_data['metadata']['periodo_datos']}")
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
