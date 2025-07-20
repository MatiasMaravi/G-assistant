import json
import re
import datetime

# Importar Vertex AI
import vertexai
from vertexai.generative_models import GenerativeModel

# Pandas es opcional - solo para compatibilidad con el código legacy
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas no disponible - funcionalidad de Excel deshabilitada")

class ClasificadorBCP:
    def __init__(self):
        # Inicializar Vertex AI
        vertexai.init(project="gassistant-466419", location="us-central1")
        self.model = GenerativeModel("gemini-2.0-flash-001")
        self.datos_bcp = None
        
    def cargar_datos_bcp(self, archivo_json="bcp-consumos-ultimos-7-dias.json"):
        """Carga los datos financieros desde el JSON del BCP"""
        try:
            with open(archivo_json, 'r', encoding='utf-8') as file:
                self.datos_bcp = json.load(file)
            print(f"✅ Cargados {self.datos_bcp.get('totalEmails', 0)} consumos del BCP")
            return True
        except Exception as e:
            print(f"❌ Error cargando datos del BCP: {e}")
            return False
    
    def extraer_datos_consumo(self, email):
        """Extrae datos específicos de un email de consumo del BCP"""
        snippet = email.get('snippet', '')
        subject = email.get('subject', '')
        
        # Extraer monto usando regex más específico
        monto_match = re.search(r'S/\s*([\d,]+\.?\d*)', snippet)
        monto = monto_match.group(0) if monto_match else "N/A"
        
        # Extraer empresa/comercio
        # Buscar patrón "con tu Tarjeta de [Débito/Crédito] BCP en [EMPRESA]"
        empresa_match = re.search(r'BCP en (.+?)\.', snippet)
        empresa = empresa_match.group(1).strip() if empresa_match else "N/A"
        
        # Extraer fecha del email
        fecha = email.get('date', '')
        
        # Determinar tipo de tarjeta
        tipo_tarjeta = "Crédito" if "Crédito" in snippet else "Débito" if "Débito" in snippet else "N/A"
        
        return {
            'monto': monto,
            'empresa': empresa,
            'fecha': fecha,
            'tipo_tarjeta': tipo_tarjeta,
            'email_id': email.get('id', ''),
            'leido': str(email.get('isRead', False)).upper()
        }
    
    def generar_contexto_clasificacion(self):
        """Genera contexto para clasificar tipos de gastos basado en las 6 categorías"""
        return """
        Eres un clasificador especializado en gastos bancarios. Clasifica cada consumo en UNA de estas 6 categorías:

        🍕 ALIMENTACIÓN:
        - Restaurantes: KFC, McDonald's, Pizza Hut, Chilis, etc.
        - Supermercados: Plaza Vea, Metro, Tottus, Wong, Vivanda
        - Delivery: Rappi, UberEats, PedidosYa, Glovo
        - Cafeterías: Starbucks, Juan Valdez, San Antonio
        - Panaderías, mercados, tiendas de conveniencia como Tambo

        🚗 TRANSPORTE:
        - Uber, taxi, apps de transporte
        - Combustible: Primax, Petroperú, Repsol
        - Peajes, estacionamiento
        - Mantenimiento de vehículo, talleres

        🛒 COMPRAS:
        - Tiendas por departamento: Falabella, Ripley, Saga
        - Tiendas online: Amazon, MercadoLibre
        - Ropa: Zara, H&M, Forever 21
        - Tecnología: Apple Store, Samsung, tiendas de electrónicos
        - Farmacias: InkaFarma, Boticas, Mifarma

        🏠 SERVICIOS:
        - Servicios básicos: Luz del Sur, Sedapal, gas, internet, telefonía
        - Streaming: Netflix, Spotify, Disney+, Amazon Prime
        - Suscripciones: Google, Microsoft, Adobe
        - Seguros, alquiler

        💳 BANCARIO:
        - Comisiones bancarias, mantenimiento de cuenta
        - Transferencias, cambio de divisas
        - Intereses, pagos de tarjetas
        - Servicios financieros

        🎮 ENTRETENIMIENTO:
        - Cines: Cineplex, Cineplanet, UVK
        - Gimnasios, deportes
        - Juegos, apps de entretenimiento
        - Eventos, conciertos, actividades recreativas

        REGLAS:
        - Si reconoces el nombre del comercio, clasifícalo según su rubro principal
        - TAMBO y tiendas de conveniencia = ALIMENTACIÓN
        - MEGA PLAZA y centros comerciales = COMPRAS (a menos que sepas el comercio específico)
        - GOOGLE = SERVICIOS (suscripciones digitales)
        - Si no estás seguro, usa la categoría más probable según el contexto
        """
    
    def clasificar_consumo(self, datos_consumo):
        """Clasifica un consumo individual usando Gemini"""
        contexto = self.generar_contexto_clasificacion()
        
        prompt = f"""
        {contexto}

        CONSUMO A CLASIFICAR:
        Empresa/Comercio: {datos_consumo['empresa']}
        Monto: {datos_consumo['monto']}
        Tipo de tarjeta: {datos_consumo['tipo_tarjeta']}
        Fecha: {datos_consumo['fecha']}

        Analiza el nombre del comercio y clasifica este gasto.
        
        Responde EXACTAMENTE en este formato:
        CATEGORIA|justificación_breve
        
        Donde CATEGORIA es una de: ALIMENTACIÓN, TRANSPORTE, COMPRAS, SERVICIOS, BANCARIO, ENTRETENIMIENTO
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 100
                }
            )
            return response.text.strip()
        except Exception as e:
            return f"ERROR|No se pudo clasificar: {e}"
    
    def procesar_consumos_bcp(self, exportar_json=True):
        """Procesa y clasifica todos los consumos del BCP"""
        print("=" * 80)
        print("💳 CLASIFICADOR DE CONSUMOS BCP")
        print("=" * 80)
        
        if not self.cargar_datos_bcp():
            print("❌ No se pudieron cargar los datos del BCP")
            return
        
        emails = self.datos_bcp.get('emails', [])
        if not emails:
            print("ℹ️  No se encontraron consumos para procesar")
            return
        
        print(f"\n💰 Clasificando {len(emails)} consumos del BCP...\n")
        
        # Contadores por categoría
        categorias_count = {}
        total_por_categoria = {}
        consumos_por_categoria = {}
        resultados = []
        
        # Emojis por categoría
        emojis = {
            'ALIMENTACIÓN': '🍕',
            'TRANSPORTE': '🚗', 
            'COMPRAS': '🛒',
            'SERVICIOS': '🏠',
            'BANCARIO': '💳',
            'ENTRETENIMIENTO': '🎮'
        }
        
        # Inicializar categorías
        for categoria in emojis.keys():
            consumos_por_categoria[categoria] = []
        
        for i, email in enumerate(emails, 1):
            print(f"--- CONSUMO {i}/{len(emails)} ---")
            
            # Extraer datos del consumo
            datos_consumo = self.extraer_datos_consumo(email)
            
            print(f"💰 Monto: {datos_consumo['monto']}")
            print(f"🏪 Empresa: {datos_consumo['empresa']}")
            print(f"💳 Tarjeta: {datos_consumo['tipo_tarjeta']}")
            
            # Clasificar
            clasificacion = self.clasificar_consumo(datos_consumo)
            
            if "|" in clasificacion:
                categoria, justificacion = clasificacion.split("|", 1)
                categoria = categoria.strip()
                justificacion = justificacion.strip()
            else:
                categoria = "COMPRAS"
                justificacion = clasificacion
            
            emoji = emojis.get(categoria, '🛒')
            print(f"{emoji} CATEGORÍA: {categoria}")
            print(f"💭 Justificación: {justificacion}")
            
            # Contar categorías y sumar montos
            categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
            
            # Extraer valor numérico del monto para sumar
            monto_numerico = 0
            if datos_consumo['monto'] != "N/A":
                try:
                    monto_str = datos_consumo['monto'].replace('S/', '').replace(',', '').strip()
                    monto_numerico = float(monto_str)
                except:
                    pass
            
            total_por_categoria[categoria] = total_por_categoria.get(categoria, 0) + monto_numerico
            
            # Crear detalle del consumo
            consumo_detalle = {
                'fecha': datos_consumo['fecha'],
                'empresa': datos_consumo['empresa'],
                'monto': datos_consumo['monto'],
                'monto_numerico': monto_numerico,
                'tipo_tarjeta': datos_consumo['tipo_tarjeta'],
                'justificacion': justificacion,
                'email_id': datos_consumo['email_id'],
                'leido': str(datos_consumo['leido']).upper() if isinstance(datos_consumo['leido'], bool) else datos_consumo['leido']
            }
            
            # Guardar resultado completo y por categoría
            resultados.append({**consumo_detalle, 'categoria': categoria})
            
            # Inicializar categoría si no existe
            if categoria not in consumos_por_categoria:
                consumos_por_categoria[categoria] = []
            
            consumos_por_categoria[categoria].append(consumo_detalle)
            
            print("=" * 60)
            print()
        
        # Exportar a JSON si se solicita
        if exportar_json and resultados:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"consumos_bcp_clasificados_{timestamp}.json"
            
            # Crear estructura completa del JSON
            resultado_completo = {
                "metadata": {
                    "fecha_proceso": datetime.datetime.now().isoformat(),
                    "total_consumos": len(resultados),
                    "total_gastado": sum(r['monto_numerico'] for r in resultados),
                    "periodo_datos": self.datos_bcp.get('exportDate', 'N/A'),
                    "fuente": "BCP - Consumos últimos 7 días"
                },
                "resumen_categorias": {},
                "consumos_por_categoria": {},
                "todos_los_consumos": resultados
            }
            
            # Agregar resumen y consumos por categoría
            for categoria in sorted(categorias_count.keys()):
                resultado_completo["resumen_categorias"][categoria] = {
                    "cantidad": categorias_count[categoria],
                    "total": round(total_por_categoria.get(categoria, 0), 2),
                    "emoji": emojis.get(categoria, '🛒')
                }
                
                # Agregar consumos de esta categoría
                resultado_completo["consumos_por_categoria"][categoria] = {
                    "emoji": emojis.get(categoria, '🛒'),
                    "total_categoria": round(total_por_categoria.get(categoria, 0), 2),
                    "cantidad_consumos": len(consumos_por_categoria.get(categoria, [])),
                    "consumos": consumos_por_categoria.get(categoria, [])
                }
            
            # Agregar categorías vacías para completitud
            for categoria, emoji in emojis.items():
                if categoria not in resultado_completo["consumos_por_categoria"]:
                    resultado_completo["consumos_por_categoria"][categoria] = {
                        "emoji": emoji,
                        "total_categoria": 0.0,
                        "cantidad_consumos": 0,
                        "consumos": []
                    }
            
            # Guardar JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultado_completo, f, ensure_ascii=False, indent=2)
            
            print(f"� Resultados exportados a JSON: {filename}")
        
        # Mostrar resumen por categorías
        print("\n📊 RESUMEN POR CATEGORÍAS:")
        total_general = 0
        for categoria in sorted(categorias_count.keys()):
            count = categorias_count[categoria]
            total_cat = total_por_categoria.get(categoria, 0)
            total_general += total_cat
            emoji = emojis.get(categoria, '🛒')
            print(f"{emoji} {categoria}: {count} consumos - S/ {total_cat:.2f}")
        
        print(f"\n💰 RESUMEN GENERAL:")
        print(f"📧 Total consumos procesados: {len(resultados)}")
        print(f"💵 Total gastado: S/ {total_general:.2f}")
        print(f"📅 Período: {self.datos_bcp.get('exportDate', 'N/A')}")
        print("=" * 80)
        
        return resultados
    
    def obtener_json_clasificado(self):
        """Retorna directamente el JSON clasificado sin exportar archivo"""
        if not self.cargar_datos_bcp():
            return None
        
        emails = self.datos_bcp.get('emails', [])
        if not emails:
            return None
        
        # Procesar sin mostrar en consola
        resultados = []
        categorias_count = {}
        total_por_categoria = {}
        consumos_por_categoria = {}
        
        emojis = {
            'ALIMENTACIÓN': '🍕', 'TRANSPORTE': '🚗', 'COMPRAS': '🛒',
            'SERVICIOS': '🏠', 'BANCARIO': '💳', 'ENTRETENIMIENTO': '🎮'
        }
        
        # Inicializar categorías
        for categoria in emojis.keys():
            consumos_por_categoria[categoria] = []
        
        for email in emails:
            datos_consumo = self.extraer_datos_consumo(email)
            clasificacion = self.clasificar_consumo(datos_consumo)
            
            if "|" in clasificacion:
                categoria, justificacion = clasificacion.split("|", 1)
                categoria = categoria.strip()
                justificacion = justificacion.strip()
            else:
                categoria = "COMPRAS"
                justificacion = clasificacion
            
            categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
            
            monto_numerico = 0
            if datos_consumo['monto'] != "N/A":
                try:
                    monto_str = datos_consumo['monto'].replace('S/', '').replace(',', '').strip()
                    monto_numerico = float(monto_str)
                except:
                    pass
            
            total_por_categoria[categoria] = total_por_categoria.get(categoria, 0) + monto_numerico
            
            consumo_detalle = {
                'fecha': datos_consumo['fecha'],
                'empresa': datos_consumo['empresa'],
                'monto': datos_consumo['monto'],
                'monto_numerico': monto_numerico,
                'tipo_tarjeta': datos_consumo['tipo_tarjeta'],
                'justificacion': justificacion,
                'email_id': datos_consumo['email_id'],
                'leido': str(datos_consumo['leido']).upper() if isinstance(datos_consumo['leido'], bool) else datos_consumo['leido']
            }
            
            # Agregar a la lista general y a la categoría específica
            resultados.append({**consumo_detalle, 'categoria': categoria})
            
            # Inicializar categoría si no existe
            if categoria not in consumos_por_categoria:
                consumos_por_categoria[categoria] = []
            
            consumos_por_categoria[categoria].append(consumo_detalle)
        
        # Crear JSON estructurado
        resultado_json = {
            "metadata": {
                "fecha_proceso": datetime.datetime.now().isoformat(),
                "total_consumos": len(resultados),
                "total_gastado": sum(r['monto_numerico'] for r in resultados),
                "periodo_datos": self.datos_bcp.get('exportDate', 'N/A'),
                "fuente": "BCP - Consumos últimos 7 días"
            },
            "resumen_categorias": {},
            "consumos_por_categoria": {},
            "todos_los_consumos": resultados
        }
        
        # Agregar resumen y consumos por categoría
        for categoria in sorted(categorias_count.keys()):
            resultado_json["resumen_categorias"][categoria] = {
                "cantidad": categorias_count[categoria],
                "total": round(total_por_categoria.get(categoria, 0), 2),
                "emoji": emojis.get(categoria, '🛒')
            }
            
            # Agregar consumos de esta categoría
            resultado_json["consumos_por_categoria"][categoria] = {
                "emoji": emojis.get(categoria, '🛒'),
                "total_categoria": round(total_por_categoria.get(categoria, 0), 2),
                "cantidad_consumos": len(consumos_por_categoria.get(categoria, [])),
                "consumos": consumos_por_categoria.get(categoria, [])
            }
        
        # Agregar categorías vacías para completitud
        for categoria, emoji in emojis.items():
            if categoria not in resultado_json["consumos_por_categoria"]:
                resultado_json["consumos_por_categoria"][categoria] = {
                    "emoji": emoji,
                    "total_categoria": 0.0,
                    "cantidad_consumos": 0,
                    "consumos": []
                }
        
        return resultado_json

def main():
    clasificador = ClasificadorBCP()
    
    print("💳 CLASIFICADOR DE CONSUMOS BCP")
    print("=" * 50)
    print("Este script lee el JSON de consumos BCP y los clasifica automáticamente")
    print("=" * 50)
    
    try:
        print("Opciones disponibles:")
        print("1. Procesamiento completo con exportación a JSON")
        print("2. Solo obtener JSON en memoria (para desarrollo)")
        
        opcion = input("Elige una opción (1/2, default: 1): ").strip()
        
        if opcion == "2":
            print(f"\n🔍 Obteniendo JSON clasificado...")
            resultado_json = clasificador.obtener_json_clasificado()
            
            if resultado_json:
                print(f"\n✅ JSON generado exitosamente!")
                print(f"📈 Total consumos: {resultado_json['metadata']['total_consumos']}")
                print(f"💰 Total gastado: S/ {resultado_json['metadata']['total_gastado']:.2f}")
                
                # Mostrar resumen por categorías
                print(f"\n📊 Resumen por categorías:")
                for categoria, datos in resultado_json['resumen_categorias'].items():
                    print(f"{datos['emoji']} {categoria}: {datos['cantidad']} consumos - S/ {datos['total']}")
                
                # Opcionalmente guardar el JSON
                guardar = input(f"\n¿Guardar JSON en archivo? (s/n): ").strip().lower()
                if guardar == 's':
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
                    filename = f"consumos_bcp_clasificados_{timestamp}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(resultado_json, f, ensure_ascii=False, indent=2)
                    print(f"📄 JSON guardado como: {filename}")
                
                return resultado_json
            else:
                print("\n❌ No se encontraron consumos para procesar")
                return None
        else:
            exportar = input("¿Exportar resultados a JSON? (s/n, default: s): ").strip().lower()
            exportar_json = exportar != 'n'
            
            print(f"\n🔍 Procesando consumos del archivo JSON...")
            resultados = clasificador.procesar_consumos_bcp(exportar_json=exportar_json)
            
            if resultados:
                print(f"\n✅ Proceso completado exitosamente!")
                print(f"📈 Se clasificaron {len(resultados)} consumos")
                return resultados
            else:
                print("\n❌ No se encontraron consumos para procesar")
                return None
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    main()

# Ejemplo de uso directo para desarrolladores:
"""
# Para usar desde otro script:
from clasificador_bcp import ClasificadorBCP

clasificador = ClasificadorBCP()
resultado_json = clasificador.obtener_json_clasificado()

if resultado_json:
    print(f"Total gastado: S/ {resultado_json['metadata']['total_gastado']}")
    
    # Acceder a consumos por categoría
    for consumo in resultado_json['consumos']:
        if consumo['categoria'] == 'ALIMENTACIÓN':
            print(f"Gasto en {consumo['empresa']}: {consumo['monto']}")
"""
