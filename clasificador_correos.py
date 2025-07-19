import pandas as pd
import vertexai
from vertexai.generative_models import GenerativeModel
from gmail import get_gmail_service, listar_correos_con_campos, mover_correo_a_spam
import datetime
import json

class ClasificadorCorreos:
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
    
    def generar_contexto_entrenamiento(self):
        """Genera un contexto de entrenamiento basado en los correos históricos"""
        if self.correos_historicos is None:
            return ""
        
        # Analizar patrones más específicos en los datos históricos
        correos_importantes = []
        correos_no_importantes = []
        
        # Dominios de trabajo comunes (puedes personalizar)
        dominios_trabajo = ['@work.com', '@empresa.com', '@company.com', '@office.com', '@trabajo.com']
        
        for _, correo in self.correos_historicos.iterrows():
            labels = str(correo.get('label_names', ''))
            subject = str(correo.get('subject', ''))
            from_email = str(correo.get('from', ''))
            
            # CRITERIOS MÁS ESTRICTOS PARA IMPORTANTE
            es_importante = any([
                # Labels que indican importancia real
                'IMPORTANT' in labels.upper(),
                'STARRED' in labels.upper(),
                'PRIORITY' in labels.upper(),
                # Palabras clave específicas en el asunto
                any(keyword in subject.upper() for keyword in [
                    'URGENTE', 'IMPORTANTE', 'PRIORITY', 'URGENT', 'CRÍTICO', 'CRITICAL',
                    'FACTURA', 'INVOICE', 'PAGO', 'PAYMENT', 'VENCIMIENTO', 'DUE',
                    'REUNIÓN', 'MEETING', 'CITA', 'APPOINTMENT'
                ]),
                # Remitentes de trabajo o institucionales
                any(domain in from_email.lower() for domain in dominios_trabajo),
                # Remitentes bancarios o gubernamentales
                any(keyword in from_email.lower() for keyword in [
                    'banco', 'bank', 'sunat', 'gobierno', 'ministerio', 'seguro'
                ])
            ])
            
            # CRITERIOS PARA NO IMPORTANTE (más específicos)
            es_no_importante = any([
                # Labels que claramente indican no importancia
                'CATEGORY_PROMOTIONS' in labels.upper(),
                'CATEGORY_SOCIAL' in labels.upper(),
                'SPAM' in labels.upper(),
                'TRASH' in labels.upper(),
                # Solo UNREAD sin otros labels importantes
                (labels.count('UNREAD') > 0 and 'IMPORTANT' not in labels.upper() and 'STARRED' not in labels.upper()),
                # Remitentes promocionales conocidos
                any(keyword in from_email.lower() for keyword in [
                    'noreply', 'no-reply', 'newsletter', 'marketing', 'promo', 'offer',
                    'duolingo', 'youtube', 'facebook', 'instagram', 'twitter', 'linkedin',
                    'amazon', 'mercadolibre', 'aliexpress'
                ]),
                # Asuntos promocionales
                any(keyword in subject.upper() for keyword in [
                    'OFERTA', 'DESCUENTO', 'PROMOCIÓN', 'SALE', 'OFFER', 'DISCOUNT',
                    'GRATIS', 'FREE', 'NEWSLETTER', 'SUSCRIPCIÓN'
                ])
            ])
            
            # Recopilar ejemplos balanceados
            if es_importante and len(correos_importantes) < 15:
                correos_importantes.append({
                    'subject': subject[:80],  # Limitar longitud
                    'from': from_email[:50],
                    'labels': labels,
                    'categoria': 'IMPORTANTE'
                })
            elif es_no_importante and len(correos_no_importantes) < 15:
                correos_no_importantes.append({
                    'subject': subject[:80],
                    'from': from_email[:50],
                    'labels': labels,
                    'categoria': 'NO_IMPORTANTE'
                })
        
        # Agregar algunos ejemplos aleatorios si no tenemos suficientes
        if len(correos_no_importantes) < 10:
            for _, correo in self.correos_historicos.sample(min(10, len(self.correos_historicos))).iterrows():
                labels = str(correo.get('label_names', ''))
                if 'IMPORTANT' not in labels.upper() and len(correos_no_importantes) < 15:
                    correos_no_importantes.append({
                        'subject': str(correo.get('subject', ''))[:80],
                        'from': str(correo.get('from', ''))[:50],
                        'labels': labels,
                        'categoria': 'NO_IMPORTANTE'
                    })
        
        contexto = f"""
        Eres un clasificador de correos entrenado con los siguientes datos históricos reales del usuario.

        CORREOS MARCADOS COMO IMPORTANTES ({len(correos_importantes)} ejemplos):
        {json.dumps(correos_importantes, indent=2, ensure_ascii=False)}

        CORREOS MARCADOS COMO NO IMPORTANTES ({len(correos_no_importantes)} ejemplos):
        {json.dumps(correos_no_importantes, indent=2, ensure_ascii=False)}

        REGLAS DE CLASIFICACIÓN APRENDIDAS:
        
        ✅ IMPORTANTE cuando:
        - Tiene labels: IMPORTANT, STARRED, PRIORITY
        - Asunto contiene: urgente, importante, factura, pago, reunión, cita, crítico
        - Remitente es: bancario, gubernamental, trabajo, seguros
        - Requiere acción inmediata del usuario
        
        ❌ NO IMPORTANTE cuando:
        - Tiene labels: CATEGORY_PROMOTIONS, CATEGORY_SOCIAL, SPAM
        - Solo tiene UNREAD sin otros labels importantes
        - Remitente es: noreply, marketing, redes sociales, tiendas online
        - Asunto contiene: oferta, descuento, promoción, gratis, newsletter
        - Es contenido promocional o social
        
        SÉ MUY ESTRICTO: Solo clasifica como IMPORTANTE si realmente requiere atención inmediata del usuario.
        """
        
        return contexto
    
    def clasificar_correo(self, correo):
        """Clasifica un correo individual usando Gemini"""
        contexto = self.generar_contexto_entrenamiento()
        
        prompt = f"""
        {contexto}

        CORREO A CLASIFICAR:
        Asunto: {correo.get('subject', '')}
        De: {correo.get('from', '')}
        Labels de Gmail: {correo.get('label_names', [])}

        Analiza este correo comparándolo con los ejemplos históricos.
        
        PREGÚNTATE:
        1. ¿Los labels son similares a correos importantes del historial?
        2. ¿El remitente es de tipo trabajo/bancario/gubernamental?
        3. ¿El asunto indica urgencia o requiere acción inmediata?
        4. ¿Es contenido promocional/social como en los ejemplos NO importantes?
        
        CLASIFICA como IMPORTANTE solo si:
        - Requiere acción inmediata del usuario
        - Es de un remitente crítico (trabajo, banco, gobierno)
        - Tiene labels que en el historial aparecen en correos importantes
        
        CLASIFICA como NO_IMPORTANTE si:
        - Es promocional, marketing o social
        - Solo tiene UNREAD sin otros labels importantes
        - El remitente es típicamente no crítico (redes sociales, tiendas, newsletters)
        
        Responde EXACTAMENTE en este formato:
        CLASIFICACION|justificación_breve
        
        Donde CLASIFICACION es solo "IMPORTANTE" o "NO_IMPORTANTE"
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.0,  # Más determinístico
                    "max_output_tokens": 150
                }
            )
            return response.text.strip()
        except Exception as e:
            return f"ERROR|No se pudo clasificar: {e}"
    
    def obtener_correos_nuevos(self, horas=24):
        """Obtiene correos nuevos de las últimas X horas"""
        print(f"🔄 Obteniendo correos de las últimas {horas} horas...")
        
        # Calcular fecha de inicio
        ahora = datetime.datetime.now()
        inicio = ahora - datetime.timedelta(hours=horas)
        
        # Usar el servicio de Gmail para obtener correos recientes
        correos = listar_correos_con_campos(self.gmail_service, days=1)
        
        # Filtrar solo los correos muy recientes
        correos_nuevos = []
        for correo in correos:
            # Aquí podrías agregar lógica más sofisticada para filtrar por fecha exacta
            # Por simplicidad, tomamos todos los del último día
            correos_nuevos.append(correo)
        
        print(f"✅ Encontrados {len(correos_nuevos)} correos recientes")
        return correos_nuevos
    
    def clasificar_correos_nuevos(self, horas=24, mover_a_spam=True):
        """Clasifica todos los correos nuevos y muestra resultados en consola"""
        print("=" * 80)
        print("🤖 CLASIFICADOR AUTOMÁTICO DE CORREOS")
        print("=" * 80)
        
        # Cargar datos históricos
        if not self.cargar_correos_historicos():
            print("❌ No se pudieron cargar los correos históricos")
            return
        
        # Obtener correos nuevos
        correos_nuevos = self.obtener_correos_nuevos(horas)
        
        if not correos_nuevos:
            print("ℹ️  No hay correos nuevos para clasificar")
            return
        
        print(f"\n📧 Clasificando {len(correos_nuevos)} correos nuevos...\n")
        
        importantes = 0
        no_importantes = 0
        correos_para_spam = []  # Lista de IDs para mover a spam
        
        for i, correo in enumerate(correos_nuevos, 1):
            print(f"--- CORREO {i}/{len(correos_nuevos)} ---")
            print(f"📨 Asunto: {correo.get('subject', 'Sin asunto')[:60]}...")
            print(f"👤 De: {correo.get('from', 'Desconocido')}")
            print(f"🏷️  Labels: {correo.get('label_names', [])}")
            
            # Clasificar
            clasificacion = self.clasificar_correo(correo)
            
            if "|" in clasificacion:
                categoria, justificacion = clasificacion.split("|", 1)
                categoria = categoria.strip()
                justificacion = justificacion.strip()
            else:
                categoria = clasificacion
                justificacion = "Sin justificación"
            
            if "IMPORTANTE" in categoria.upper():
                print(f"🔴 CLASIFICACIÓN: IMPORTANTE")
                importantes += 1
                emoji = "🔴"
            else:
                print(f"🔵 CLASIFICACIÓN: NO IMPORTANTE")
                no_importantes += 1
                emoji = "🔵"
                
                # Agregar a lista para mover a spam
                if mover_a_spam and correo.get('message_id'):
                    correos_para_spam.append(correo['message_id'])
                    print(f"� Marcado para mover a SPAM")
            
            print(f"�💭 Justificación: {justificacion}")
            print(f"{emoji} {'='*50}")
            print()
        
        # Mover correos no importantes a spam
        if mover_a_spam and correos_para_spam:
            print(f"\n🗑️  Moviendo {len(correos_para_spam)} correos no importantes a SPAM...")
            
            movidos_exitosamente = 0
            for i, message_id in enumerate(correos_para_spam, 1):
                print(f"   Moviendo {i}/{len(correos_para_spam)}...", end=" ")
                if mover_correo_a_spam(self.gmail_service, message_id):
                    print("✅")
                    movidos_exitosamente += 1
                else:
                    print("❌")
            
            print(f"\n✅ {movidos_exitosamente}/{len(correos_para_spam)} correos movidos a SPAM exitosamente")
        
        # Resumen final
        print("\n📊 RESUMEN DE CLASIFICACIÓN:")
        print(f"🔴 Importantes: {importantes}")
        print(f"🔵 No importantes: {no_importantes}")
        if mover_a_spam:
            print(f"🗑️  Movidos a SPAM: {len(correos_para_spam)}")
        print(f"📊 Total clasificados: {importantes + no_importantes}")
        print("=" * 80)

def main():
    clasificador = ClasificadorCorreos()
    
    print("🤖 CLASIFICADOR AUTOMÁTICO DE CORREOS")
    print("=" * 50)
    print("1. Solo clasificar (sin mover a spam)")
    print("2. Clasificar y mover no importantes a spam")
    print("=" * 50)
    
    try:
        opcion = input("Selecciona una opción (1 o 2): ").strip()
        
        if opcion == "1":
            print("\n🔍 Modo: Solo clasificación")
            clasificador.clasificar_correos_nuevos(horas=24, mover_a_spam=False)
        elif opcion == "2":
            print("\n🗑️  Modo: Clasificar y mover a spam")
            confirmacion = input("⚠️  ¿Estás seguro de mover correos no importantes a SPAM? (s/n): ").strip().lower()
            if confirmacion in ['s', 'si', 'yes', 'y']:
                clasificador.clasificar_correos_nuevos(horas=24, mover_a_spam=True)
            else:
                print("❌ Operación cancelada")
        else:
            print("❌ Opción no válida")
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
