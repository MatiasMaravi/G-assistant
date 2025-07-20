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

# Configurar locale para español de forma compatible con macOS
try:
    # Intentar locales comunes para español en macOS
    for loc in ['es_ES.UTF-8', 'es_ES', 'Spanish_Spain', 'es']:
        try:
            locale.setlocale(locale.LC_TIME, loc)
            print(f"✅ Locale configurado: {loc}")
            break
        except locale.Error:
            continue
    else:
        # Si ninguno funciona, usar el locale por defecto
        print("⚠️ No se pudo configurar locale en español, usando por defecto")
except Exception as e:
    print(f"⚠️ Error configurando locale: {e}")
    # Continuar sin locale específico

# Cargar datos del JSON
try:
    with open("consumos_bcp_clasificados_20250719_1957.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    print("✅ Datos cargados correctamente")
except FileNotFoundError:
    st.error("❌ No se encontró el archivo de datos. Verifica que existe: consumos_bcp_clasificados_20250719_1957.json")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"❌ Error al leer el archivo JSON: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Error inesperado: {e}")
    st.stop()


# === Procesar datos ===
datos = []
for item in json_data["todos_los_consumos"]:
    try:
        fecha = parser.parse(item["fecha"])
        datos.append({
            "Fecha": fecha,
            "Comercio": item["empresa"],
            "Monto (S/.)": item["monto_numerico"],
            "Categoría": item["categoria"],
            "Tipo de Tarjeta": item["tipo_tarjeta"],
            "Justificación": item["justificacion"],
            "Leído": item["leido"]
        })
    except Exception as e:
        print(f"⚠️ Error procesando consumo: {e}")
        continue

df = pd.DataFrame(datos)

# Verificar que tenemos datos
if df.empty:
    st.error("❌ No se encontraron datos para procesar")
    st.stop()

# Procesamiento de fechas más robusto
try:
    # Si las fechas ya están parseadas por dateutil.parser, solo eliminar zona horaria
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.tz_localize(None)
except Exception as e:
    print(f"⚠️ Error procesando fechas: {e}")
    # Fallback: intentar parseado directo
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')

# Procesar fecha del periodo
try:
    periodo_raw = json_data['metadata']['periodo_datos']
    periodo_dt = datetime.fromisoformat(periodo_raw.replace("Z", ""))
    periodo_legible = periodo_dt.strftime("%d/%m/%Y %H:%M")
except Exception as e:
    print(f"⚠️ Error procesando fecha del periodo: {e}")
    periodo_legible = "Fecha no disponible"

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
            # Manejar caracteres especiales en categorías
            categoria = str(row["Categoría"]).encode('latin1', 'replace').decode('latin1')
            self.cell(100, 10, categoria, 1)
            self.cell(40, 10, f"S/ {row['Total (S/.)']:.2f}", 1, ln=True)

resumen_df = gasto_por_categoria.reset_index().rename(columns={"Monto (S/.)": "Total (S/.)"})
pdf = PDF()
pdf.add_page()

try:
    # Obtener la fecha ISO del JSON
    fecha_iso = json_data['metadata']['periodo_datos']
    fecha_dt = datetime.strptime(fecha_iso.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
    fecha_formateada = fecha_dt.strftime("%d/%m/%Y")  # Formato más simple para evitar problemas con locale
except Exception as e:
    print(f"⚠️ Error formateando fecha para PDF: {e}")
    fecha_formateada = "Fecha no disponible"

pdf.set_font("Arial", "", 12)
pdf.cell(0, 10, f"Periodo: {fecha_formateada}", ln=True)
pdf.cell(0, 10, f"Gasto Total: S/ {json_data['metadata']['total_gastado']:.2f}", ln=True)
pdf.ln(10)
pdf.categoria_table(resumen_df)

try:
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    
    st.download_button(
        label="📄 Descargar PDF",
        data=pdf_bytes,
        file_name="resumen_gastos.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"❌ Error generando PDF: {e}")
    st.info("💡 El PDF no está disponible, pero puedes descargar el Excel.")