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

# Menú de navegación
opcion = st.sidebar.radio(
    "Selecciona una página:",
    ["Inicio", "Filtro Avanzado", "Detalles Expansibles", "Tablas Expandibles"]
)

# Página: Inicio
if opcion == "Inicio":
    st.title("Bienvenido a la Aplicación de Licitaciones")
    st.write("Selecciona una opción desde el menú de navegación para explorar la información.")
    st.write("Desarrollado para visualizar datos clave de forma ordenada y eficiente.")

# Página: Filtro Avanzado
elif opcion == "Filtro Avanzado":
    st.title("Filtro Avanzado de Licitaciones")
    
    # Filtro por tipo de licitación
    tipo = st.selectbox("Selecciona el Tipo de Licitación:", licitaciones['tipo'].unique())
    
    # Filtro por rango de fechas
    min_fecha = st.date_input("Fecha de publicación mínima:", licitaciones['fecha_publicacion'].min())
    max_fecha = st.date_input("Fecha de publicación máxima:", licitaciones['fecha_publicacion'].max())
    
    # Aplicar filtros
    licitaciones_filtradas = licitaciones[
        (licitaciones['tipo'] == tipo) & 
        (licitaciones['fecha_publicacion'] >= min_fecha) &
        (licitaciones['fecha_publicacion'] <= max_fecha)
    ]
    
    # Mostrar resultados
    st.markdown(f"### Resultados Filtrados ({len(licitaciones_filtradas)})")
    st.dataframe(licitaciones_filtradas)

# Página: Detalles Expansibles
elif opcion == "Detalles Expansibles":
    st.title("Detalles Expansibles de Licitaciones")
    
    # Mostrar tabla principal
    st.markdown("### Tabla de Licitaciones")
    licitaciones_table = licitaciones[['id', 'nombre_proyecto', 'oferentes_cantidad', 'cant_lotes']]
    st.dataframe(licitaciones_table)

    # Selección de fila
    fila_seleccionada = st.selectbox("Selecciona un ID de Licitación para Detalles:", licitaciones_table['id'])
    
    if fila_seleccionada:
        st.markdown(f"### Detalles para la Licitación ID: {fila_seleccionada}")
        
        # Mostrar oferentes
        oferentes_relacionados = oferentes[oferentes['id'] == fila_seleccionada]
        st.markdown("**Oferentes:**")
        st.dataframe(oferentes_relacionados[['name', 'address_countryName']])
        
        # Mostrar lotes
        lotes_relacionados = lotes[lotes['id'] == fila_seleccionada]
        st.markdown("**Lotes:**")
        st.dataframe(lotes_relacionados[['title', 'value_amount_GS']])

# Página: Tablas Expandibles
elif opcion == "Tablas Expandibles":
    st.title("Tablas Expandibles de Licitaciones")
    
    # Mostrar tabla de licitaciones
    st.markdown("### Licitaciones")
    for _, row in licitaciones.iterrows():
        with st.expander(f"Proyecto: {row['nombre_proyecto']} (ID: {row['id']})"):
            st.markdown(f"**Criterio:** {row['criterio']}")
            st.markdown(f"**Tipo:** {row['tipo']}")
            st.markdown(f"**Estimado (GS):** {row['estimado_GS']}")
            st.markdown(f"**Adjudicado (GS):** {row['adjudicado_GS']}")
            
            # Detalles de adjudicados
            adjudicados_relacionados = adjudicado[adjudicado['id'] == row['id']]
            st.markdown("**Adjudicados:**")
            st.dataframe(adjudicados_relacionados[['name_oferente', 'value_amount_GS']])
            
            # Detalles de oferentes
            oferentes_relacionados = oferentes[oferentes['id'] == row['id']]
            st.markdown("**Oferentes:**")
            st.dataframe(oferentes_relacionados[['name', 'address_countryName']])
