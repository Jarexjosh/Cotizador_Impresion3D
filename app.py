import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cotizador 3D - Bambu Lab A1", layout="wide")

# --- CONSTANTES FIJAS (MXN) ---
COSTO_ENERGIA_HR = 1.05
AMORTIZACION_HR = 5.60
RENTA_HR = 5.00
INTERNET_HR = 1.40
MO_INACTIVA_HR = 3.93
MO_ACTIVA_HR = 39.30

st.title("🚀 Cotizador Profesional de Impresión 3D")
st.sidebar.header("Configuración de Catálogo")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    # Asegúrate de subir 'catalogo.xlsx' a tu repo de GitHub
    try:
        xls = pd.ExcelFile("catalogo.xlsx")
        return xls
    except:
        st.error("No se encontró el archivo catalogo.xlsx")
        return None

archivo_excel = cargar_datos()

if archivo_excel:
    # --- INPUTS DE USUARIO ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Configuración de Material")
        tipo_material = st.selectbox("Tipo de Material", archivo_excel.sheet_names)
        df_cat = pd.read_excel(archivo_excel, sheet_name=tipo_material)
        
        modo_impresion = st.radio("Modo de Impresión", ["Un solo color", "Multicolor"])
        
        detalles_material = []
        if modo_impresion == "Un solo color":
            st.markdown("---")
            marca = st.selectbox("Marca", df_cat['Marca'].unique())
            color = st.selectbox("Color", df_cat[df_cat['Marca'] == marca]['Color'])
            gramos = st.number_input("Gramos totales", min_value=1.0, step=1.0)
            horas = st.number_input("Horas de impresión", min_value=0.1, step=0.1)
            
            # Obtener costo del Excel
            fila = df_cat[(df_cat['Marca'] == marca) & (df_cat['Color'] == color)].iloc[0]
            costo_g = fila['Costo'] / fila['Peso']
            detalles_material.append({"costo_g": costo_g, "gramos": gramos, "horas": horas})
            
        else:
            num_colores = st.number_input("¿Cuántos colores?", min_value=2, max_value=4, step=1)
            total_horas = 0
            for i in range(int(num_colores)):
                st.markdown(f"**Color {i+1}**")
                m = st.selectbox(f"Marca C{i+1}", df_cat['Marca'].unique(), key=f"m{i}")
                c = st.selectbox(f"Color C{i+1}", df_cat[df_cat['Marca'] == m]['Color'], key=f"c{i}")
                g = st.number_input(f"Gramos C{i+1}", min_value=0.1, key=f"g{i}")
                h = st.number_input(f"Horas asignadas a este color C{i+1}", min_value=0.0, key=f"h{i}")
                
                fila = df_cat[(df_cat['Marca'] == m) & (df_cat['Color'] == c)].iloc[0]
                costo_g = fila['Costo'] / fila['Peso']
                detalles_material.append({"costo_g": costo_g, "gramos": g, "horas": h})
                total_horas += h
            horas = total_horas

    with col2:
        st.subheader("2. Mano de Obra y Utilidad")
        tiempo_mo_activa = st.number_input("Horas de mano de obra activa (Lijado, pintura, setup)", min_value=0.0, step=0.1)
        utilidad_slider = st.slider("Porcentaje de Utilidad esperado", 5, 100, 30) / 100

    # --- CÁLCULOS ---
    # 1. Costo Material
    costo_material_total = sum(item['costo_g'] * item['gramos'] for item in detalles_material)
    
    # 2. Costos Fijos por tiempo de máquina (Horas Totales)
    horas_totales = sum(item['horas'] for item in detalles_material)
    costo_fijo_total = (COSTO_ENERGIA_HR + AMORTIZACION_HR + RENTA_HR + INTERNET_HR + MO_INACTIVA_HR) * horas_totales
    
    # 3. Mano de Obra Activa
    costo_mo_activa = tiempo_mo_activa * MO_ACTIVA_HR
    
    # COSTO TOTAL (Antes de utilidad)
    costo_produccion = costo_material_total + costo_fijo_total + costo_mo_activa
    
    # PRECIO FINAL CON UTILIDAD
    precio_final = costo_produccion * (1 + utilidad_slider)

    # --- RESULTADOS ---
    st.markdown("---")
    st.subheader("📊 Resumen de Cotización")
    res1, res2, res3 = st.columns(3)
    
    res1.metric("Costo Producción", f"${costo_produccion:.2f} MXN")
    res2.metric("Utilidad", f"${(precio_final - costo_produccion):.2f} MXN")
    res3.subheader(f"Precio Sugerido: ${precio_final:.2f} MXN")

    with st.expander("Ver desglose detallado"):
        st.write(f"**Material:** ${costo_material_total:.2f}")
        st.write(f"**Costos Fijos (Máquina/Renta):** ${costo_fijo_total:.2f}")
        st.write(f"**Mano de Obra Activa:** ${costo_mo_activa:.2f}")
