// Ejemplo básico de uso del Gmail Assistant
const GmailReader = require('./src/gmailReader');

async function ejemploUso() {
  const gmailReader = new GmailReader();

  try {
    console.log('📧 Ejemplo de uso del Gmail Assistant\n');

    // 1. Cargar credenciales
    const loaded = await gmailReader.loadCredentials();
    if (!loaded) {
      console.log('❌ Error: No se pudieron cargar las credenciales');
      console.log('💡 Asegúrate de que el archivo credenciales.json esté configurado correctamente');
      return;
    }

    // 2. Verificar autenticación
    if (!gmailReader.isAuthenticated()) {
      console.log('🔐 No estás autenticado');
      console.log('💡 Ejecuta: npm run auth');
      return;
    }

    console.log('✅ Conectado exitosamente a Gmail\n');

    // 3. Obtener información del perfil
    const profile = await gmailReader.getProfile();
    console.log('👤 Información del perfil:');
    console.log(`   📧 Email: ${profile.emailAddress}`);
    console.log(`   📊 Total mensajes: ${profile.messagesTotal}`);
    console.log(`   📊 Total hilos: ${profile.threadsTotal}\n`);

    // 4. Obtener correos no leídos (máximo 3)
    console.log('📬 Correos no leídos:');
    const unreadEmails = await gmailReader.getUnreadEmails(3);
    
    if (unreadEmails.length === 0) {
      console.log('   ✨ No tienes correos no leídos\n');
    } else {
      unreadEmails.forEach((email, index) => {
        console.log(`   ${index + 1}. 📧 ${email.from}`);
        console.log(`      📝 ${email.subject}`);
        console.log(`      📅 ${email.date}`);
        console.log(`      📄 ${email.snippet.substring(0, 100)}...\n`);
      });
    }

    // 5. Buscar correos específicos (ejemplo: de Gmail Team)
    console.log('🔍 Buscando correos de "gmail" (últimos 3):');
    const searchResults = await gmailReader.searchEmails({
      from: 'gmail',
      maxResults: 3
    });

    if (searchResults.length === 0) {
      console.log('   📭 No se encontraron correos\n');
    } else {
      searchResults.forEach((email, index) => {
        console.log(`   ${index + 1}. 📧 ${email.from}`);
        console.log(`      📝 ${email.subject}`);
        console.log(`      📅 ${email.date}\n`);
      });
    }

    // 6. Obtener correos recientes
    console.log('📨 Últimos 5 correos recibidos:');
    const recentMessages = await gmailReader.listEmails({ maxResults: 5 });
    
    for (let i = 0; i < Math.min(3, recentMessages.length); i++) {
      const email = await gmailReader.getEmail(recentMessages[i].id);
      console.log(`   ${i + 1}. 📧 ${email.from}`);
      console.log(`      📝 ${email.subject}`);
      console.log(`      👁️ ${email.isRead ? 'Leído' : 'No leído'}`);
      console.log(`      📅 ${email.date}\n`);
    }

    console.log('✅ Ejemplo completado exitosamente!');

  } catch (error) {
    console.error('❌ Error en el ejemplo:', error.message);
    
    if (error.message.includes('invalid_grant')) {
      console.log('🔄 El token ha expirado. Ejecuta: npm run auth');
    } else if (error.message.includes('invalid_client')) {
      console.log('🔧 Verifica que tu archivo credenciales.json sea correcto');
    }
  }
}

// Ejecutar el ejemplo
if (require.main === module) {
  ejemploUso().catch(console.error);
}

module.exports = { ejemploUso };
