import streamlit as st
import pandas as pd
import webbrowser

# Configuración de la página
st.set_page_config(page_title="Buscador de Licitaciones", layout="centered")

# Función para cargar datos con caché
@st.cache_data
def load_data(sheet_name):
    return pd.read_excel('BDD_DNCP_FINAL.xlsx', sheet_name=sheet_name)

# Cargar las hojas de cálculo con caché
licitaciones = load_data('licitaciones')
adjudicado = load_data('adjudicado')
lotes = load_data('lotes')
oferentes = load_data('oferentes')
actas = load_data('actas')

# Título de la app
st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="color: #003366;">Buscador de Licitaciones</h1>
        <p style="color: #666;">Encuentra información detallada de las licitaciones, adjudicaciones, lotes y oferentes.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Barra de búsqueda
id_search = st.text_input("Ingrese el ID de la licitación:")

# Buscar información si se ingresa un ID
if id_search:
    st.markdown(f"<h3 style='color: #003366;'>Resultados para ID: {id_search}</h3>", unsafe_allow_html=True)
    st.divider()

    # Datos de licitaciones
    licitacion_data = licitaciones[licitaciones['id'] == id_search]
    if not licitacion_data.empty:
        st.markdown("### Información de la Licitación")
        st.divider()
        with st.container():
            st.markdown(f"**Proyecto:** {licitacion_data.iloc[0]['nombre_proyecto']}")
            st.markdown(f"**Criterio:** {licitacion_data.iloc[0]['criterio']}")
            st.markdown(f"**Tipo:** {licitacion_data.iloc[0]['tipo']}")
            st.markdown(f"**Monto Estimado (GS):** {licitacion_data.iloc[0]['estimado_GS']:,}")
            st.markdown(f"**Monto Adjudicado (GS):** {licitacion_data.iloc[0]['adjudicado_GS']:,}")
            st.markdown(f"**Cantidad de Oferentes:** {licitacion_data.iloc[0]['oferentes_cantidad']}")
            st.markdown(f"**Cantidad de Lotes:** {licitacion_data.iloc[0]['cant_lotes']}")
    else:
        st.warning("No se encontró información en la tabla de licitaciones.")

    st.divider()

    # Datos de adjudicado
    adjudicado_data = adjudicado[adjudicado['id'] == id_search]
    if not adjudicado_data.empty:
        st.markdown("### Información de Adjudicación")
        st.divider()
        with st.container():
            st.markdown(f"**Fecha de Adjudicación:** {adjudicado_data.iloc[0]['fecha_adjudicacion']}")
            st.markdown(f"**Monto Adjudicado (GS):** {adjudicado_data.iloc[0]['value_amount_GS']:,}")
            st.markdown(f"**Oferente Adjudicado:** {adjudicado_data.iloc[0]['name_oferente']}")
    else:
        st.warning("No se encontró información en la tabla de adjudicación.")

    st.divider()

    # Datos de lotes
    lotes_data = lotes[lotes['id'] == id_search]
    if not lotes_data.empty:
        st.markdown("### Información de los Lotes")
        st.divider()
        for _, row in lotes_data.iterrows():
            with st.container():
                st.markdown(f"**Título del Lote:** {row['title']}")
                st.markdown(f"**Monto del Lote (GS):** {row['value_amount_GS']:,}")
                st.divider()
    else:
        st.warning("No se encontró información en la tabla de lotes.")

    # Datos de oferentes
    oferentes_ids = lotes_data['id'].unique() if not lotes_data.empty else []
    oferentes_data = oferentes[oferentes['id'].isin(oferentes_ids)]
    if not oferentes_data.empty:
        st.markdown("### Información de los Oferentes")
        st.divider()
        for _, row in oferentes_data.iterrows():
            with st.container():
                st.markdown(f"**Nombre:** {row['name']}")
                st.markdown(f"**País:** {row['address_countryName']}")
                st.divider()
    else:
        st.warning("No se encontró información en la tabla de oferentes.")

    st.divider()

    # Cargar Acta de Apertura
    acta_data = actas[actas['id'] == id_search]
    if not acta_data.empty:
        acta_url = acta_data.iloc[0]['url']
        st.markdown("### Acta de Apertura")
        st.divider()
        if st.button("Abrir Acta de Apertura"):
            webbrowser.open_new_tab(acta_url)
    else:
        st.warning("No se encontró el Acta de Apertura para esta licitación.")
