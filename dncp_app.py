import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

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
        ["Buscador por ID", "Filtro Avanzado", "Tablas Expandibles"]
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
        tipos = ["None"] + list(licitaciones['tipo'].unique())
        tipo = st.selectbox("Selecciona el Tipo de Licitación:", tipos)
        min_fecha = st.date_input("Fecha de publicación mínima:", licitaciones['fecha_publicacion'].min().date())
        max_fecha = st.date_input("Fecha de publicación máxima:", licitaciones['fecha_publicacion'].max().date())
    
    # Asegurar formato correcto de fechas
    licitaciones['fecha_publicacion'] = pd.to_datetime(licitaciones['fecha_publicacion'])
    
    # Aplicar filtros
    licitaciones_filtradas = licitaciones[
        (licitaciones['fecha_publicacion'].dt.date >= min_fecha) & 
        (licitaciones['fecha_publicacion'].dt.date <= max_fecha)
    ]
    if tipo != "None":
        licitaciones_filtradas = licitaciones_filtradas[licitaciones_filtradas['tipo'] == tipo]
    
    # Formatear columnas con separadores de miles
    licitaciones_filtradas['estimado_GS'] = licitaciones_filtradas['estimado_GS'].apply(lambda x: f"{x:,.0f}")
    licitaciones_filtradas['adjudicado_GS'] = licitaciones_filtradas['adjudicado_GS'].apply(lambda x: f"{x:,.0f}")
    
    st.markdown(f"### Resultados Filtrados ({len(licitaciones_filtradas)})")

    # Configuración de AgGrid para filtros avanzados
    gb = GridOptionsBuilder.from_dataframe(licitaciones_filtradas)
    gb.configure_default_column(editable=False, filter=True, sortable=True, resizable=True)
    gb.configure_pagination(enabled=True, paginationAutoPageSize=True)
    grid_options = gb.build()

    # Mostrar la tabla interactiva
    AgGrid(licitaciones_filtradas, gridOptions=grid_options, height=400, fit_columns_on_grid_load=True)

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

    # Convertir `id_dncp` a cadena de texto
    licitaciones_paginadas['id_dncp'] = licitaciones_paginadas['id_dncp'].astype(str)

    for _, row in licitaciones_paginadas.iterrows():
        with st.expander(f"Proyecto: {row['nombre_proyecto']} (ID: {row['id']})"):
            st.markdown(f"**Criterio:** {row['criterio']}")
            st.markdown(f"**Tipo:** {row['tipo']}")
            st.markdown(f"**ID DNCP:** {row['id_dncp']}")
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
