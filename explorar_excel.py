import pandas as pd
import os

def explorar_correos_excel():
    """Explora la estructura del archivo Excel con correos"""
    archivo = "mis_correos_semana.xlsx"
    
    if not os.path.exists(archivo):
        print(f"❌ No se encuentra el archivo {archivo}")
        return
    
    try:
        # Leer archivo Excel
        df = pd.read_excel(archivo)
        
        print("📊 ESTRUCTURA DEL ARCHIVO DE CORREOS:")
        print("=" * 50)
        print(f"Total de correos: {len(df)}")
        print(f"Columnas disponibles: {list(df.columns)}")
        print("\n📋 Primeras 3 filas:")
        print(df.head(3).to_string())
        
        print("\n🏷️ ANÁLISIS DE LABELS:")
        if 'label_names' in df.columns:
            # Mostrar los labels más comunes
            all_labels = []
            for labels in df['label_names'].dropna():
                if isinstance(labels, str):
                    # Si es string, intentar convertir de lista
                    if labels.startswith('[') and labels.endswith(']'):
                        try:
                            import ast
                            labels_list = ast.literal_eval(labels)
                            all_labels.extend(labels_list)
                        except:
                            all_labels.append(labels)
                    else:
                        all_labels.append(labels)
                elif isinstance(labels, list):
                    all_labels.extend(labels)
            
            label_counts = pd.Series(all_labels).value_counts()
            print("Labels más comunes:")
            print(label_counts.head(10))
        
        print("\n📨 MUESTRA DE CORREOS:")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"\nCorreo {i+1}:")
            print(f"  Asunto: {str(row.get('subject', 'Sin asunto'))[:60]}...")
            print(f"  De: {str(row.get('from', 'Desconocido'))[:40]}...")
            print(f"  Labels: {row.get('label_names', [])}")
            
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

if __name__ == "__main__":
    explorar_correos_excel()
