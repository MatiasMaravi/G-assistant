const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

class CloudNLChecker {
  constructor() {
    this.credentialsPath = path.join(__dirname, '..', 'credenciales2.json');
    this.tokenPath = path.join(__dirname, '..', 'token-cloudnl.json'); // Usar el token específico de Cloud NL
    this.oauth2Client = null;
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

      // Intentar cargar token existente
      if (fs.existsSync(this.tokenPath)) {
        const token = JSON.parse(fs.readFileSync(this.tokenPath, 'utf8'));
        this.oauth2Client.setCredentials(token);
        console.log('✅ Token de Cloud NL cargado exitosamente');
        
        // Verificar scopes si están disponibles
        if (token.scope) {
          const scopes = token.scope.split(' ');
          const hasCloudLanguage = scopes.some(scope => 
            scope.includes('cloud-language') || scope.includes('cloud-platform')
          );
          if (hasCloudLanguage) {
            console.log('✅ Token contiene scopes de Cloud Natural Language');
          } else {
            console.log('⚠️ Token podría no tener scopes de Cloud Natural Language');
          }
        }
      } else {
        console.log('❌ No se encontró el archivo token-cloudnl.json');
        console.log('💡 Ejecuta: node authCloudNL.js para autenticarte con Cloud Natural Language API');
        return false;
      }

      return true;
    } catch (error) {
      console.error('❌ Error al cargar credenciales:', error.message);
      return false;
    }
  }

  /**
   * Verifica si el usuario está autenticado
   */
  isAuthenticated() {
    return this.oauth2Client && this.oauth2Client.credentials && this.oauth2Client.credentials.access_token;
  }

  /**
   * Verifica acceso a Cloud Natural Language API
   */
  async checkCloudNLAccess() {
    console.log('🔍 Verificando acceso a Cloud Natural Language API...\n');

    try {
      // Intentar crear el cliente de Cloud Natural Language
      const language = google.language({ version: 'v1', auth: this.oauth2Client });
      
      console.log('📋 Información del proyecto:');
      
      // Obtener información del proyecto desde las credenciales
      const credentials = JSON.parse(fs.readFileSync(this.credentialsPath, 'utf8'));
      const projectId = credentials.web.project_id;
      console.log(`   🆔 Project ID: ${projectId}`);
      console.log(`   🔑 Client ID: ${credentials.web.client_id}`);
      console.log('');

      // Hacer una prueba simple con análisis de sentimientos
      console.log('🧪 Realizando prueba de análisis de sentimientos...');
      const testText = 'Este es un texto de prueba para verificar el acceso a la API.';
      
      const request = {
        requestBody: {
          document: {
            content: testText,
            type: 'PLAIN_TEXT',
          },
          encodingType: 'UTF8',
        }
      };

      const response = await language.documents.analyzeSentiment(request);
      
      if (response.data) {
        console.log('✅ ¡Acceso exitoso a Cloud Natural Language API!');
        console.log('\n📊 Resultado de la prueba:');
        console.log(`   📝 Texto analizado: "${testText}"`);
        console.log(`   😊 Sentimiento: ${response.data.documentSentiment.score >= 0 ? 'Positivo' : 'Negativo'}`);
        console.log(`   📈 Score: ${response.data.documentSentiment.score}`);
        console.log(`   🎯 Magnitud: ${response.data.documentSentiment.magnitude}`);
        
        return {
          hasAccess: true,
          projectId: projectId,
          testResult: response.data
        };
      }

    } catch (error) {
      console.error('❌ Error al acceder a Cloud Natural Language API:', error.message);
      
      // Analizar diferentes tipos de errores
      if (error.message.includes('403')) {
        console.log('\n🚨 Error 403 - Posibles causas:');
        console.log('   • Cloud Natural Language API no está habilitada en el proyecto');
        console.log('   • Las credenciales no tienen los permisos necesarios');
        console.log('   • El proyecto no tiene facturación habilitada');
        
        console.log('\n🔧 Soluciones:');
        console.log('   1. Ir a Google Cloud Console');
        console.log('   2. Habilitar Cloud Natural Language API');
        console.log('   3. Configurar facturación si es necesario');
        console.log('   4. Verificar permisos IAM');
        
      } else if (error.message.includes('401')) {
        console.log('\n🚨 Error 401 - Problema de autenticación:');
        console.log('   • Token de acceso inválido o expirado');
        console.log('   • Credenciales incorrectas');
        
        console.log('\n🔧 Solución:');
        console.log('   • Ejecuta: npm run auth para renovar la autenticación');
        
      } else if (error.message.includes('quota')) {
        console.log('\n🚨 Error de cuota:');
        console.log('   • Se ha excedido la cuota de uso de la API');
        console.log('   • Revisar límites en Google Cloud Console');
        
      } else {
        console.log('\n❓ Error desconocido. Detalles completos:');
        console.log(error);
      }
      
      return {
        hasAccess: false,
        error: error.message
      };
    }
  }

  /**
   * Verifica qué APIs están disponibles con las credenciales actuales
   */
  async checkAvailableAPIs() {
    console.log('\n🔍 Verificando APIs disponibles...\n');
    
    const apisToCheck = [
      { name: 'Gmail API', service: 'gmail', version: 'v1' },
      { name: 'Cloud Natural Language API', service: 'language', version: 'v1' },
      { name: 'Google Drive API', service: 'drive', version: 'v3' },
      { name: 'Google Sheets API', service: 'sheets', version: 'v4' }
    ];

    const results = [];

    for (const api of apisToCheck) {
      try {
        console.log(`   🧪 Probando ${api.name}...`);
        
        const service = google[api.service]({ 
          version: api.version, 
          auth: this.oauth2Client 
        });

        // Hacer una llamada simple para probar acceso
        if (api.service === 'gmail') {
          await service.users.getProfile({ userId: 'me' });
        } else if (api.service === 'language') {
          await service.documents.analyzeSentiment({
            requestBody: {
              document: { content: 'test', type: 'PLAIN_TEXT' },
              encodingType: 'UTF8'
            }
          });
        } else if (api.service === 'drive') {
          await service.files.list({ pageSize: 1 });
        } else if (api.service === 'sheets') {
          // Solo crear el cliente sin hacer llamada
        }

        console.log(`      ✅ ${api.name} - Acceso disponible`);
        results.push({ ...api, available: true });

      } catch (error) {
        console.log(`      ❌ ${api.name} - Sin acceso (${error.message.substring(0, 50)}...)`);
        results.push({ ...api, available: false, error: error.message });
      }
    }

    return results;
  }

  /**
   * Genera un reporte completo del estado de las APIs
   */
  async generateReport() {
    console.log('📊 REPORTE DE ACCESO A APIS');
    console.log('=============================\n');

    const report = {
      timestamp: new Date().toISOString(),
      credentialsLoaded: false,
      authenticated: false,
      cloudNLAccess: null,
      availableAPIs: []
    };

    try {
      // 1. Verificar credenciales
      console.log('1️⃣ Verificando credenciales...');
      report.credentialsLoaded = await this.loadCredentials();
      
      if (!report.credentialsLoaded) {
        console.log('❌ No se pueden continuar las pruebas sin credenciales válidas');
        return report;
      }

      // 2. Verificar autenticación
      console.log('\n2️⃣ Verificando autenticación...');
      report.authenticated = this.isAuthenticated();
      
      if (!report.authenticated) {
        console.log('❌ Usuario no autenticado. Ejecuta: npm run auth');
        return report;
      }
      console.log('✅ Usuario autenticado correctamente');

      // 3. Verificar Cloud Natural Language API específicamente
      console.log('\n3️⃣ Verificando Cloud Natural Language API...');
      report.cloudNLAccess = await this.checkCloudNLAccess();

      // 4. Verificar otras APIs disponibles
      console.log('\n4️⃣ Verificando otras APIs...');
      report.availableAPIs = await this.checkAvailableAPIs();

      // 5. Resumen final
      console.log('\n📋 RESUMEN FINAL:');
      console.log('==================');
      console.log(`✅ Credenciales: ${report.credentialsLoaded ? 'OK' : 'ERROR'}`);
      console.log(`✅ Autenticación: ${report.authenticated ? 'OK' : 'ERROR'}`);
      console.log(`🧠 Cloud Natural Language: ${report.cloudNLAccess?.hasAccess ? 'DISPONIBLE' : 'NO DISPONIBLE'}`);
      
      console.log('\n🔌 APIs disponibles:');
      report.availableAPIs.forEach(api => {
        console.log(`   ${api.available ? '✅' : '❌'} ${api.name}`);
      });

    } catch (error) {
      console.error('❌ Error durante la generación del reporte:', error.message);
      report.error = error.message;
    }

    return report;
  }
}

module.exports = CloudNLChecker;
