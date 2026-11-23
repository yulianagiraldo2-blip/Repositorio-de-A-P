import pandas as pd
import streamlit as st
import plotly.express as px

from src.data import cargar_datos

st.title("❤️ Mi Música")
df = cargar_datos()

# Verificar que existan las variables de sesión 
if "canciones_favoritas" not in st.session_state:
    st.session_state["canciones_favoritas"] = []

if "canciones_escuchadas" not in st.session_state:
    st.session_state["canciones_escuchadas"] = []

if "historial_partidas" not in st.session_state:
    st.session_state["historial_partidas"] = []

# Comprobar si hay actividad real
tiene_favoritas = len(st.session_state["canciones_favoritas"]) > 0
tiene_escuchadas = len(st.session_state["canciones_escuchadas"]) > 0
tiene_partidas = len(st.session_state["historial_partidas"]) > 0


# Estado sin actividad

if not (tiene_favoritas or tiene_escuchadas or tiene_partidas):
    st.info("""
     **¡Aún no hay actividad registrada en esta sesión!**
    
    Para ver información en este panel:
    * Ve a la sección **Explorar**, selecciona canciones y guárdalas en tus favoritas o márcalas como escuchadas.
    * Ve a la sección **Jugar**, completa algunas partidas de adivinanzas.
    """)
    st.stop()

# Resumen de actividad

st.subheader(" Resumen General")

total_partidas = len(st.session_state["historial_partidas"])
total_favs = len(st.session_state["canciones_favoritas"])
total_escuchadas = len(st.session_state["canciones_escuchadas"])

if total_partidas > 0:
    mejor_puntaje = max(p["puntos"] for p in st.session_state["historial_partidas"])
    puntaje_promedio = sum(p["puntos"] for p in st.session_state["historial_partidas"]) / total_partidas
else:
    mejor_puntaje = 0
    puntaje_promedio = 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric(" Partidas Jugadas", total_partidas)
col2.metric(" Mejor Puntaje", f"{mejor_puntaje} / 10" if total_partidas > 0 else "N/A")
col3.metric("Canciones Favoritas", total_favs)
col4.metric("Canciones Escuchadas", total_escuchadas)

st.divider()


# Estadística y historial

st.subheader("Historial y desempeño en juegos")

if total_partidas == 0:
    st.warning("Todavía no has jugado ninguna partida en la sección de Jugar.")
else:
    # Preparar DataFrame del historial de partidas
    df_historial = pd.DataFrame(st.session_state["historial_partidas"])
    df_historial.index = df_historial.index + 1  # Orden de juego (Partida 1, 2, 3...)
    df_historial = df_historial.reset_index().rename(columns={"index": "Orden", "modo": "Modo de Juego", "puntos": "Puntaje", "total": "Total Preguntas"})
    
    col_h1, col_h2 = st.columns([1, 1])
    
    with col_h1:
        st.write("**Resumen de partidas jugadas:**")
        st.dataframe(df_historial, use_container_width=True, hide_index=True)
        st.caption(f"Puntaje promedio de sesión: {puntaje_promedio:.1f} / 10")

    with col_h2:
        st.write("**Evolución del puntaje por partida:**")
        fig_evolucion = px.line(
            df_historial,
            x="Orden",
            y="Puntaje",
            markers=True,
            title="Progreso de puntajes en el tiempo",
            color_discrete_sequence=["#8B5CF6"]
        )
        fig_evolucion.update_layout(yaxis=dict(range=[0, 11]))
        st.plotly_chart(fig_evolucion, use_container_width=True)

st.divider()

# Lista de favoritas guardada en la sesión
if "favoritas" not in st.session_state:
    st.session_state.favoritas = []

tab1, tab2, tab3 = st.tabs(["Mis favoritas", "Agregar canción propia", "Sobre los datos"])

with tab1:
    opciones = (df["titulo"] + " — " + df["artista"]).tolist()
    elegidas = st.multiselect("Elige tus canciones favoritas del catálogo", opciones)
    if elegidas:
        favs = df[(df["titulo"] + " — " + df["artista"]).isin(elegidas)]
    else:
        favs = df.iloc[0:0]
    propias = pd.DataFrame(st.session_state.favoritas)
    todas = pd.concat([favs[["titulo", "artista", "genero", "anio"]], propias], ignore_index=True)

    if todas.empty:
        st.info("Aún no tienes favoritas. ¡Elige algunas arriba!")
    else:
        st.dataframe(todas, use_container_width=True, hide_index=True)
        st.subheader("Tus géneros favoritos")
        st.bar_chart(todas["genero"].value_counts())
        st.download_button(
            "Descargar mis favoritas (CSV)",
            todas.to_csv(index=False).encode("utf-8"),
            file_name="mis_favoritas.csv",
            mime="text/csv",
        )

with tab2:
    with st.form("nueva_cancion", clear_on_submit=True):
        titulo = st.text_input("Título")
        artista = st.text_input("Artista")
        genero = st.selectbox("Género", sorted(df["genero"].unique()))
        anio = st.number_input("Año", min_value=1900, max_value=2030, value=2020, step=1)
        enviado = st.form_submit_button("Agregar")
    if enviado:
        if titulo.strip() and artista.strip():
            st.session_state.favoritas.append(
                {"titulo": titulo.strip(), "artista": artista.strip(),
                 "genero": genero, "anio": int(anio)}
            )
            st.success("Canción agregada. Mira la pestaña “Mis favoritas”.")
        else:
            st.error("Escribe el título y el artista.")

with tab3:
    st.write(f"El catálogo tiene **{df.shape[0]} filas** y **{df.shape[1]} columnas**.")
    st.write("Valores nulos por columna:")
    st.dataframe(df.isna().sum().rename("nulos"))
    st.write("Vista previa:")
    st.dataframe(df.head(10), hide_index=True)
