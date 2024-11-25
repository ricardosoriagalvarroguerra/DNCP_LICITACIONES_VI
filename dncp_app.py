import streamlit as st
import pandas as pd

# Cargar las hojas de cálculo
file_path = 'BDD_DNCP_FINAL.xlsx'
licitaciones = pd.read_excel(file_path, sheet_name='licitaciones')
adjudicado = pd.read_excel(file_path, sheet_name='adjudicado')
lotes = pd.read_excel(file_path, sheet_name='lotes')
oferentes = pd.read_excel(file_path, sheet_name='oferentes')

# Título de la app
st.title("Buscador de Licitaciones")

# Barra de búsqueda
id_search = st.text_input("Ingrese el ID de la licitación:")

# Buscar información si se ingresa un ID
if id_search:
    st.subheader("Resultados para ID: " + id_search)

    # Datos de licitaciones
    licitacion_data = licitaciones[licitaciones['id'] == id_search]
    if not licitacion_data.empty:
        st.markdown("### Información de la Licitación")
        st.write(f"**Proyecto:** {licitacion_data.iloc[0]['nombre_proyecto']}")
        st.write(f"**Criterio:** {licitacion_data.iloc[0]['criterio']}")
        st.write(f"**Tipo:** {licitacion_data.iloc[0]['tipo']}")
        st.write(f"**Estimado:** {licitacion_data.iloc[0]['estimado_GS']}")
        st.write(f"**Adjudicado:** {licitacion_data.iloc[0]['adjudicado_GS']}")
        st.write(f"**Cantidad de Oferentes:** {licitacion_data.iloc[0]['oferentes_cantidad']}")
        st.write(f"**Cantidad de Lotes:** {licitacion_data.iloc[0]['cant_lotes']}")
    else:
        st.write("No se encontró información en la tabla de licitaciones.")

    # Datos de adjudicado
    adjudicado_data = adjudicado[adjudicado['id'] == id_search]
    if not adjudicado_data.empty:
        st.markdown("### Información de Adjudicación")
        st.write(f"**Fecha de Adjudicación:** {adjudicado_data.iloc[0]['fecha_adjudicacion']}")
        st.write(f"**Monto Adjudicado:** {adjudicado_data.iloc[0]['value_amount_GS']}")
        st.write(f"**Nombre del Oferente:** {adjudicado_data.iloc[0]['name_oferente']}")
    else:
        st.write("No se encontró información en la tabla de adjudicación.")

    # Datos de lotes
    lotes_data = lotes[lotes['id'] == id_search]
    if not lotes_data.empty:
        st.markdown("### Información de los Lotes")
        for _, row in lotes_data.iterrows():
            st.write(f"**Título del Lote:** {row['title']}")
            st.write(f"**Monto del Lote:** {row['value_amount_GS']}")
    else:
        st.write("No se encontró información en la tabla de lotes.")

    # Datos de oferentes
    oferentes_data = oferentes[oferentes['_link_main'].isin(lotes_data['_link_main'])]
    if not oferentes_data.empty:
        st.markdown("### Información de los Oferentes")
        for _, row in oferentes_data.iterrows():
            st.write(f"**Nombre:** {row['name']}")
            st.write(f"**País:** {row['address_countryName']}")
    else:
        st.write("No se encontró información en la tabla de oferentes.")