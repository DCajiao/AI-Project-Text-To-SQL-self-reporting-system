import streamlit as st
import core.llm_management as llm_management
import core.model_usage as model_usage
import services.sql_validator as sql_validator
import time

st.set_page_config(page_title="ERP Self-Reporting System", layout="centered")

# --- Sidebar ---
st.sidebar.header("👋 Bienvenido al sistema de generación de consultas SQL con IA.")
st.sidebar.markdown("Este sistema utiliza un modelo de IA para transformar preguntas en lenguaje natural en consultas SQL.")
st.sidebar.markdown("Puedes hacer preguntas sobre tus datos y obtener consultas SQL listas para usar.")
st.sidebar.header("📚 Recursos")
st.sidebar.markdown("> - 🦾 [Notebook: Entrenamiento y Evaluación del Modelo Fine Tuneado](https://drive.google.com/file/d/14IJFm_jgxA4lGs-Vj4hOTpFGOJZJy3RX/view?usp=sharing) \n"
                    "> - 📁 [Repositorio en Drive sobre el proyecto](https://drive.google.com/drive/folders/1qZgkBOGta7riLBaDLEdRl8hn94-nvPLH) \n"
                    ">- 💻 [Repositorio en GitHub](https://github.com/DCajiao/AI-Project-Text-To-SQL-self-reporting-system)")

# --- Estado inicial ---
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Pantalla inicial ---
if not st.session_state.model_loaded:
    st.title("🧠 Generador de consultas SQL con IA")

    st.header("📌 Antes de comenzar")
    st.markdown(
        "Para generar consultas SQL a partir de lenguaje natural, primero necesitamos cargar el modelo de IA.\n\n"
        "Selecciona la precisión con la que prefieres que trabaje el modelo:"
    )

    st.markdown("- **float16**: más rápida y eficiente, ideal para equipos con recursos limitados.\n"
                "- **float32**: más precisa, ideal si la exactitud es prioridad.")

    show_more = st.toggle("🔍 Ver más detalles técnicos", value=False, key="show_more")
    if show_more:
        st.info(
            "- `float16`: usa 2 bytes por número. Reduce el uso de memoria, con una ligera pérdida de precisión.\n"
            "- `float32`: usa 4 bytes por número. Mayor precisión, pero requiere más memoria."
        )

    st.markdown("---")
    dtype_option = st.radio("⚙️ Selecciona tipo de precisión:", ["float16", "float32"])

    if st.button("🚀 Cargar modelo"):
        with st.spinner("⏳ Cargando el modelo... Esto puede tardar unos segundos."):
            tokenizer = llm_management.load_tokenizer()
            model = llm_management.load_model(dtype_option)
            st.session_state["model"] = model
            st.session_state["tokenizer"] = tokenizer
            st.session_state.model_loaded = True
        st.success("✅ ¡Listo! El modelo está preparado.")
        st.rerun()  # 🔁 Forzar recarga para continuar al chat

# --- Modo Chat (una vez cargado el modelo) ---
else:
    st.header('💬 Interfaz de acceso al Modelo Text-to-SQL "ERP Self-Reporting System"')
    st.markdown("Haz una pregunta sobre tus datos, y la IA la transformará en una consulta SQL lista para usar.")

    if st.button("🔃 Cambiar Precisión del Modelo"):
        st.session_state["model"] = None
        st.session_state.model_loaded = False
        st.session_state.chat_history = []
        st.rerun()
    st.markdown("---")
    
    # --- Entrada de la pregunta del usuario (sin preguntas sugeridas) ---
    st.subheader("🤔 ¿Qué preguntas tienes hoy?")

    manual_question = st.text_input("Escribe tu pregunta:")

    final_question = manual_question

    if st.button("📥 Generar consulta SQL"):
        if not final_question.strip():
            st.warning("❗ Por favor, ingresa una pregunta válida.")
        else:
            with st.spinner("🔍 Generando consulta SQL... Esto puede tardar un momento."):
                start = time.time()
                generated_sql = model_usage.generate_sql(
                    final_question,
                    model=st.session_state["model"],
                    tokenizer=st.session_state["tokenizer"]
                )
                valid = sql_validator.check_sql_syntax(generated_sql)
                elapsed = time.time() - start

            st.success(f"✅ Consulta generada en {elapsed:.2f} segundos.")
            st.info(f"🔎 Validación de sintaxis: {'✅ Válida' if valid else '❌ Inválida'}")

            st.session_state.chat_history.append(
                {
                    "pregunta": final_question,
                    "respuesta": generated_sql,
                    "valida": valid,
                    "tiempo": elapsed
                }
            )

    st.markdown("---")

    # --- Mostrar historial tipo chat ---
    if st.session_state.chat_history:
        st.subheader("🧾 Historial de consultas")
        for i, msg in enumerate(st.session_state.chat_history[::-1]):
            st.markdown(f"**👤: ** {msg['pregunta']}")
            st.markdown("**🧠: **")
            st.code(msg['respuesta'], language="sql")
            st.caption(f"⏱️ Tiempo: {msg['tiempo']:.2f}s · 🧪 Sintaxis válida: {'✅ Sí' if msg['valida'] else '❌ No'}")
            if i < len(st.session_state.chat_history) - 1:
                st.markdown("---")
