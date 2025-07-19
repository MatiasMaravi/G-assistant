import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from gmail import get_gmail_service, listar_correos_con_campos
import datetime
import json
import re

class ClasificadorFinanciero:
    def __init__(self):
        # Inicializar Vertex AI
        vertexai.init(project="gassistant-466419", location="us-central1")
        self.model = GenerativeModel("gemini-2.0-flash-001")
        self.gmail_service = get_gmail_service()
        self.correos_historicos = None
        
    def cargar_correos_historicos(self, archivo_excel="mis_correos_semana.xlsx"):
        """Carga los correos históricos del archivo Excel"""
        try:
            self.correos_historicos = pd.read_excel(archivo_excel)
            print(f"✅ Cargados {len(self.correos_historicos)} correos históricos")
            return True
        except Exception as e:
            print(f"❌ Error cargando correos históricos: {e}")
            return False
    
    def es_correo_financiero(self, correo):
        """Determina si un correo contiene información financiera"""
        subject = str(correo.get('subject', '')).upper()
        from_email = str(correo.get('from', '')).lower()
        
        # Palabras clave financieras en el asunto
        palabras_financieras = [
            'PAGO', 'PAYMENT', 'TRANSFERENCIA', 'TRANSFER', 'COMPRA', 'PURCHASE',
            'FACTURA', 'INVOICE', 'RECIBO', 'RECEIPT', 'COBRO', 'CHARGE',
            'TARJETA', 'CARD', 'DÉBITO', 'DEBIT', 'CRÉDITO', 'CREDIT',
            'BANCO', 'BANK', 'CUENTA', 'ACCOUNT', 'SALDO', 'BALANCE',
            'TRANSACCIÓN', 'TRANSACTION', 'MOVIMIENTO', 'MOVEMENT',
            'RETIRO', 'WITHDRAWAL', 'DEPÓSITO', 'DEPOSIT', 'AHORRO', 'SAVINGS',
            'PRÉSTAMO', 'LOAN', 'CUOTA', 'INSTALLMENT', 'INTERÉS', 'INTEREST',
            'COMISIÓN', 'COMMISSION', 'FEE', 'COSTO', 'COST', 'PRECIO', 'PRICE',
            'TOTAL', 'AMOUNT', 'SUMA', 'MONTO', 'VALOR', 'VALUE',
            'YAPE', 'PLIN', 'BCP', 'BBVA', 'INTERBANK', 'SCOTIABANK',
            'VISA', 'MASTERCARD', 'AMERICAN EXPRESS', 'DINERS'
        ]
        
        # Remitentes financieros conocidos
        remitentes_financieros = [
            'banco', 'bank', 'bcp', 'bbva', 'interbank', 'scotiabank',
            'visa', 'mastercard', 'yape', 'plin', 'paypal', 'mercadopago',
            'culqi', 'izipay', 'payme', 'tunki', 'lukita', 'billetera',
            'wallet', 'fintech', 'nequi', 'daviplata', 'financier',
            'credito', 'prestamo', 'seguros', 'insurance', 'sunat',
            'tributario', 'tax', 'facturacion', 'billing', 'cobranza'
        ]
        
        # Patrones de montos (S/, $, €, etc.)
        patron_monto = r'[S$€£¥]\s*[\d,]+\.?\d*|[\d,]+\.?\d*\s*[S$€£¥]|PEN|USD|EUR|GBP'
        
        # Verificar criterios
        tiene_palabra_financiera = any(palabra in subject for palabra in palabras_financieras)
        tiene_remitente_financiero = any(keyword in from_email for keyword in remitentes_financieros)
        tiene_monto = bool(re.search(patron_monto, subject))
        
        return tiene_palabra_financiera or tiene_remitente_financiero or tiene_monto
    
    def extraer_correos_financieros(self, dias=30):
        """Extrae correos financieros de los últimos X días"""
        print(f"🔄 Obteniendo correos de los últimos {dias} días...")
        
        # Obtener correos recientes
        correos = listar_correos_con_campos(self.gmail_service, days=dias)
        
        # Filtrar solo correos financieros
        correos_financieros = []
        for correo in correos:
            if self.es_correo_financiero(correo):
                correos_financieros.append(correo)
        
        print(f"✅ Encontrados {len(correos_financieros)} correos financieros de {len(correos)} totales")
        return correos_financieros
    
    def generar_contexto_clasificacion_financiera(self):
        """Genera contexto para clasificar tipos de gastos"""
        return """
        Eres un clasificador especializado en correos financieros. Tu tarea es clasificar correos en las 6 categorías más importantes de gastos.

        CATEGORÍAS DE CLASIFICACIÓN (SOLO 6):

        🍕 ALIMENTACIÓN:
        - Supermercados, restaurantes, delivery de comida
        - Cafeterías, panaderías, mercados, apps de comida

        🚗 TRANSPORTE:
        - Combustible, peajes, estacionamiento
        - Uber, taxi, transporte público, mantenimiento de vehículo

        🛒 COMPRAS:
        - Amazon, MercadoLibre, tiendas online y físicas
        - Electrodomésticos, tecnología, ropa, accesorios

        � SERVICIOS:
        - Servicios básicos (luz, agua, gas, internet, teléfono)
        - Alquiler, seguros, suscripciones, streaming

        💳 BANCARIO:
        - Comisiones bancarias, intereses, seguros
        - Transferencias, cambio de divisas, tarjetas de crédito

        � ENTRETENIMIENTO:
        - Cine, streaming, juegos, conciertos, gym
        - Deportes, hobbies, actividades recreativas

        Si un gasto no encaja claramente en ninguna categoría, asígnalo a la más cercana.
        """
    
    def clasificar_correo_financiero(self, correo):
        """Clasifica un correo financiero por tipo de gasto"""
        contexto = self.generar_contexto_clasificacion_financiera()
        
        # Extraer información del monto si está disponible
        subject = str(correo.get('subject', ''))
        from_email = str(correo.get('from', ''))
        
        # Buscar montos en el asunto
        patron_monto = r'[S$€£¥]\s*[\d,]+\.?\d*|[\d,]+\.?\d*\s*[S$€£¥]'
        montos_encontrados = re.findall(patron_monto, subject)
        monto_info = f"Montos encontrados: {montos_encontrados}" if montos_encontrados else "Sin monto visible"
        
        prompt = f"""
        {contexto}

        CORREO FINANCIERO A CLASIFICAR:
        Asunto: {subject}
        De: {from_email}
        {monto_info}

        Analiza este correo y clasifícalo en UNA de las categorías listadas arriba.
        
        INSTRUCCIONES:
        1. Lee cuidadosamente el asunto y remitente
        2. Identifica de qué tipo de gasto se trata
        3. Asigna la categoría más apropiada
        4. Si detectas un monto, inclúyelo en tu respuesta
        
        Responde EXACTAMENTE en este formato:
        CATEGORIA|monto_detectado|justificación_breve
        
        Donde:
        - CATEGORIA es una de: ALIMENTACIÓN, TRANSPORTE, COMPRAS, SERVICIOS, BANCARIO, ENTRETENIMIENTO
        - monto_detectado es el monto encontrado o "N/A"
        - justificación_breve es una explicación corta (máximo 30 palabras)
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 200
                }
            )
            return response.text.strip()
        except Exception as e:
            return f"ERROR|N/A|No se pudo clasificar: {e}"
    
    def procesar_correos_financieros(self, dias=30, exportar_excel=True):
        """Procesa y clasifica todos los correos financieros"""
        print("=" * 80)
        print("💰 CLASIFICADOR FINANCIERO DE CORREOS")
        print("=" * 80)
        
        # Extraer correos financieros
        correos_financieros = self.extraer_correos_financieros(dias)
        
        if not correos_financieros:
            print("ℹ️  No se encontraron correos financieros")
            return
        
        print(f"\n💳 Clasificando {len(correos_financieros)} correos financieros...\n")
        
        # Contadores por categoría
        categorias_count = {}
        resultados = []
        
        for i, correo in enumerate(correos_financieros, 1):
            print(f"--- CORREO FINANCIERO {i}/{len(correos_financieros)} ---")
            print(f"📨 Asunto: {correo.get('subject', 'Sin asunto')[:60]}...")
            print(f"👤 De: {correo.get('from', 'Desconocido')[:40]}...")
            
            # Clasificar
            clasificacion = self.clasificar_correo_financiero(correo)
            
            if "|" in clasificacion:
                partes = clasificacion.split("|", 2)
                categoria = partes[0].strip() if len(partes) > 0 else "COMPRAS"
                monto = partes[1].strip() if len(partes) > 1 else "N/A"
                justificacion = partes[2].strip() if len(partes) > 2 else "Sin justificación"
            else:
                categoria = "COMPRAS"
                monto = "N/A"
                justificacion = clasificacion
            
            # Mapear emojis por categoría (solo 6 categorías)
            emojis = {
                'ALIMENTACIÓN': '🍕',
                'TRANSPORTE': '🚗', 
                'COMPRAS': '🛒',
                'SERVICIOS': '🏠',
                'BANCARIO': '💳',
                'ENTRETENIMIENTO': '🎮'
            }
            
            emoji = emojis.get(categoria, '🛒')
            print(f"{emoji} CATEGORÍA: {categoria}")
            if monto != "N/A":
                print(f"💵 Monto: {monto}")
            print(f"💭 Justificación: {justificacion}")
            
            # Contar categorías
            categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
            
            # Guardar resultado
            resultados.append({
                'fecha': correo.get('date', ''),
                'asunto': correo.get('subject', ''),
                'remitente': correo.get('from', ''),
                'categoria': categoria,
                'monto': monto,
                'justificacion': justificacion,
                'labels': correo.get('label_names', [])
            })
            
            print("=" * 60)
            print()
        
        # Exportar a Excel si se solicita
        if exportar_excel and resultados:
            filename = f"correos_financieros_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df = pd.DataFrame(resultados)
            df.to_excel(filename, index=False)
            print(f"📊 Resultados exportados a: {filename}")
        
        # Mostrar resumen por categorías
        print("\n📊 RESUMEN POR CATEGORÍAS:")
        for categoria, count in sorted(categorias_count.items()):
            emoji = emojis.get(categoria, '🛒')
            print(f"{emoji} {categoria}: {count} correos")
        
        print(f"\n💰 Total correos financieros procesados: {len(resultados)}")
        print("=" * 80)
        
        return resultados

def main():
    clasificador = ClasificadorFinanciero()
    
    print("💰 CLASIFICADOR FINANCIERO DE CORREOS")
    print("=" * 50)
    print("Este script identifica y clasifica correos con información financiera")
    print("=" * 50)
    
    try:
        dias = input("¿Cuántos días atrás buscar? (default: 30): ").strip()
        dias = int(dias) if dias else 30
        
        exportar = input("¿Exportar resultados a Excel? (s/n, default: s): ").strip().lower()
        exportar_excel = exportar != 'n'
        
        print(f"\n🔍 Buscando correos financieros de los últimos {dias} días...")
        resultados = clasificador.procesar_correos_financieros(dias=dias, exportar_excel=exportar_excel)
        
        if resultados:
            print(f"\n✅ Proceso completado exitosamente!")
            print(f"📈 Se clasificaron {len(resultados)} correos financieros")
        else:
            print("\n❌ No se encontraron correos financieros en el período especificado")
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
    except ValueError:
        print("❌ Error: Ingresa un número válido para los días")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
