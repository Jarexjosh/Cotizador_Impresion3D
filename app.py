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
                with st.expander(f"Color {i+1}", expanded=True):
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        m = st.selectbox(f"Marca C{i+1}", df_cat['Marca'].unique(), key=f"m{i}")
                        c = st.selectbox(f"Color C{i+1}", df_cat[df_cat['Marca'] == m]['Color'], key=f"c{i}")
                        fila = df_cat[(df_cat['Marca'] == m) & (df_cat['Color'] == c)].iloc[0]
                        costo_g = fila['Costo'] / fila['Peso']
                        st.caption(f"Costo por gramo: ${costo_g:.4f}")
                    with m_col2:
                        g = st.number_input(f"Gramos C{i+1}", min_value=0.1, key=f"g{i}")
                    detalles_material.append({"costo_g": costo_g, "gramos": g})

    with col2:
        st.subheader("2. Mano de Obra y Ganancia")
        mo_h = st.number_input("Horas manuales (Lijado/Setup)", min_value=0)
        mo_m = st.number_input("Minutos manuales", min_value=0, max_value=59)
        tiempo_mo_activa = mo_h + (mo_m / 60)

        utilidad_slider = st.slider("Margen de Utilidad (%)", 5, 100, 40)
        utilidad_factor = utilidad_slider / 100

    # --- CÁLCULOS ---
    costo_filamento_total = sum(item['costo_g'] * item['gramos'] for item in detalles_material)
    tasa_fija_hr = COSTO_ENERGIA_HR + AMORTIZACION_HR + RENTA_HR + INTERNET_HR + MO_INACTIVA_HR
    costo_fijo_total = tasa_fija_hr * total_horas_impresion
    costo_mo_activa = tiempo_mo_activa * MO_ACTIVA_HR
    
    costo_total_prod = costo_filamento_total + costo_fijo_total + costo_mo_activa
    precio_final = costo_total_prod * (1 + utilidad_factor)

    # --- RESULTADOS ---
    st.markdown("---")
    st.header(f"💰 Precio Final: ${precio_final:.2f} MXN")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Costo Producción", f"${costo_total_prod:.2f}")
    c2.metric("Ganancia", f"${(precio_final - costo_total_prod):.2f}")
    c3.metric("Tiempo Máquina", f"{total_horas_impresion:.2f} hrs")

    with st.expander("Ver desglose detallado"):
        st.write(f"• **Materiales:** ${costo_filamento_total:.2f}")
        st.write(f"• **Costos Fijos ({total_horas_impresion:.2f}h máquina):** ${costo_fijo_total:.2f}")
        st.write(f"• **Mano de Obra Activa:** ${costo_mo_activa:.2f}")
