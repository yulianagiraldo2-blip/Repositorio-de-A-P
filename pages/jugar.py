# Preparación del entorno
import random
import streamlit as st

from src.data import cargar_datos

st.title("Jugar")
df = cargar_datos()

N_PREGUNTAS = 10

# Inicialización de variables
if "historial_partidas" not in st.session_state:
    st.session_state["historial_partidas"] = []
    
def nueva_partida(modo: str):
    campo = "genero" if modo == "Adivina el género" else "decada"
    muestra = df.sample(N_PREGUNTAS)
    opciones_total = sorted(df[campo].unique())
    preguntas = []
    for _, fila in muestra.iterrows():
        correcta = fila[campo]
        otras = [o for o in opciones_total if o != correcta]
        opciones = random.sample(otras, 3) + [correcta]
        random.shuffle(opciones)
        preguntas.append(
            {"titulo": fila["titulo"], "artista": fila["artista"],
             "correcta": correcta, "opciones": opciones}
        )
    st.session_state.juego = {
        "modo": modo, "preguntas": preguntas, "i": 0,
        "puntos": 0, "respondida": False, "acierto": None,
    }


def responder():
    j = st.session_state.juego
    p = j["preguntas"][j["i"]]
    eleccion = st.session_state.get(f"resp_{j['i']}")
    j["acierto"] = eleccion == p["correcta"]
    j["puntos"] += int(j["acierto"])
    j["respondida"] = True


def siguiente():
    j = st.session_state.juego
    j["i"] += 1
    j["respondida"] = False
    j["acierto"] = None
    
# Si termina la última pregunta, se guarda en el historial de la sesión
    if j["i"] >= N_PREGUNTAS:
        st.session_state["historial_partidas"].append({
            "modo": j["modo"],
            "puntos": j["puntos"],
            "total": N_PREGUNTAS
        })

def terminar():
    st.session_state.pop("juego", None)


# Pantalla de inicio
if "juego" not in st.session_state:
    st.markdown("""
    ### Instrucciones del Juego
    * **Objetivo:** Demuestra tus conocimientos musicales adivinando el género o la década de las canciones del catálogo.
    * **Reglas:** Se te presentarán **10 canciones** una a una. Para cada canción tendrás 4 opciones de respuesta. Selecciona la correcta y presiona **Responder**.
    * **Puntuación:** Acumulas 1 punto por cada acierto. ¡Intenta conseguir el puntaje perfecto!
    """)
    
    st.divider()

    # Mostrar estadísticas acumuladas de la sesión si hay
    historial = st.session_state["historial_partidas"]
    if historial:
        st.subheader("Estadísticas de tus partidas en esta sesión")
        partidas_jugadas = len(historial)
        mejor_puntaje = max(p["puntos"] for p in historial)
        
        m1, m2 = st.columns(2)
        m1.metric("Partidas jugadas", partidas_jugadas)
        m2.metric("Mejor puntaje histórico", f"{mejor_puntaje} / {N_PREGUNTAS}")
        st.divider()
        
if "juego" not in st.session_state:
    st.write(f"Responde {N_PREGUNTAS} preguntas sobre canciones. ¡Mira cuánto sabes!")
    modo = st.radio("Modo de juego", ["Adivina el género", "Adivina la década"], horizontal=True)
    st.button("Empezar ", type="primary", on_click=nueva_partida, args=(modo,))
    st.stop()

j = st.session_state.juego

# Resultado final
if j["i"] >= N_PREGUNTAS:
    st.header(f"Puntaje final: {j['puntos']} / {N_PREGUNTAS}")
    if j["puntos"] >= 8:
        st.balloons()
        st.success("¡Eres un experto musical!")
    elif j["puntos"] >= 5:
        st.info("¡Buen trabajo! Sigue practicando.")
    else:
        st.warning("Hay que escuchar más música ")
    st.button("Jugar de nuevo", type="primary", on_click=terminar)
    st.stop()

# Pregunta actual
p = j["preguntas"][j["i"]]
st.progress(j["i"] / N_PREGUNTAS, text=f"Pregunta {j['i'] + 1} de {N_PREGUNTAS} · Puntos: {j['puntos']}")

pide = "el GÉNERO" if j["modo"] == "Adivina el género" else "la DÉCADA"
st.markdown(
    f'<div class="vm-pregunta">¿Cuál es {pide} de “{p["titulo"]}” de {p["artista"]}?</div>',
    unsafe_allow_html=True,
)

st.radio("Elige una opción", p["opciones"], key=f"resp_{j['i']}", disabled=j["respondida"])

if not j["respondida"]:
    st.button("Responder", type="primary", on_click=responder)
else:
    if j["acierto"]:
        st.markdown('<span class="vm-ok"> ¡Correcto!</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="vm-mal"> Era: {p["correcta"]}</span>', unsafe_allow_html=True)
    etiqueta = "Siguiente ➡️" if j["i"] < N_PREGUNTAS - 1 else "Ver resultado "
    st.button(etiqueta, type="primary", on_click=siguiente)
