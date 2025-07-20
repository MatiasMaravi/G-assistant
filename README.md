# Gmail Assistant

Un asistente para leer y gestionar correos electrónicos de Gmail usando la API de Google.

## 🚀 Características

- ✅ Autenticación OAuth2 con Gmail
- 📧 Lectura de correos no leídos
- 🔍 Búsqueda de correos por remitente, asunto y fecha
- 📊 Información del perfil de Gmail
- 🖥️ Interfaz de línea de comandos interactiva
- 🔐 Gestión segura de tokens de acceso

## 📋 Requisitos Previos

1. **Node.js**: Versión 14 o superior
2. **Cuenta de Gmail**: Con acceso a la API de Gmail
3. **Credenciales OAuth2**: Archivo `credenciales.json` con las credenciales de tu aplicación de Google

## 🛠️ Instalación

1. Clona o descarga este proyecto
2. Instala las dependencias:
```bash
npm install
```

## ⚙️ Configuración

### 1. Obtener Credenciales de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Gmail:
   - Ve a "APIs & Services" > "Library"
   - Busca "Gmail API" y habilítala
4. Crear credenciales OAuth2:
   - Ve a "APIs & Services" > "Credentials"
   - Clic en "Create Credentials" > "OAuth client ID"
   - Selecciona "Web application"
   - Agrega `http://localhost:3000/auth/callback` en "Authorized redirect URIs"
   - Descarga el archivo JSON de credenciales

### 2. Configurar Credenciales

Asegúrate de que tu archivo `credenciales.json` esté en la raíz del proyecto con el formato correcto.

## 🚦 Uso

### 1. Autenticación Inicial

Antes de usar la aplicación por primera vez, debes autenticarte:

```bash
npm run auth
```

Este comando:
- Abrirá tu navegador automáticamente
- Te pedirá que autorices la aplicación
- Guardará el token de acceso para uso futuro

### 2. Ejecutar la Aplicación

```bash
npm start
```

### 3. Menú Interactivo

La aplicación ofrece un menú interactivo con las siguientes opciones:

1. **Ver correos no leídos**: Muestra los correos que no has leído
2. **Buscar correos por remitente**: Busca correos de un remitente específico
3. **Buscar correos por asunto**: Busca correos que contengan palabras específicas en el asunto
4. **Ver correos recientes**: Muestra los correos más recientes
5. **Salir**: Cierra la aplicación

## 📁 Estructura del Proyecto

```
G-assistant/
├── src/
│   ├── auth.js          # Manejo de autenticación OAuth2
│   ├── gmailReader.js   # Clase principal para leer correos
│   └── index.js         # Aplicación principal con menú interactivo
├── credenciales.json    # Credenciales de Google OAuth2
├── token.json          # Token de acceso (generado automáticamente)
├── package.json        # Configuración del proyecto
└── README.md          # Este archivo
```

## 🔧 API Disponible

### GmailReader

La clase principal `GmailReader` ofrece los siguientes métodos:

#### `loadCredentials()`
Carga las credenciales desde `credenciales.json`

#### `isAuthenticated()`
Verifica si el usuario está autenticado

#### `getProfile()`
Obtiene información del perfil de Gmail

#### `listEmails(options)`
Lista correos con opciones de filtrado:
- `query`: Query de búsqueda de Gmail
- `maxResults`: Número máximo de resultados
- `includeSpamTrash`: Incluir spam y papelera

#### `getEmail(messageId)`
Obtiene detalles completos de un correo específico

#### `searchEmails(criteria)`
Busca correos por criterios específicos:
- `from`: Remitente
- `to`: Destinatario  
- `subject`: Asunto
- `isUnread`: Solo no leídos
- `hasAttachment`: Con archivos adjuntos
- `afterDate`: Después de fecha
- `beforeDate`: Antes de fecha

#### `getUnreadEmails(maxResults)`
Obtiene correos no leídos

## 🔒 Seguridad

- Las credenciales se almacenan localmente en `credenciales.json`
- Los tokens de acceso se guardan en `token.json`
- La aplicación usa OAuth2 para autenticación segura
- Los tokens se actualizan automáticamente cuando es necesario

## 🚨 Solución de Problemas

### Error de autenticación
Si obtienes errores de autenticación:
```bash
npm run auth
```

### Token expirado
Si el token ha expirado, vuelve a autenticarte:
```bash
npm run auth
```

### Revocar acceso
Para revocar el acceso actual:
```bash
node src/auth.js --revoke
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia ISC. Ver archivo `LICENSE` para más detalles.

## ⚠️ Limitaciones

- La API de Gmail tiene límites de cuota
- Solo lectura de correos (no modificación)
- Requiere conexión a internet para funcionar

## 🆘 Soporte

Si encuentras algún problema:

1. Verifica que tu archivo `credenciales.json` esté correctamente configurado
2. Asegúrate de tener permisos para acceder a la API de Gmail
3. Revisa que Node.js esté correctamente instalado
4. Verifica tu conexión a internet

---

¡Disfruta usando tu Gmail Assistant! 📧✨