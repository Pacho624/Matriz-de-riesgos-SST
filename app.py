import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

st.set_page_config(page_title="Matriz de Riesgos SST", layout="centered")

st.title("🧩 Análisis de Matriz de Riesgos - SST")
st.markdown("Ingresa los datos de la actividad para evaluar el nivel de riesgo.")

if "datos" not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=[
        "Actividad", "Peligro", "Consecuencias",
        "Probabilidad", "Severidad", "Controles"
    ])

with st.form("form_riesgo"):
    actividad = st.text_input("Actividad")
    peligro = st.text_input("Peligro")
    consecuencias = st.text_input("Consecuencias")
    probabilidad = st.slider("Probabilidad (1-5)", 1, 5)
    severidad = st.slider("Severidad (1-5)", 1, 5)
    controles = st.text_area("Controles existentes")

    submitted = st.form_submit_button("Agregar a la matriz")

    if submitted:
        nuevo_dato = {
            "Actividad": actividad,
            "Peligro": peligro,
            "Consecuencias": consecuencias,
            "Probabilidad": probabilidad,
            "Severidad": severidad,
            "Controles": controles
        }
        st.session_state.datos = pd.concat([
            st.session_state.datos,
            pd.DataFrame([nuevo_dato])
        ], ignore_index=True)
        st.success("✅ Registro agregado correctamente.")

st.subheader("📋 Datos registrados")
st.dataframe(st.session_state.datos)

def calcular_nivel_y_clasificacion(df):
    df = df.copy()
    df["Nivel de Riesgo"] = df["Probabilidad"] * df["Severidad"]
    def clasificar(riesgo):
        if riesgo >= 16:
            return "Alto"
        elif riesgo >= 6:
            return "Medio"
        else:
            return "Bajo"
    df["Clasificación"] = df["Nivel de Riesgo"].apply(clasificar)
    return df

if not st.session_state.datos.empty:
    matriz_con_riesgo = calcular_nivel_y_clasificacion(st.session_state.datos)
    st.subheader("⚠️ Matriz de Riesgos con Clasificación")
    st.dataframe(matriz_con_riesgo)

    st.subheader("📊 Distribución de Riesgos por Clasificación")
    conteo = matriz_con_riesgo["Clasificación"].value_counts()
    fig, ax = plt.subplots()
    ax.bar(conteo.index, conteo.values)
    ax.set_title("Cantidad de Riesgos por Clasificación")
    ax.set_xlabel("Clasificación del Riesgo")
    ax.set_ylabel("Cantidad de Casos")
    st.pyplot(fig)

st.subheader("✏️ Editar o Eliminar un Registro")
if not st.session_state.datos.empty:
    index_to_edit = st.number_input(
        "Selecciona el índice del registro", 
        min_value=0, 
        max_value=len(st.session_state.datos) - 1, 
        step=1
    )

    selected_row = st.session_state.datos.iloc[index_to_edit]

    with st.form("editar_formulario"):
        actividad_edit = st.text_input("Actividad", value=selected_row["Actividad"])
        peligro_edit = st.text_input("Peligro", value=selected_row["Peligro"])
        consecuencias_edit = st.text_input("Consecuencias", value=selected_row["Consecuencias"])
        probabilidad_edit = st.slider("Probabilidad (1-5)", 1, 5, int(selected_row["Probabilidad"]))
        severidad_edit = st.slider("Severidad (1-5)", 1, 5, int(selected_row["Severidad"]))
        controles_edit = st.text_area("Controles existentes", value=selected_row["Controles"])

        col1, col2 = st.columns(2)
        with col1:
            actualizar = st.form_submit_button("✅ Actualizar")
        with col2:
            eliminar = st.form_submit_button("🗑 Eliminar")

        if actualizar:
            st.session_state.datos.iloc[index_to_edit] = [
                actividad_edit, peligro_edit, consecuencias_edit,
                probabilidad_edit, severidad_edit, controles_edit
            ]
            st.success("Registro actualizado correctamente.")

        if eliminar:
            st.session_state.datos = st.session_state.datos.drop(index=index_to_edit).reset_index(drop=True)
            st.warning("Registro eliminado.")

def exportar_pdf(df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 40, "Reporte de Matriz de Riesgos - SST")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 55, f"Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y = height - 80
    c.setFont("Helvetica-Bold", 9)
    columnas = list(df.columns)
    c.drawString(40, y, " | ".join(col[:15] for col in columnas))
    c.setFont("Helvetica", 9)
    y -= 15
    for _, row in df.iterrows():
        fila = " | ".join(str(val)[:15] for val in row)
        c.drawString(40, y, fila)
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40
    c.save()
    buffer.seek(0)
    return buffer

st.subheader("📤 Exportar reporte a PDF")
if not st.session_state.datos.empty:
    df_export = calcular_nivel_y_clasificacion(st.session_state.datos)
    if st.button("Generar PDF"):
        pdf = exportar_pdf(df_export)
        st.download_button(
            label="📥 Descargar PDF",
            data=pdf,
            file_name="reporte_matriz_riesgos.pdf",
            mime="application/pdf"
        )

def exportar_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Matriz de Riesgos")
    buffer.seek(0)
    return buffer

st.subheader("📥 Exportar reporte a Excel")
if not st.session_state.datos.empty:
    df_excel = calcular_nivel_y_clasificacion(st.session_state.datos)
    if st.button("Generar Excel"):
        excel_data = exportar_excel(df_excel)
        st.download_button(
            label="📄 Descargar Excel",
            data=excel_data,
            file_name="matriz_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
