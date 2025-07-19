const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const express = require('express');
const open = require('open');

class CloudNLAuth {
  constructor() {
    this.credentialsPath = path.join(__dirname, '..', 'credenciales2.json');
    this.tokenPath = path.join(__dirname, '..', 'token-cloudnl.json');
    this.oauth2Client = null;
    this.app = express();
    this.server = null;
  }

  /**
   * Carga las credenciales y configura el cliente OAuth2
   */
  async loadCredentials() {
    try {
      const credentials = JSON.parse(fs.readFileSync(this.credentialsPath, 'utf8'));
      const { client_secret, client_id, redirect_uris } = credentials.web;
      
      this.oauth2Client = new google.auth.OAuth2(
        client_id,
        client_secret,
        redirect_uris[0]
      );

      console.log('✅ Credenciales cargadas exitosamente');
      console.log(`🆔 Project ID: ${credentials.web.project_id}`);
      console.log(`🔑 Client ID: ${client_id}`);
      
      return true;
    } catch (error) {
      console.error('❌ Error al cargar credenciales:', error.message);
      return false;
    }
  }

  /**
   * Inicia el proceso de autenticación con los scopes necesarios para Cloud NL
   */
  async authenticate() {
    console.log('🔐 AUTENTICACIÓN PARA CLOUD NATURAL LANGUAGE API');
    console.log('================================================\n');

    // Cargar credenciales
    const loaded = await this.loadCredentials();
    if (!loaded) {
      console.log('❌ No se pueden cargar las credenciales');
      return false;
    }

    // Scopes requeridos para usar la Natural Language API
    const scopes = [
      'https://www.googleapis.com/auth/cloud-language',
      'https://www.googleapis.com/auth/cloud-platform',
      'https://www.googleapis.com/auth/gmail.readonly' // Mantener Gmail también
    ];

    console.log('🎯 Scopes requeridos:');
    scopes.forEach((scope, index) => {
      console.log(`   ${index + 1}. ${scope}`);
    });
    console.log('');

    // Generar URL de autenticación
    const authUrl = this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: scopes,
      include_granted_scopes: true,
      prompt: 'consent' // Forzar que muestre el consentimiento para obtener refresh token
    });

    console.log('🌐 URL de autenticación generada:');
    console.log(authUrl);
    console.log('');

    // Configurar servidor para recibir el callback
    return this.startCallbackServer(authUrl);
  }

  /**
   * Inicia el servidor para recibir el código de autorización
   */
  async startCallbackServer(authUrl) {
    return new Promise((resolve, reject) => {
      this.app.get('/auth/callback', async (req, res) => {
        const { code } = req.query;

        if (code) {
          try {
            console.log('✅ Código de autorización recibido');
            
            // Intercambiar código por tokens
            const { tokens } = await this.oauth2Client.getToken(code);
            this.oauth2Client.setCredentials(tokens);

            // Guardar tokens
            fs.writeFileSync(this.tokenPath, JSON.stringify(tokens, null, 2));
            console.log(`💾 Tokens guardados en: ${this.tokenPath}`);

            // Verificar que los tokens incluyen los scopes necesarios
            console.log('\n🔍 Verificando scopes obtenidos...');
            if (tokens.scope) {
              const obtainedScopes = tokens.scope.split(' ');
              console.log('✅ Scopes obtenidos:');
              obtainedScopes.forEach(scope => {
                console.log(`   • ${scope}`);
              });

              const hasCloudLanguage = obtainedScopes.some(scope => 
                scope.includes('cloud-language') || scope.includes('cloud-platform')
              );

              if (hasCloudLanguage) {
                console.log('\n🎉 ¡Autenticación exitosa con Cloud Natural Language API!');
              } else {
                console.log('\n⚠️ Advertencia: No se detectaron scopes de Cloud Natural Language');
              }
            }

            res.send(`
              <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                  <h1 style="color: green;">🎉 ¡Autenticación exitosa!</h1>
                  <p>Ya puedes cerrar esta ventana y volver a la terminal.</p>
                  <p>Los tokens han sido guardados para Cloud Natural Language API.</p>
                </body>
              </html>
            `);

            this.server.close();
            resolve(true);

          } catch (error) {
            console.error('❌ Error al obtener tokens:', error.message);
            res.send(`
              <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                  <h1 style="color: red;">❌ Error en la autenticación</h1>
                  <p>${error.message}</p>
                </body>
              </html>
            `);
            this.server.close();
            reject(error);
          }
        } else {
          res.send(`
            <html>
              <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Error</h1>
                <p>No se recibió el código de autorización.</p>
              </body>
            </html>
          `);
          this.server.close();
          reject(new Error('No se recibió código de autorización'));
        }
      });

      this.server = this.app.listen(3000, () => {
        console.log('🚀 Servidor iniciado en http://localhost:3000');
        console.log('🌐 Abriendo navegador para autenticación...\n');
        
        // Abrir navegador automáticamente
        open(authUrl).catch(err => {
          console.log('⚠️ No se pudo abrir el navegador automáticamente');
          console.log('🔗 Por favor, abre manualmente esta URL en tu navegador:');
          console.log(authUrl);
        });
      });
    });
  }

  /**
   * Verifica si ya existe un token válido para Cloud NL
   */
  hasValidToken() {
    try {
      if (fs.existsSync(this.tokenPath)) {
        const tokens = JSON.parse(fs.readFileSync(this.tokenPath, 'utf8'));
        
        // Verificar si el token tiene los scopes necesarios
        if (tokens.scope) {
          const scopes = tokens.scope.split(' ');
          const hasCloudLanguage = scopes.some(scope => 
            scope.includes('cloud-language') || scope.includes('cloud-platform')
          );
          
          if (hasCloudLanguage) {
            console.log('✅ Token válido encontrado para Cloud Natural Language API');
            return true;
          }
        }
      }
      
      console.log('⚠️ No se encontró token válido para Cloud Natural Language API');
      return false;
    } catch (error) {
      console.error('❌ Error al verificar token:', error.message);
      return false;
    }
  }
}

module.exports = CloudNLAuth;
