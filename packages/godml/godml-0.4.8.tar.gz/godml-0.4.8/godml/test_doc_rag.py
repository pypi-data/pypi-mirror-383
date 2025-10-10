from godml.advisor_service.doc_rag_advisor import DocRAGAdvisor

def main():
    # Inicializamos el RAG con el índice generado
    bot = DocRAGAdvisor(doc_index_path="godml_doc_index.json")

    # Preguntas de validación
    preguntas = [
        "¿Qué hace la función train_model?",
        "Dame un ejemplo de cómo usar quick_train_yaml",
        "¿Para qué sirve dataprep_run_inline?",
        "¿Qué retorna compare_models?",
        "¿Cómo funciona advisor_full_report?"
    ]


    for q in preguntas:
        print("\n❓", q)
        print("💡", bot.ask(q))

if __name__ == "__main__":
    main()
