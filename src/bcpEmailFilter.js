const GmailReader = require('./gmailReader');

class BCPEmailFilter {
  constructor() {
    this.gmailReader = new GmailReader();
  }

  /**
   * Inicializa el filtro de correos BCP
   */
  async initialize() {
    console.log('🔑 Cargando credenciales...');
    const loaded = await this.gmailReader.loadCredentials();
    
    if (!loaded) {
      throw new Error('No se pudieron cargar las credenciales. Ejecuta: npm run auth');
    }

    if (!this.gmailReader.isAuthenticated()) {
      throw new Error('No estás autenticado. Ejecuta: npm run auth');
    }

    console.log('✅ Autenticación exitosa');
  }

  /**
   * Filtra correos específicos de BCP con asunto "Realizaste un consumo"
   * @param {Object} options - Opciones de filtrado
   * @param {number} options.maxResults - Número máximo de resultados (default: 50)
   * @param {string} options.afterDate - Fecha después de (formato: YYYY/MM/DD)
   * @param {string} options.beforeDate - Fecha antes de (formato: YYYY/MM/DD)
   */
  async getBCPConsumptionEmails(options = {}) {
    const {
      maxResults = 50,
      afterDate = null,
      beforeDate = null
    } = options;

    console.log('🏦 Buscando correos de BCP sobre consumos...');
    
    try {
      // Construir la query específica para BCP
      let query = 'from:"BCP Notificaciones" subject:"Realizaste un consumo"';
      
      if (afterDate) {
        query += ` after:${afterDate}`;
      }
      
      if (beforeDate) {
        query += ` before:${beforeDate}`;
      }

      console.log(`🔍 Query de búsqueda: ${query}`);

      // Buscar los mensajes usando la API de Gmail
      const messages = await this.gmailReader.listEmails({
        query: query,
        maxResults: maxResults
      });

      if (messages.length === 0) {
        console.log('📭 No se encontraron correos de BCP con esas características');
        return [];
      }

      console.log(`📬 Encontrados ${messages.length} correos de BCP`);
      console.log('📄 Obteniendo detalles de los correos...');

      // Obtener detalles completos de cada correo
      const bcpEmails = [];
      for (let i = 0; i < messages.length; i++) {
        try {
          console.log(`   Procesando correo ${i + 1}/${messages.length}...`);
          const email = await this.gmailReader.getEmail(messages[i].id);
          bcpEmails.push(email);
          
          // Pequeña pausa para no sobrecargar la API
          if (i < messages.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        } catch (error) {
          console.error(`❌ Error al obtener correo ${messages[i].id}:`, error.message);
        }
      }

      return bcpEmails;

    } catch (error) {
      console.error('❌ Error al buscar correos de BCP:', error.message);
      throw error;
    }
  }

  /**
   * Analiza los correos de BCP y extrae información útil
   * @param {Array} emails - Array de emails de BCP
   */
  analyzeBCPEmails(emails) {
    console.log('\n📊 ANÁLISIS DE CORREOS BCP - CONSUMOS');
    console.log('=====================================\n');

    if (emails.length === 0) {
      console.log('📭 No hay correos para analizar');
      return;
    }

    // Estadísticas generales
    console.log(`📈 Total de correos encontrados: ${emails.length}`);
    console.log(`📅 Período: Del ${this.getOldestDate(emails)} al ${this.getNewestDate(emails)}\n`);

    // Mostrar cada correo
    emails.forEach((email, index) => {
      console.log(`${index + 1}. 💳 CONSUMO BCP`);
      console.log(`   📅 Fecha: ${email.date}`);
      console.log(`   📧 ID: ${email.id}`);
      console.log(`   👁️ Leído: ${email.isRead ? 'Sí' : 'No'}`);
      console.log(`   📄 Resumen: ${email.snippet}`);
      
      // Intentar extraer información del cuerpo del correo
      const consumptionInfo = this.extractConsumptionInfo(email);
      if (consumptionInfo) {
        console.log(`   💰 Información del consumo:`);
        Object.entries(consumptionInfo).forEach(([key, value]) => {
          console.log(`      ${key}: ${value}`);
        });
      }
      console.log('');
    });

    return {
      totalEmails: emails.length,
      oldestDate: this.getOldestDate(emails),
      newestDate: this.getNewestDate(emails),
      unreadCount: emails.filter(email => !email.isRead).length,
      emails: emails
    };
  }

  /**
   * Extrae información específica del consumo del cuerpo del correo
   * @param {Object} email - Objeto email
   */
  extractConsumptionInfo(email) {
    const body = email.body || email.snippet || '';
    const info = {};

    // Patrones comunes para extraer información (estos pueden necesitar ajustes según el formato real)
    const patterns = {
      monto: /(?:monto|importe|total).*?S\/\s*(\d+\.?\d*)/i,
      tarjeta: /(?:tarjeta|card).*?(\*\*\*\*\s*\d+)/i,
      comercio: /(?:comercio|establecimiento|tienda).*?([A-Z][A-Za-z\s]+)/i,
      fecha: /(\d{1,2}\/\d{1,2}\/\d{4})/,
      hora: /(\d{1,2}:\d{2})/
    };

    Object.entries(patterns).forEach(([key, pattern]) => {
      const match = body.match(pattern);
      if (match) {
        info[key] = match[1].trim();
      }
    });

    return Object.keys(info).length > 0 ? info : null;
  }

  /**
   * Obtiene la fecha más antigua de los emails
   */
  getOldestDate(emails) {
    if (emails.length === 0) return 'N/A';
    return emails
      .map(email => new Date(email.date))
      .reduce((oldest, date) => date < oldest ? date : oldest)
      .toLocaleDateString('es-ES');
  }

  /**
   * Obtiene la fecha más nueva de los emails
   */
  getNewestDate(emails) {
    if (emails.length === 0) return 'N/A';
    return emails
      .map(email => new Date(email.date))
      .reduce((newest, date) => date > newest ? date : newest)
      .toLocaleDateString('es-ES');
  }

  /**
   * Exporta los correos a un archivo JSON
   * @param {Array} emails - Array de emails
   * @param {string} filename - Nombre del archivo (opcional)
   */
  async exportToJSON(emails, filename = null) {
    const fs = require('fs');
    const path = require('path');
    
    if (!filename) {
      const now = new Date();
      const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, -5);
      filename = `bcp-consumos-${timestamp}.json`;
    }

    const exportData = {
      exportDate: new Date().toISOString(),
      totalEmails: emails.length,
      query: 'from:"BCP Notificaciones" subject:"Realizaste un consumo"',
      emails: emails.map(email => ({
        id: email.id,
        date: email.date,
        subject: email.subject,
        from: email.from,
        snippet: email.snippet,
        isRead: email.isRead,
        body: email.body
      }))
    };

    const exportPath = path.join(__dirname, '..', 'exports', filename);
    
    // Crear directorio exports si no existe
    const exportsDir = path.dirname(exportPath);
    if (!fs.existsSync(exportsDir)) {
      fs.mkdirSync(exportsDir, { recursive: true });
    }

    fs.writeFileSync(exportPath, JSON.stringify(exportData, null, 2));
    console.log(`💾 Correos exportados a: ${exportPath}`);
    
    return exportPath;
  }
}

module.exports = BCPEmailFilter;
