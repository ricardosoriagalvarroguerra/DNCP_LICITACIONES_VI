import streamlit as st
import pandas as pd
import datetime

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

# Título de la app
st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="color: #003366;">Buscador y Gestión de Licitaciones</h1>
        <p style="color: #666;">Explora información detallada de licitaciones, adjudicaciones, lotes y oferentes.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Menú de navegación
opcion = st.sidebar.radio(
    "Selecciona una página:",
    ["Buscador por ID", "Filtro Avanzado", "Detalles Expansibles", "Tablas Expandibles"]
)

# --- Página: Buscador por ID ---
if opcion == "Buscador por ID":
    st.title("Buscador por ID de Licitación")
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
                if st.button("Abrir Acta de Apertura"):
                    st.markdown(f"[Ver Acta]({acta_url})", unsafe_allow_html=True)
            else:
                st.warning("No se encontró el Acta de Apertura.")
        else:
            st.warning("No se encontró información para el ID proporcionado.")

# --- Página: Filtro Avanzado ---
elif opcion == "Filtro Avanzado":
    st.title("Filtro Avanzado de Licitaciones")
    
    # Asegurar formato correcto de fechas
    licitaciones['fecha_publicacion'] = pd.to_datetime(licitaciones['fecha_publicacion'])
    
    tipo = st.selectbox("Selecciona el Tipo de Licitación:", licitaciones['tipo'].unique())
    min_fecha = st.date_input("Fecha de publicación mínima:", licitaciones['fecha_publicacion'].min().date())
    max_fecha = st.date_input("Fecha de publicación máxima:", licitaciones['fecha_publicacion'].max().date())
    
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
    
    # Mostrar tabla completa
    st.markdown("### Tabla de Licitaciones")
    licitaciones_table = licitaciones
    st.dataframe(licitaciones_table)

    # Selección de fila
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

    # Filtros por monto, año y tipo
    min_monto = st.number_input("Monto mínimo (GS):", min_value=0, value=0)
    max_monto = st.number_input("Monto máximo (GS):", min_value=0, value=int(licitaciones['estimado_GS'].max()))
    anio = st.selectbox("Año de la Licitación:", licitaciones['fecha_publicacion'].dt.year.unique())
    tipo = st.selectbox("Tipo de Licitación:", licitaciones['tipo'].unique())
    
    licitaciones_filtradas = licitaciones[
        (licitaciones['estimado_GS'] >= min_monto) &
        (licitaciones['estimado_GS'] <= max_monto) &
        (licitaciones['fecha_publicacion'].dt.year == anio) &
        (licitaciones['tipo'] == tipo)
    ]

    # Paginación
    page_size = 10
    total_rows = len(licitaciones_filtradas)
    total_pages = -(-total_rows // page_size)
    page = st.number_input("Página:", min_value=1, max_value=total_pages, value=1)

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    st.markdown(f"### Mostrando página {page} de {total_pages}")
    st.dataframe(licitaciones_filtradas.iloc[start_idx:end_idx])
