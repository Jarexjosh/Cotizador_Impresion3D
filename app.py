import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cotizador 3D - Bambu Lab A1", layout="wide")

# --- CONSTANTES FIJAS (MXN por hora) ---
COSTO_ENERGIA_HR = 1.05
AMORTIZACION_HR = 5.60
RENTA_HR = 5.00
INTERNET_HR = 1.40
MO_INACTIVA_HR = 3.93
MO_ACTIVA_HR = 39.30

# --- LÓGICA DE CARGA DE DATOS ---
@st.cache_resource
def obtener_conexion_excel():
    try:
        return pd.ExcelFile("catalogo.xlsx")
    except Exception as e:
        return None

@st.cache_data
def leer_hoja_material(nombre_hoja):
    xls = obtener_conexion_excel()
    if xls:
        return pd.read_excel(xls, sheet_name=nombre_hoja)
    return None

# --- INTERFAZ ---
st.title("🤖 Cotizador Web: Impresión 3D")

archivo_excel = obtener_conexion_excel()

if archivo_excel is None:
    st.error("❌ No se encontró el archivo 'catalogo.xlsx'.")
else:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("1. Configuración de Material e Impresión")
        tipo_material = st.selectbox("Tipo de Material", archivo_excel.sheet_names)
        df_cat = leer_hoja_material(tipo_material)
        
        modo_impresion = st.radio("Modo de Impresión", ["Un solo color", "Varios colores (Multicolor)"])
        
        detalles_material = []
        total_horas_impresion = 0.0

        if modo_impresion == "Un solo color":
            st.info("Configuración para filamento único.")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                marca = st.selectbox("Marca", df_cat['Marca'].unique())
                color = st.selectbox("Color", df_cat[df_cat['Marca'] == marca]['Color'])
                
                # Resumen del filamento seleccionado
                fila = df_cat[(df_cat['Marca'] == marca) & (df_cat['Color'] == color)].iloc[0]
                costo_g = fila['Costo'] / fila['Peso']
                st.info(f"💡 **Resumen:** Carrete de {fila['Peso']}g a ${fila['Costo']} MXN. Costo por gramo: **${costo_g:.4f}**")
                
            with c_col2:
                gramos = st.number_input("Gramos usados", min_value=0.1, step=1.0)
                h = st.number_input("Horas de impresión", min_value=0, step=1)
                m = st.number_input("Minutos de impresión", min_value=0, max_value=59, step=1)
                total_horas_impresion = h + (m / 60)
            
            detalles_material.append({"costo_g": costo_g, "gramos": gramos})

        else:
            num_colores = st.number_input("¿Cuántos colores?", min_value=2, max_value=4, step=1)
            t_h = st.number_input("Tiempo TOTAL de máquina (Horas)", min_value=0, key="th_multi")
            t_m = st.number_input("Tiempo TOTAL de máquina (Minutos)", min_value=0, max_value=59, key="tm_multi")
            total_horas_impresion = t_h + (t_m / 60)

            for i in range(int(num_colores)):
                with st.
