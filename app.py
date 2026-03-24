import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Consulta de Estados - Scouts", page_icon="⚜️")

st.title("🔎 Consulta de Miembros")
st.markdown("Ingresá tu DNI para ver el estado de cuenta y recibos.")

# --- CONEXIÓN CON GOOGLE SHEETS ---
# Aquí es donde ocurre la magia. Usamos el secreto de conexión que configuraremos luego.
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FORMULARIO DE ENTRADA ---
with st.container():
    dni_input = st.text_input("DNI", max_chars=8, placeholder="Ej: 40123456")
    hoja_seleccionada = st.selectbox("¿Qué desea consultar?", ["Estados", "Recibos"])
    boton_buscar = st.button("Buscar Datos")

if boton_buscar:
    if not dni_input:
        st.error("⚠️ Por favor, ingresá un DNI válido.")
    else:
        try:
            # Leemos la hoja específica
            # 'ttl=0' asegura que siempre traiga datos frescos y no use caché vieja
            df = conn.read(worksheet=hoja_seleccionada, ttl=0)
            
            # Convertimos la columna DNI a string para comparar correctamente
            df['DNI'] = df['DNI'].astype(str)
            
            # Filtramos por el DNI ingresado
            resultado = df[df['DNI'] == dni_input]

            if resultado.empty:
                st.warning(f"No se encontraron datos para el DNI {dni_input} en la hoja {hoja_seleccionada}.")
            else:
                st.success(f"Datos encontrados para: {resultado.iloc[0].get('Nombre', 'Usuario')}")
                
                if hoja_seleccionada == "Estados":
                    # Vista Vertical: Transponemos los datos para que se vea como tu tabla original
                    # Mostramos solo la primera coincidencia
                    ficha = resultado.iloc[0].to_frame().reset_index()
                    ficha.columns = ["Concepto", "Detalle"]
                    st.table(ficha)
                
                else: # Caso Recibos
                    # Vista Horizontal: Mostramos todos los recibos encontrados para ese DNI
                    st.dataframe(
                        resultado,
                        column_config={
                            "Link": st.column_config.LinkColumn("Comprobante", help="Hacé clic para ver el recibo"),
                            "DNI": None # Ocultamos la columna DNI para que no sature la vista
                        },
                        hide_index=True,
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Error al conectar con la planilla: {e}")

# --- PIE DE PÁGINA ---
st.caption("Sistema de gestión interna - Grupo Scout Santa Fe")
