const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

class GmailReader {
  constructor() {
    this.credentialsPath = path.join(__dirname, '..', 'credenciales.json');
    this.tokenPath = path.join(__dirname, '..', 'token.json');
    this.oauth2Client = null;
    this.gmail = null;
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
        console.log('Token cargado exitosamente');
      }

      this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
      return true;
    } catch (error) {
      console.error('Error al cargar credenciales:', error.message);
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
   * Obtiene la información del perfil del usuario
   */
  async getProfile() {
    try {
      const response = await this.gmail.users.getProfile({
        userId: 'me'
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener el perfil:', error.message);
      throw error;
    }
  }

  /**
   * Lista los correos con filtros opcionales
   * @param {Object} options - Opciones de filtrado
   * @param {string} options.query - Query de búsqueda (ej: 'is:unread', 'from:ejemplo@gmail.com')
   * @param {number} options.maxResults - Número máximo de resultados (default: 10)
   * @param {boolean} options.includeSpamTrash - Incluir spam y papelera (default: false)
   */
  async listEmails(options = {}) {
    const {
      query = '',
      maxResults = 10,
      includeSpamTrash = false
    } = options;

    try {
      const response = await this.gmail.users.messages.list({
        userId: 'me',
        q: query,
        maxResults: maxResults,
        includeSpamTrash: includeSpamTrash
      });

      return response.data.messages || [];
    } catch (error) {
      console.error('Error al listar correos:', error.message);
      throw error;
    }
  }

  /**
   * Obtiene los detalles completos de un correo
   * @param {string} messageId - ID del mensaje
   */
  async getEmail(messageId) {
    try {
      const response = await this.gmail.users.messages.get({
        userId: 'me',
        id: messageId,
        format: 'full'
      });

      const message = response.data;
      const headers = message.payload.headers;

      // Extraer información útil de los headers
      const subject = headers.find(h => h.name === 'Subject')?.value || 'Sin asunto';
      const from = headers.find(h => h.name === 'From')?.value || 'Desconocido';
      const to = headers.find(h => h.name === 'To')?.value || 'Desconocido';
      const date = headers.find(h => h.name === 'Date')?.value || '';

      // Extraer el cuerpo del mensaje
      const body = this.extractBody(message.payload);

      return {
        id: messageId,
        threadId: message.threadId,
        subject,
        from,
        to,
        date,
        snippet: message.snippet,
        body,
        labels: message.labelIds || [],
        isRead: !message.labelIds?.includes('UNREAD')
      };
    } catch (error) {
      console.error('Error al obtener correo:', error.message);
      throw error;
    }
  }

  /**
   * Extrae el cuerpo del mensaje desde el payload
   * @param {Object} payload - Payload del mensaje
   */
  extractBody(payload) {
    let body = '';

    if (payload.parts) {
      // Mensaje multiparte
      for (const part of payload.parts) {
        if (part.mimeType === 'text/plain' && part.body.data) {
          body += Buffer.from(part.body.data, 'base64').toString('utf8');
        } else if (part.mimeType === 'text/html' && part.body.data && !body) {
          // Solo usar HTML si no hay texto plano
          body += Buffer.from(part.body.data, 'base64').toString('utf8');
        } else if (part.parts) {
          // Recursivo para partes anidadas
          body += this.extractBody(part);
        }
      }
    } else if (payload.body && payload.body.data) {
      // Mensaje simple
      body = Buffer.from(payload.body.data, 'base64').toString('utf8');
    }

    return body;
  }

  /**
   * Busca correos por criterios específicos
   * @param {Object} searchCriteria - Criterios de búsqueda
   */
  async searchEmails(searchCriteria) {
    const {
      from,
      to,
      subject,
      isUnread = false,
      hasAttachment = false,
      afterDate,
      beforeDate,
      maxResults = 10
    } = searchCriteria;

    let query = '';
    
    if (from) query += `from:${from} `;
    if (to) query += `to:${to} `;
    if (subject) query += `subject:${subject} `;
    if (isUnread) query += 'is:unread ';
    if (hasAttachment) query += 'has:attachment ';
    if (afterDate) query += `after:${afterDate} `;
    if (beforeDate) query += `before:${beforeDate} `;

    console.log(`Buscando con query: ${query.trim()}`);
    
    const messages = await this.listEmails({
      query: query.trim(),
      maxResults
    });

    // Obtener detalles de cada mensaje
    const emails = [];
    for (const message of messages) {
      try {
        const email = await this.getEmail(message.id);
        emails.push(email);
      } catch (error) {
        console.error(`Error al obtener email ${message.id}:`, error.message);
      }
    }

    return emails;
  }

  /**
   * Obtiene los correos no leídos
   * @param {number} maxResults - Número máximo de resultados
   */
  async getUnreadEmails(maxResults = 10) {
    return this.searchEmails({
      isUnread: true,
      maxResults
    });
  }
}

module.exports = GmailReader;
