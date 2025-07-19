#!/usr/bin/env python3
"""
Script para probar la conexión con Gmail y verificar permisos
"""

from gmail import get_gmail_service

def test_gmail_permissions():
    """Prueba la conexión con Gmail y verifica permisos"""
    print("🔄 Probando conexión con Gmail...")
    
    try:
        # Obtener servicio de Gmail
        service = get_gmail_service()
        print("✅ Conexión establecida exitosamente")
        
        # Probar permisos básicos
        print("🔄 Verificando permisos...")
        
        # Obtener perfil del usuario
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Usuario: {profile.get('emailAddress')}")
        print(f"✅ Total de mensajes: {profile.get('messagesTotal')}")
        
        # Obtener lista de labels para verificar permisos de lectura
        labels = service.users().labels().list(userId='me').execute()
        print(f"✅ Labels disponibles: {len(labels.get('labels', []))}")
        
        # Buscar un mensaje reciente para probar
        messages = service.users().messages().list(userId='me', maxResults=1).execute()
        if messages.get('messages'):
            msg_id = messages['messages'][0]['id']
            print(f"✅ Mensaje de prueba encontrado: {msg_id}")
            
            # Intentar obtener detalles del mensaje
            msg = service.users().messages().get(userId='me', id=msg_id).execute()
            print(f"✅ Detalles del mensaje obtenidos correctamente")
            
            print("\n🎉 TODAS LAS PRUEBAS PASARON")
            print("Los permisos de Gmail están correctamente configurados")
            return True
        else:
            print("⚠️  No se encontraron mensajes para probar")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if "insufficient" in str(e).lower() or "permission" in str(e).lower():
            print("\n💡 SOLUCIÓN:")
            print("1. Ejecuta: rm -f token.json")
            print("2. Vuelve a ejecutar este script")
            print("3. Autoriza los nuevos permisos en el navegador")
        return False

if __name__ == "__main__":
    test_gmail_permissions()
