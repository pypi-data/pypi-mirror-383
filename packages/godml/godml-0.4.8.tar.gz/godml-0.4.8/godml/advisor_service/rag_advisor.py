# godml/advisor_service/rag_advisor.py

import json
import re
from difflib import SequenceMatcher
from gpt4all import GPT4All
from godml.advisor_service.schemas import RecipeSchema


class RAGAdvisor:
    def __init__(self,
                 model_name="q4_0-orca-mini-3b.gguf",
                 model_path="C:/Users/arturo/.gpt4all/models",
                 examples_path="recipes_examples.json"):
        self.model = GPT4All(model_name, model_path=model_path)
        with open(examples_path, "r", encoding="utf-8") as f:
            self.examples = json.load(f)

    def retrieve_examples(self, dataset_summary, top_k=2):
        scored = [(e, SequenceMatcher(None, dataset_summary, e["summary"]).ratio())
                  for e in self.examples]
        return [s[0] for s in sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]]

    def _extract_first_json(self, raw_output: str) -> str:
        """
        Extrae el primer bloque JSON válido del texto, incluso si hay ruido.
        - Busca balance de llaves { }
        - Arregla comas colgantes
        """
        start = raw_output.find("{")
        if start == -1:
            raise ValueError("⚠️ No se encontró '{' en salida del LLM")

        depth, i = 0, start
        for i, ch in enumerate(raw_output[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = raw_output[start:i+1]
                    break
        else:
            raise ValueError("⚠️ No se cerró JSON en salida del LLM")

        # 🔹 Limpiar problemas comunes
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)  # comas colgantes
        candidate = candidate.replace("true", "true").replace("false", "false").replace("null", "null")

        return candidate

    def suggest_recipe(self, dataset_summary: str):
        examples = self.retrieve_examples(dataset_summary, top_k=2)
        examples_text = "\n\n".join([
            f"Ejemplo:\nDataset: {e['summary']}\nReceta:\n{json.dumps(e['recipe'], indent=2)}"
            for e in examples
        ])

        prompt = f"""
Eres un experto en ciencia de datos y GODML.
Genera una receta de DataPrep en formato JSON para usar en un notebook.

Reglas:
- SOLO devuelve JSON válido con inputs, steps y outputs.
- No devuelvas explicaciones ni comentarios.

Ejemplos:
{examples_text}

Ahora genera la receta para:
Dataset: {dataset_summary}
Receta:
"""
        raw_output = self.model.generate(prompt, max_tokens=800)
        print("📝 Respuesta cruda del LLM:\n", raw_output)

        try:
            # 🔹 Extraer primer bloque JSON limpio
            cleaned = self._extract_first_json(raw_output)
            recipe_dict = json.loads(cleaned)

            # 🔹 Validar contra schema
            validated = RecipeSchema(**recipe_dict)
            return validated.dict()

        except Exception as e:
            print(f"⚠️ Error validando receta tras limpiar: {e}")
            return self.fallback_recipe()

    def fallback_recipe(self):
        """Receta mínima por defecto"""
        return {
            "inputs": [{"name": "raw", "connector": "csv", "uri": "inp"}],
            "steps": [{"op": "drop_duplicates", "params": {}}],
            "outputs": [{"name": "clean", "connector": "csv", "uri": "out"}],
        }
