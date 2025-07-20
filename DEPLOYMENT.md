# 🚀 Publicar API Clasificador BCP

Guía completa para publicar tu API del Clasificador BCP y hacerla accesible desde cualquier lugar.

## ⚡ Inicio Rápido

```bash
# Opción 1: Script automático
python inicio_rapido.py

# Opción 2: Configurador completo
python publicar_api.py

# Opción 3: Manual
python api_clasificador_bcp.py
```

## 🌐 Opciones de Publicación

### 1. 🏠 Red Local (Gratis)

**Acceso desde otras máquinas en tu WiFi/LAN**

```bash
# Iniciar API
python api_clasificador_bcp.py

# Tu API estará en:
# http://TU_IP_LOCAL:8000
```

**Ventajas:**
- ✅ Completamente gratis
- ✅ Funciona inmediatamente
- ✅ Control total

**Desventajas:**
- ❌ Solo accesible desde tu red local
- ❌ Requiere tu computadora encendida

---

### 2. 🔗 Ngrok (Túnel Público - Recomendado)

**Crea un túnel desde tu máquina al internet**

```bash
# 1. Instalar ngrok
brew install ngrok  # macOS
# apt install ngrok  # Linux

# 2. Registrarse gratis en https://ngrok.com
# 3. Configurar token
ngrok config add-authtoken TU_TOKEN

# 4. En una terminal: iniciar API
python api_clasificador_bcp.py

# 5. En otra terminal: crear túnel
ngrok http 8000

# Tu API estará en: https://xxxxx.ngrok.io
```

**Ventajas:**
- ✅ URL pública instantánea
- ✅ HTTPS automático
- ✅ Gratis para uso básico
- ✅ Fácil configuración

**Desventajas:**
- ❌ URL cambia cada vez que reinicias
- ❌ Requiere tu computadora encendida

---

### 3. 🚂 Railway (Hosting Gratuito)

**Hosting en la nube con 500 horas gratis/mes**

```bash
# 1. Archivos ya creados en el proyecto
# 2. Ve a https://railway.app
# 3. Conecta con GitHub
# 4. Selecciona este repositorio
# 5. ¡Deploy automático!

# Tu API estará en: https://tu-proyecto.railway.app
```

**Archivos incluidos:**
- `railway.json` - Configuración
- `Procfile` - Comando de inicio
- `requirements_cloud.txt` - Dependencias

**Ventajas:**
- ✅ Hosting gratuito 500h/mes
- ✅ Deploy automático desde GitHub
- ✅ URL permanente
- ✅ SSL incluido

**Desventajas:**
- ❌ Límite de horas mensuales
- ❌ Requiere configurar credenciales Google Cloud

---

### 4. 🎨 Render (Hosting Gratuito)

**Hosting gratuito con 750 horas/mes**

```bash
# 1. Ve a https://render.com
# 2. Conecta con GitHub
# 3. Selecciona "Web Service"
# 4. Conecta este repositorio
# 5. Render detecta render.yaml automáticamente

# Tu API estará en: https://tu-proyecto.onrender.com
```

**Ventajas:**
- ✅ 750 horas gratis/mes
- ✅ Deploy automático
- ✅ URL permanente
- ✅ SSL incluido

---

### 5. 🐳 Docker (Para Servidores)

```bash
# Construir imagen
docker build -t clasificador-bcp-api .

# Ejecutar contenedor
docker run -p 8000:8000 clasificador-bcp-api

# Tu API estará en: http://localhost:8000
```

---

## 🔧 Configuración de Credenciales

Para que la API funcione en la nube, necesitas configurar las credenciales de Google Cloud:

### Opción 1: Variables de Entorno
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export VERTEX_AI_PROJECT="gassistant-466419"
export VERTEX_AI_LOCATION="us-central1"
```

### Opción 2: Service Account Key
1. Ve a Google Cloud Console
2. IAM & Admin > Service Accounts
3. Crear/seleccionar service account
4. Crear key JSON
5. Configurar en la plataforma de hosting

### Para Railway:
```
Variables de entorno:
VERTEX_AI_PROJECT = gassistant-466419
VERTEX_AI_LOCATION = us-central1
GOOGLE_APPLICATION_CREDENTIALS = [contenido del JSON]
```

### Para Render:
```
Environment Variables:
VERTEX_AI_PROJECT = gassistant-466419
VERTEX_AI_LOCATION = us-central1
GOOGLE_APPLICATION_CREDENTIALS = [contenido del JSON]
```

---

## 📱 Ejemplos de Uso Público

Una vez publicada, tu API será accesible desde cualquier aplicación:

### JavaScript (Frontend)
```javascript
const API_URL = 'https://tu-api.railway.app';

// Clasificar consumo
const response = await fetch(`${API_URL}/clasificar-manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        empresa: 'RAPPI',
        monto: 'S/ 25.50',
        tipo_tarjeta: 'Crédito'
    })
});

const resultado = await response.json();
console.log(`${resultado.emoji} ${resultado.categoria}`);
```

### Python (Otra aplicación)
```python
import requests

API_URL = 'https://tu-api.railway.app'

# Obtener estadísticas
response = requests.get(f'{API_URL}/estadisticas')
stats = response.json()
print(f"Total gastado: S/ {stats['total_gastado']}")

# Clasificar consumo
response = requests.post(f'{API_URL}/clasificar-manual', json={
    'empresa': 'TAMBO',
    'monto': 'S/ 12.50',
    'tipo_tarjeta': 'Débito'
})
resultado = response.json()
print(f"{resultado['emoji']} {resultado['categoria']}")
```

### curl (Terminal)
```bash
# Obtener categorías
curl https://tu-api.railway.app/categorias

# Clasificar consumo
curl -X POST "https://tu-api.railway.app/clasificar-manual" \
     -H "Content-Type: application/json" \
     -d '{"empresa": "KFC", "monto": "S/ 35.90", "tipo_tarjeta": "Crédito"}'

# Ver estadísticas
curl https://tu-api.railway.app/estadisticas
```

### Aplicación Móvil (React Native)
```javascript
const API_URL = 'https://tu-api.railway.app';

const clasificarGasto = async (gasto) => {
    try {
        const response = await fetch(`${API_URL}/clasificar-manual`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(gasto)
        });
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
    }
};
```

---

## 🔒 Seguridad

### Para Producción:
1. **API Keys**: Agregar autenticación con tokens
2. **CORS**: Limitar origins específicos
3. **Rate Limiting**: Prevenir abuso
4. **HTTPS**: Siempre usar SSL

### Ejemplo con API Key:
```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != "tu-api-key-secreta":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/clasificar-manual", dependencies=[Depends(verify_api_key)])
async def clasificar_manual_protegido(consumo: ConsumoManual):
    # Tu código aquí
```

---

## 📊 Monitoreo

### URLs de Estado:
- `/health` - Estado de la API y Vertex AI
- `/` - Información general
- `/docs` - Documentación interactiva

### Logs en Railway:
```bash
# Ver logs en tiempo real
railway logs
```

### Logs en Render:
```bash
# Ver desde el dashboard web
# O usando CLI: render logs
```

---

## 🆘 Solución de Problemas

### Error: "Vertex AI not available"
- Verificar credenciales de Google Cloud
- Configurar variables de entorno correctamente
- Verificar que el proyecto tiene Vertex AI habilitado

### Error: "Port binding"
- Railway/Render usan variable `$PORT`
- Verificar que el Procfile usa `--port $PORT`

### Error: "Dependencies"
- Verificar `requirements_cloud.txt`
- Python 3.11 compatible
- Sin pandas problemático

---

## 🎯 Recomendación Final

**Para desarrollo/pruebas:** Ngrok
**Para producción pequeña:** Railway
**Para producción media:** Render
**Para producción enterprise:** Google Cloud Run / AWS

---

¡Tu API del Clasificador BCP estará disponible mundialmente en minutos! 🌍
