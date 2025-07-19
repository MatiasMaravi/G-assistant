const { google } = require('googleapis');
const express = require('express');
const fs = require('fs');
const path = require('path');
const open = require('open');

// Configuración
const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const CREDENTIALS_PATH = path.join(__dirname, '..', 'credenciales.json');
const TOKEN_PATH = path.join(__dirname, '..', 'token.json');
const PORT = 3000;

class AuthManager {
  constructor() {
    this.oauth2Client = null;
    this.server = null;
  }

  /**
   * Inicia el proceso de autenticación
   */
  async authenticate() {
    try {
      // Cargar credenciales
      const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
      const { client_secret, client_id, redirect_uris } = credentials.web;

      // Crear cliente OAuth2
      this.oauth2Client = new google.auth.OAuth2(
        client_id,
        client_secret,
        redirect_uris[0]
      );

      // Verificar si ya existe un token válido
      if (fs.existsSync(TOKEN_PATH)) {
        const token = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8'));
        this.oauth2Client.setCredentials(token);
        
        // Verificar si el token es válido
        try {
          await this.oauth2Client.getAccessToken();
          console.log('✅ Token existente válido. Autenticación completada.');
          return true;
        } catch (error) {
          console.log('⚠️  Token existente inválido. Iniciando nueva autenticación...');
          fs.unlinkSync(TOKEN_PATH);
        }
      }

      // Iniciar servidor para callback
      await this.startCallbackServer();

      // Generar URL de autorización
      const authUrl = this.oauth2Client.generateAuthUrl({
        access_type: 'offline',
        scope: SCOPES,
      });

      console.log('🔐 Iniciando proceso de autenticación...');
      console.log('📱 Se abrirá tu navegador automáticamente');
      console.log('🔗 Si no se abre, visita esta URL:', authUrl);
      
      // Abrir navegador
      await open(authUrl);

      return new Promise((resolve) => {
        this.resolveAuth = resolve;
      });

    } catch (error) {
      console.error('❌ Error durante la autenticación:', error.message);
      return false;
    }
  }

  /**
   * Inicia el servidor para manejar el callback de OAuth
   */
  async startCallbackServer() {
    const app = express();

    app.get('/auth/callback', async (req, res) => {
      const { code, error } = req.query;

      if (error) {
        res.send(`
          <h2>❌ Error en la autenticación</h2>
          <p>Error: ${error}</p>
          <p>Puedes cerrar esta ventana.</p>
        `);
        this.resolveAuth(false);
        return;
      }

      try {
        // Intercambiar código por token
        const { tokens } = await this.oauth2Client.getToken(code);
        this.oauth2Client.setCredentials(tokens);

        // Guardar token
        fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens, null, 2));
        
        res.send(`
          <h2>✅ Autenticación exitosa!</h2>
          <p>Ya puedes cerrar esta ventana y regresar a la aplicación.</p>
          <script>setTimeout(() => window.close(), 3000);</script>
        `);

        console.log('✅ Autenticación completada exitosamente!');
        console.log('📁 Token guardado en:', TOKEN_PATH);
        
        this.resolveAuth(true);
      } catch (error) {
        console.error('❌ Error al intercambiar código:', error.message);
        res.send(`
          <h2>❌ Error al completar autenticación</h2>
          <p>Error: ${error.message}</p>
          <p>Puedes cerrar esta ventana.</p>
        `);
        this.resolveAuth(false);
      } finally {
        // Cerrar servidor después de un momento
        setTimeout(() => {
          this.server?.close();
        }, 5000);
      }
    });

    return new Promise((resolve) => {
      this.server = app.listen(PORT, () => {
        console.log(`🌐 Servidor de callback iniciado en http://localhost:${PORT}`);
        resolve();
      });
    });
  }

  /**
   * Revoca el token actual
   */
  async revokeToken() {
    try {
      if (fs.existsSync(TOKEN_PATH)) {
        const token = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8'));
        
        if (token.refresh_token) {
          await this.oauth2Client.revokeToken(token.refresh_token);
        }
        
        fs.unlinkSync(TOKEN_PATH);
        console.log('✅ Token revocado y eliminado exitosamente');
        return true;
      } else {
        console.log('⚠️  No hay token para revocar');
        return true;
      }
    } catch (error) {
      console.error('❌ Error al revocar token:', error.message);
      return false;
    }
  }
}

// Ejecutar si se llama directamente
if (require.main === module) {
  const authManager = new AuthManager();
  
  const args = process.argv.slice(2);
  
  if (args.includes('--revoke')) {
    authManager.revokeToken().then(() => {
      process.exit(0);
    });
  } else {
    authManager.authenticate().then((success) => {
      if (success) {
        console.log('\n🎉 ¡Autenticación completada!');
        console.log('💡 Ahora puedes usar: npm start');
      } else {
        console.log('\n❌ Falló la autenticación');
        process.exit(1);
      }
      process.exit(0);
    });
  }
}

module.exports = AuthManager;
