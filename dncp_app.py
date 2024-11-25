import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Aplicación de Licitaciones", layout="centered")

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

# Menú de navegación
with st.sidebar:
    opcion = st.radio(
        "Selecciona una página:",
        ["Buscador por ID", "Filtro Avanzado", "Detalles Expansibles", "Tablas Expandibles"]
    )

# --- Página: Buscador por ID ---
if opcion == "Buscador por ID":
    st.title("Buscador por ID de Licitación")
    
    with st.sidebar:
        id_search = st.text_input("🔍 Ingrese el ID de la Licitación:")

    if id_search:
        licitacion_data = licitaciones[licitaciones['id'] == id_search]
        if not licitacion_data.empty:
            st.markdown("### Información de la Licitación")
            st.write(f"**Proyecto:** {licitacion_data.iloc[0]['nombre_proyecto']}")
            st.write(f"**Criterio:** {licitacion_data.iloc[0]['criterio']}")
            st.write(f"**Tipo:** {licitacion_data.iloc[0]['tipo']}")
            st.write(f"**Monto Estimado (GS):** {licitacion_data.iloc[0]['estimado_GS']:,}")
            st.write(f"**Monto Adjudicado (GS):** {licitacion_data.iloc[0]['adjudicado_GS']:,}")
            st.write(f"**Cantidad de Oferentes:** {licitacion_data.iloc[0]['oferentes_cantidad']}")
            st.write(f"**Cantidad de Lotes:** {licitacion_data.iloc[0]['cant_lotes']}")

            acta_data = actas[actas['id'] == id_search]
            if not acta_data.empty:
                acta_url = acta_data.iloc[0]['url']
                date_published = acta_data.iloc[0]['datePublished']
                st.markdown(f"**Fecha de Publicación del Acta:** {date_published}")
                st.markdown(f"[Ver Acta]({acta_url})", unsafe_allow_html=True)
            else:
                st.warning("No se encontró el Acta de Apertura.")
        else:
            st.warning("No se encontró información para el ID proporcionado.")

# --- Página: Filtro Avanzado ---
elif opcion == "Filtro Avanzado":
    st.title("Filtro Avanzado de Licitaciones")
    
    # Filtros en el menú lateral
    with st.sidebar:
        tipo = st.selectbox("Selecciona el Tipo de Licitación:", licitaciones['tipo'].unique())
        min_fecha = st.date_input("Fecha de publicación mínima:", licitaciones['fecha_publicacion'].min().date())
        max_fecha = st.date_input("Fecha de publicación máxima:", licitaciones['fecha_publicacion'].max().date())
    
    licitaciones['fecha_publicacion'] = pd.to_datetime(licitaciones['fecha_publicacion'])
    licitaciones_filtradas = licitaciones[
        (licitaciones['tipo'] == tipo) & 
        (licitaciones['fecha_publicacion'].dt.date >= min_fecha) & 
        (licitaciones['fecha_publicacion'].dt.date <= max_fecha)
    ]
    
    st.markdown(f"### Resultados Filtrados ({len(licitaciones_filtradas)})")
    st.dataframe(licitaciones_filtradas)

# --- Página: Detalles Expansibles ---
elif opcion == "Detalles Expansibles":
    st.title("Detalles Expansibles de Licitaciones")
    st.markdown("### Tabla de Licitaciones")
    licitaciones_table = licitaciones
    st.dataframe(licitaciones_table)

    with st.sidebar:
        fila_seleccionada = st.selectbox("Selecciona un ID de Licitación para Detalles:", licitaciones_table['id'])
    
    if fila_seleccionada:
        st.markdown(f"### Detalles para la Licitación ID: {fila_seleccionada}")
        oferentes_relacionados = oferentes[oferentes['id'] == fila_seleccionada]
        st.markdown("**Oferentes:**")
        st.dataframe(oferentes_relacionados[['name', 'address_countryName']])
        
        lotes_relacionados = lotes[lotes['id'] == fila_seleccionada]
        st.markdown("**Lotes:**")
        st.dataframe(lotes_relacionados[['title', 'value_amount_GS']])

# --- Página: Tablas Expandibles ---
elif opcion == "Tablas Expandibles":
    st.title("Tablas Expandibles de Licitaciones")

    # Filtros en el menú lateral
    with st.sidebar:
        anio = st.selectbox("Año de la Licitación:", licitaciones['fecha_publicacion'].dt.year.unique())
        tipos = ["None"] + list(licitaciones['tipo'].unique())
        tipo = st.selectbox("Tipo de Licitación:", tipos)

    licitaciones_filtradas = licitaciones[
        (licitaciones['fecha_publicacion'].dt.year == anio)
    ]
    if tipo != "None":
        licitaciones_filtradas = licitaciones_filtradas[licitaciones_filtradas['tipo'] == tipo]

    # Paginación
    page_size = 10
    total_rows = len(licitaciones_filtradas)
    total_pages = -(-total_rows // page_size)
    with st.sidebar:
        page = st.selectbox("Selecciona la Página:", range(1, total_pages + 1))

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    licitaciones_paginadas = licitaciones_filtradas.iloc[start_idx:end_idx]

    for _, row in licitaciones_paginadas.iterrows():
        with st.expander(f"Proyecto: {row['nombre_proyecto']} (ID: {row['id']})"):
            st.markdown(f"**Criterio:** {row['criterio']}")
            st.markdown(f"**Tipo:** {row['tipo']}")
            st.markdown(f"**Estimado (GS):** {row['estimado_GS']:,}")
            st.markdown(f"**Adjudicado (GS):** {row['adjudicado_GS']:,}")

            acta_data = actas[actas['id'] == row['id']]
            if not acta_data.empty:
                acta_url = acta_data.iloc[0]['url']
                date_published = acta_data.iloc[0]['datePublished']
                st.markdown(f"**Fecha de Publicación del Acta:** {date_published}")
                st.markdown(f"**Acta de Apertura:** [Ver Acta]({acta_url})", unsafe_allow_html=True)
            else:
                st.warning("No se encontró el Acta de Apertura.")

            adjudicados_relacionados = adjudicado[adjudicado['id'] == row['id']]
            if not adjudicados_relacionados.empty:
                st.markdown("**Adjudicados:**")
                st.dataframe(adjudicados_relacionados[['name_oferente', 'value_amount_GS']])

            oferentes_relacionados = oferentes[oferentes['id'] == row['id']]
            if not oferentes_relacionados.empty:
                st.markdown("**Oferentes:**")
                st.dataframe(oferentes_relacionados[['name', 'address_countryName']])
