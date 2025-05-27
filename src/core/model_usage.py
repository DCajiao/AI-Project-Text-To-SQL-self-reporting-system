import json
import time

import services.sql_validator as sql_validator
import utils.definitions as definitions

def select_model_dtype():
    """
    Selecciona el tipo de dato preferido para el modelo basado en la entrada del usuario.
    """
    print("Usar en modo bajo consumo de memoria y velocidad de inferencia.")
    print("Elige el tipo de dato preferido para el modelo:")
    print("1. float16 (menos preciso, pero más rápido y con menos uso de memoria)")
    print("2. float32 (más preciso, pero más lento y con mayor uso de memoria)")

    preferred_torch_dtype = input(" ")

    if preferred_torch_dtype == "1":
        return "float16"
    elif preferred_torch_dtype == "2":
        return "float32"
    else:
        raise ValueError("Tipo de dato no válido. Debe ser 1, 2 o 3.")


def format_schema():
    erp_schema_json_path = f"{definitions.TRAINING_DATA_PATH}/schema.json"
    
    with open(erp_schema_json_path, "r", encoding="utf-8") as f:
        schema = json.load(f)["schema_context"]

    schema_lines = [
        "Contexto: Las siguientes tablas conforman el esquema ERP_SCHEMA:"]
    for table in schema:
        # Se listan las columnas de cada tabla junto con sus tipos de datos
        cols = ", ".join([f"{col} ({dtype})" for col,
                         dtype in table["columns"].items()])
        # Se agrega la descripción funcional de la tabla para ayudar al modelo a comprender su propósito
        schema_lines.append(
            f"- {table['table']}({cols})\n  → {table['description']}")
    return "\n".join(schema_lines)


def generate_sql(question, model=None, tokenizer=None):
    # Se agrega todo el contexto del schema al prompt
    schema_context = format_schema()

    # Se construye un prompt completo con el esquema + una instrucción + la pregunta
    prompt = (
        f"{schema_context}\n"
        f"Instrucción: Genera solamente una consulta SQL que responda a la pregunta a partir del esquema ERP_SCHEMA.\n"
        f"Pregunta: {question}\n"
        f"SQL:"
    )

    # Se tokeniza el prompt y se lo pasa al modelo para generar una respuesta
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,  # Límite máximo de tokens para la salida
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )

    # Decodificación del resultado generado a texto legible
    # Toma solo la primera línea de la consulta
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extracción únicamente de la parte relevante (la sentencia SQL)
    if "SQL:" in decoded:
        decoded = decoded.split("SQL:")[-1]
    decoded = decoded.strip().split("\n")[0]  # tomar solo la primera línea
    return decoded


def use_model_and_calculate_metrics(question, model, tokenizer):
    # Tiempo de inicio
    start_time = time.time()

    # --- Uso del modelo ---
    generated_sql = generate_sql(question, model, tokenizer)
    print(f"🧠 Pregunta: {question}")
    print(f"🤖 Generado: {generated_sql}")
    valid = sql_validator.check_sql_syntax(generated_sql)

    # Medición después
    end_time = time.time()

    # --- Resultados ---
    print(f"📊 Tiempo: {end_time - start_time:.2f} segundos")
