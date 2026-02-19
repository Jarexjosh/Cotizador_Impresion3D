import streamlit as st
import pandas as pd
from cotizador import calcular_cotizacion, GANANCIAS

st.set_page_config(page_title="Cotizador CNC Pro", layout="wide")

st.title("💻 Cotizador de Corte CNC")
st.markdown("Cálculo para láminas de **122 x 244 cm**.")

@st.cache_data
def cargar_catalogo():
    archivo = "Catalogo_precios.xlsx"
    return pd.read_excel(archivo, sheet_name=None)

try:
    catalogo = cargar_catalogo()
    hojas_disponibles = list(catalogo.keys())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Material y Pieza")
        material_sel = st.selectbox("1. Material", hojas_disponibles)
        df_material = catalogo[material_sel]
        espesor_sel = st.selectbox("2. Grosor (mm)", df_material["Grosor"].tolist())
        
        precio_lamina = float(df_material.loc[df_material["Grosor"] == espesor_sel, "Precio"].values[0])
        st.info(f"Precio Lámina: **${precio_lamina:,.2f} MXN**")

        st.write("---")
        c1, c2 = st.columns(2)
        ancho_p = c1.number_input("Ancho pieza (cm)", min_value=0.1, value=10.0)
        largo_p = c2.number_input("Largo pieza (cm)", min_value=0.1, value=10.0)
        num_piezas = st.number_input("3. Cantidad de piezas", min_value=1, value=1)

    with col2:
        st.subheader("⚙️ Proceso")
        tipo_corte = st.selectbox("4. Tipo de Corte", ["Fresadora", "Laser"])
        costo_minuto = 17.0 if tipo_corte == "Fresadora" else 25.0
        st.warning(f"Tarifa: **${costo_minuto:,.2f} / min**")
        
        tiempo = st.number_input("5. Tiempo (minutos)", min_value=1, value=15)
        ganancia_sel = st.selectbox("6. Ganancia", list(GANANCIAS.keys()), index=4)

    st.divider()

    if st.button("CALCULAR COTIZACIÓN FINAL", use_container_width=True):
        # LLAMADA CORREGIDA: 7 argumentos en el orden exacto
        res = calcular_cotizacion(
            tiempo, num_piezas, precio_lamina, costo_minuto, ganancia_sel, ancho_p, largo_p
        )
        
        st.success(f"### Resumen (Uso: {res['Uso Material %']:.2f}% de la lámina)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Material", f"${res['Costo Material']:,.2f}")
        m2.metric("Máquina", f"${res['Costo Máquina']:,.2f}")
        m3.metric("TOTAL CLIENTE", f"${res['Total Final']:,.2f}")

except Exception as e:
    st.error(f"⚠️ Ocurrió un error: {e}")
