import streamlit as st
import core.llm_management as llm_management
import core.model_usage as model_usage
import services.sql_validator as sql_validator

st.set_page_config(page_title="Generador de SQL", layout="centered")

st.title("🔍 Generador de consultas SQL usando LLM")

# --- Sidebar: Configuración del modelo ---
st.sidebar.header("⚙️ Configuración del modelo")

dtype_option = st.sidebar.radio(
    "Selecciona el tipo de precisión:",
    options=["float16", "float32"],
    index=0,
    help="Usa float16 para menor consumo de memoria o float32 para más precisión."
)

if "model" not in st.session_state:
    with st.spinner("Cargando modelo y tokenizer..."):
        tokenizer = llm_management.load_tokenizer()
        model = llm_management.load_model(dtype_option)
        st.session_state["model"] = model
        st.session_state["tokenizer"] = tokenizer

# --- Entrada del usuario ---
st.subheader("Escribe una pregunta en lenguaje natural")
question = st.text_area("Pregunta:", placeholder="¿Cuáles empleados ganan más de 2000 euros?", height=100)

if st.button("Generar consulta SQL", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Por favor, escribe una pregunta válida.")
    else:
        with st.spinner("Generando consulta..."):
            import time
            start = time.time()
            generated_sql = model_usage.generate_sql(
                question,
                model=st.session_state["model"],
                tokenizer=st.session_state["tokenizer"]
            )
            valid = sql_validator.check_sql_syntax(generated_sql)
            elapsed = time.time() - start

        # --- Resultados ---
        st.markdown("### Resultado")

        if valid:
            st.success("Consulta generada correctamente.")
        else:
            st.error("Consulta generada con errores de sintaxis.")


        #st.success("Consulta generada correctamente.") if valid else st.error("Consulta generada con errores de sintaxis.")
        
        st.code(generated_sql, language="sql")

        col1, col2 = st.columns(2)
        col1.metric("⏱️ Tiempo de inferencia", f"{elapsed:.2f} s")
        col2.metric("✅ Sintaxis válida", "Sí" if valid else "No")
