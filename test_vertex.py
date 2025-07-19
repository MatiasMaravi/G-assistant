import vertexai

def test_connection():
    try:
        # Inicializa Vertex AI
        vertexai.init(project="gassistant-466419", location="us-central1")
        print("✅ Conexión a Vertex AI establecida correctamente")
        
        # Probar lista de modelos disponibles
        from vertexai import generative_models
        print("✅ Módulo generative_models importado correctamente")
        
        # AHORA vamos a intentar cargar un modelo específico
        print("🔄 Intentando cargar modelo gemini-1.5-pro...")
        from vertexai.generative_models import GenerativeModel
        model = GenerativeModel("gemini-2.0-flash-001")
        print("✅ Modelo cargado exitosamente!")
        
        # AHORA vamos a intentar generar contenido
        print("🔄 Intentando generar contenido...")
        response = model.generate_content(
            "Di solo 'HOLA'",
            generation_config={
                "temperature": 0.0,
                "max_output_tokens": 200  # Aumentamos los tokens
            }
        )
        print(f"✅ Respuesta: {response.text}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
