import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cotizador 3D Pro - Bambu Lab A1", layout="wide")

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
st.title("🚀 Cotizador 3D: Estilo Excel por Fases")
st.markdown("Cálculo exacto basado en el modelo de costos por material y tiempo.")

archivo_excel = obtener_conexion_excel()

if archivo_excel is None:
    st.error("❌ No se encontró 'catalogo.xlsx'. Súbelo a tu repositorio de GitHub.")
else:
    col_input, col_viz = st.columns([1.5, 1])

    with col_input:
        st.subheader("1. Configuración de Impresión")
        tipo_material = st.selectbox("Tipo de Material", archivo_excel.sheet_names)
        df_cat = leer_hoja_material(tipo_material)
        
        modo_impresion = st.radio("Modo de Impresión", ["Un solo color", "Multicolor (Por fases)"])
        
        detalles_fases = []

        if modo_impresion == "Un solo color":
            with st.container(border=True):
                m = st.selectbox("Marca", df_cat['Marca'].unique())
                c = st.selectbox("Color", df_cat[df_cat['Marca'] == m]['Color'])
                g = st.number_input("Gramos usados", min_value=0.1, step=1.0)
                
                c1, c2 = st.columns(2)
                h = c1.number_input("Horas", min_value=0, step=1)
                minu = c2.number_input("Minutos", min_value=0, max_value=59, step=1)
                
                fila = df_cat[(df_cat['Marca'] == m) & (df_cat['Color'] == c)].iloc[0]
                detalles_fases.append({
                    "nombre": f"{m} {c}",
                    "costo_g": fila['Costo'] / fila['Peso'],
                    "gramos": g,
                    "horas_fase": h + (minu / 60)
                })
        else:
            num_colores = st.number_input("¿Cuántos colores/fases?", min_value=2, max_value=4, step=1)
            for i in range(int(num_colores)):
                with st.expander(f"Fase Color {i+1}", expanded=True):
                    m = st.selectbox(f"Marca C{i+1}", df_cat['Marca'].unique(), key=f"m{i}")
                    c = st.selectbox(f"Color C{i+1}", df_cat[df_cat['Marca'] == m]['Color'], key=f"c{i}")
                    g = st.number_input(f"Gramos C{i+1}", min_value=0.1, key=f"g{i}")
                    
                    c1, c2 = st.columns(2)
                    h = c1.number_input(f"Horas C{i+1}", min_value=0, step=1, key=f"h{i}")
                    minu = c2.number_input(f"Minutos C{i+1}", min_value=0, max_value=59, step=1, key=f"min{i}")
                    
                    fila = df_cat[(df_cat['Marca'] == m) & (df_cat['Color'] == c)].iloc[0]
                    detalles_fases.append({
                        "nombre": f"{m} {c}",
                        "costo_g": fila['Costo'] / fila['Peso'],
                        "gramos": g,
                        "horas_fase": h + (minu / 60)
                    })

        st.subheader("2. Mano de Obra y Utilidad")
        c_mo1, c_mo2 = st.columns(2)
        mo_h = c_mo1.number_input("Horas Trabajo Manual", min_value=0)
        mo_m = c_mo2.number_input("Minutos Trabajo Manual", min_value=0, max_value=59)
        utilidad_slider = st.slider("Margen de Utilidad (%)", 5, 100, 30)

    # --- CÁLCULOS LÓGICOS ---
    tasa_fija_hr = COSTO_ENERGIA_HR + AMORTIZACION_HR + RENTA_HR + INTERNET_HR + MO_INACTIVA_HR
    
    total_material = 0
    total_fijos = 0
    total_tiempo_maq = 0
    
    for fase in detalles_fases:
        c_mat = fase['costo_g'] * fase['gramos']
        c_fij = tasa_fija_hr * fase['horas_fase']
        total_material += c_mat
        total_fijos += c_fij
        total_tiempo_maq += fase['horas_fase']
        
    total_mo_activa = (mo_h + (mo_m / 60)) * MO_ACTIVA_HR
    costo_produccion = total_material + total_fijos + total_mo_activa
    precio_final = costo_produccion * (1 + (utilidad_slider / 100))

    # --- VISUALIZACIÓN ---
    with col_viz:
        st.subheader("💰 Resumen Financiero")
        st.metric("PRECIO DE VENTA", f"${precio_final:.2f} MXN")
        st.metric("Costo Producción", f"${costo_produccion:.2f} MXN")
        st.metric("Ganancia Estimada", f"${(precio_final - costo_produccion):.2f} MXN")
        
        # Gráfica de Pastel
        datos_grafica = {
            "Concepto": ["Filamentos", "Costos Fijos (Máquina/Renta)", "Mano de Obra Manual"],
            "Monto": [total_material, total_fijos, total_mo_activa]
        }
        df_plot = pd.DataFrame(datos_grafica)
        fig = px.pie(df_plot, values='Monto', names='Concepto', 
                     title="Distribución de Costos de Producción",
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    # --- DESGLOSE FINAL ---
    with st.expander("📝 Detalle de Fases (Estilo Excel)"):
        for i, f in enumerate(detalles_fases):
            costo_fase = (f['costo_g'] * f['gramos']) + (tasa_fija_hr * f['horas_fase'])
            st.write(f"**Fase {i+1} ({f['nombre']}):** ${costo_fase:.2f} (Material: ${f['costo_g']*f['gramos']:.2f} | Fijos: ${tasa_fija_hr*f['horas_fase']:.2f})")
