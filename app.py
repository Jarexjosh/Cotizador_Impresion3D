import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cotizador 3D - Bambu Lab A1", layout="wide")

# --- CONSTANTES FIJAS (MXN por hora) ---
# Estos valores se multiplican directamente por el tiempo de impresión
COSTO_ENERGIA_HR = 1.05
AMORTIZACION_HR = 5.60
RENTA_HR = 5.00
INTERNET_HR = 1.40
MO_INACTIVA_HR = 3.93

# Tarifa para el tiempo de trabajo manual (Setup, lijado, etc.)
MO_ACTIVA_HR = 39.30

# --- LÓGICA DE CARGA DE DATOS ---
@st.cache_resource
def obtener_conexion_excel():
    """Mantiene la conexión al archivo Excel sin errores de serialización."""
    try:
        return pd.ExcelFile("catalogo.xlsx")
    except Exception as e:
        return None

@st.cache_data
def leer_hoja_material(nombre_hoja):
    """Carga los datos de una hoja específica (PLA, ABS, etc)."""
    xls = obtener_conexion_excel()
    if xls:
        return pd.read_excel(xls, sheet_name=nombre_hoja)
    return None

# --- INTERFAZ DE USUARIO ---
st.title("🤖 Cotizador Web: Impresión 3D")
st.markdown("Costo basado en **Bambu Lab A1** con Salario Mínimo CDMX 2026.")

archivo_excel = obtener_conexion_excel()

if archivo_excel is None:
    st.error("❌ No se encontró el archivo 'catalogo.xlsx'. Por favor súbelo a tu repositorio de GitHub.")
else:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("1. Configuración de Material e Impresión")
        
        # Selección de Material (Hojas del Excel)
        tipo_material = st.selectbox("Tipo de Material", archivo_excel.sheet_names)
        df_cat = leer_hoja_material(tipo_material)
        
        modo_impresion = st.radio("Modo de Impresión", ["Un solo color", "Varios colores (Multicolor)"])
        
        detalles_material = []
        total_horas_impresion = 0.0

        if modo_impresion == "Un solo color":
            st.info("Configura los datos para un solo filamento.")
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                marca = st.selectbox("Marca", df_cat['Marca'].unique())
                color = st.selectbox("Color", df_cat[df_cat['Marca'] == marca]['Color'])
            with c_col2:
                gramos = st.number_input("Gramos usados (con soportes)", min_value=0.1, step=1.0)
                horas = st.number_input("Tiempo de impresión (Horas)", min_value=0.1, step=0.1)
                minutos = st.number_input("Tiempo de impresión (Minutos)", min_value=0, max_value=59, step=1)
            
            # Cálculo de tiempo decimal y costo
            total_horas_impresion = horas + (minutos / 60)
            fila = df_cat[(df_cat['Marca'] == marca) & (df_cat['Color'] == color)].iloc[0]
            costo_g = fila['Costo'] / fila['Peso']
            detalles_material.append({"costo_g": costo_g, "gramos": gramos})

        else:
            num_colores = st.number_input("¿Cuántos colores tendrá la pieza?", min_value=2, max_value=4, step=1)
            st.warning("Para multicolor, ingresa el gramaje por color y el tiempo TOTAL de la máquina.")
            
            t_h = st.number_input("Tiempo TOTAL de impresión (Horas)", min_value=0.1, key="th_multi")
            t_m = st.number_input("Tiempo TOTAL de impresión (Minutos)", min_value=0, max_value=59, key="tm_multi")
            total_horas_impresion = t_h + (t_m / 60)

            for i in range(int(num_colores)):
                with st.expander(f"Configuración Color {i+1}", expanded=True):
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        m = st.selectbox(f"Marca C{i+1}", df_cat['Marca'].unique(), key=f"m{i}")
                        c = st.selectbox(f"Color C{i+1}", df_cat[df_cat['Marca'] == m]['Color'], key=f"c{i}")
                    with m_col2:
                        g = st.number_input(f"Gramos C{i+1}", min_value=0.1, key=f"g{i}")
                    
                    fila = df_cat[(df_cat['Marca'] == m) & (df_cat['Color'] == c)].iloc[0]
                    costo_g = fila['Costo'] / fila['Peso']
                    detalles_material.append({"costo_g": costo_g, "gramos": g})

    with col2:
        st.subheader("2. Mano de Obra y Ganancia")
        
        st.markdown("**Tiempo Activo (Lijado, pintura, etc.)**")
        mo_h = st.number_input("Horas manuales", min_value=0, step=1)
        mo_m = st.number_input("Minutos manuales", min_value=0, max_value=59, step=1)
        tiempo_mo_activa = mo_h + (mo_m / 60)

        st.markdown("---")
        utilidad_slider = st.slider("Margen de Utilidad (%)", 5, 100, 40)
        utilidad_factor = utilidad_slider / 100

    # --- CÁLCULOS FINALES ---
    
    # 1. Costo de Filamento
    costo_filamento_total = sum(item['costo_g'] * item['gramos'] for item in detalles_material)
    
    # 2. Costos Fijos (Basados en tiempo de máquina)
    # Suma de: Energía + Amortización + Renta + Internet + MO Inactiva
    tasa_fija_por_hora = COSTO_ENERGIA_HR + AMORTIZACION_HR + RENTA_HR + INTERNET_HR + MO_INACTIVA_HR
    costo_fijo_total = tasa_fija_por_hora * total_horas_impresion
    
    # 3. Costo de Mano de Obra Activa
    costo_mo_activa_total = tiempo_mo_activa * MO_ACTIVA_HR
    
    # COSTO TOTAL DE PRODUCCIÓN
    costo_total_produccion = costo_filamento_total + costo_fijo_total
