import core.model_usage as model_usage
import core.llm_management as llm_management

tokenizer = llm_management.load_tokenizer()

preferred_torch_dtype = model_usage.select_model_dtype()
model = llm_management.load_model(preferred_torch_dtype)

question = None
while True:
    question = input("Escribe tu pregunta: ")
    if question != "bye":
        print("-"*20)
        print("Generando query...")
        model_usage.use_model_and_calculate_metrics(question,model=model, tokenizer=tokenizer)
        print("-"*40+"\n")
    else:
        print("Fin.")
        break
