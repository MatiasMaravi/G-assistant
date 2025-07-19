const GmailReader = require('./gmailReader');

async function main() {
  const gmailReader = new GmailReader();

  try {
    console.log('📧 Iniciando Gmail Assistant...\n');

    // Cargar credenciales
    console.log('🔑 Cargando credenciales...');
    const loaded = await gmailReader.loadCredentials();
    if (!loaded) {
      console.log('❌ No se pudieron cargar las credenciales');
      console.log('💡 Ejecuta: npm run auth');
      return;
    }

    // Verificar autenticación
    if (!gmailReader.isAuthenticated()) {
      console.log('🔐 No estás autenticado');
      console.log('💡 Ejecuta: npm run auth');
      return;
    }

    // Obtener perfil del usuario
    console.log('👤 Obteniendo información del perfil...');
    const profile = await gmailReader.getProfile();
    console.log(`📧 Email: ${profile.emailAddress}`);
    console.log(`📊 Total de mensajes: ${profile.messagesTotal}`);
    console.log(`📊 Total de hilos: ${profile.threadsTotal}\n`);

    // Ejemplo 1: Obtener correos no leídos
    console.log('📬 Obteniendo correos no leídos...');
    const unreadEmails = await gmailReader.getUnreadEmails(5);
    
    if (unreadEmails.length === 0) {
      console.log('✨ No tienes correos no leídos\n');
    } else {
      console.log(`📮 Tienes ${unreadEmails.length} correos no leídos:\n`);
      
      unreadEmails.forEach((email, index) => {
        console.log(`${index + 1}. 📧 De: ${email.from}`);
        console.log(`   📝 Asunto: ${email.subject}`);
        console.log(`   📅 Fecha: ${email.date}`);
        console.log(`   📄 Resumen: ${email.snippet}\n`);
      });
    }

    // Ejemplo 2: Buscar correos específicos
    console.log('🔍 Buscando correos recientes...');
    const recentEmails = await gmailReader.listEmails({
      maxResults: 3
    });

    if (recentEmails.length > 0) {
      console.log(`📨 Últimos ${recentEmails.length} correos:\n`);
      
      for (const messageInfo of recentEmails) {
        const email = await gmailReader.getEmail(messageInfo.id);
        console.log(`📧 De: ${email.from}`);
        console.log(`📝 Asunto: ${email.subject}`);
        console.log(`📅 Fecha: ${email.date}`);
        console.log(`👁️ Leído: ${email.isRead ? 'Sí' : 'No'}`);
        console.log(`📄 Resumen: ${email.snippet}\n`);
      }
    }

    // Ejemplo 3: Mostrar menú interactivo
    await showInteractiveMenu(gmailReader);

  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.message.includes('invalid_grant')) {
      console.log('🔄 El token ha expirado. Ejecuta: npm run auth');
    }
  }
}

async function showInteractiveMenu(gmailReader) {
  const readline = require('readline');
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const question = (prompt) => {
    return new Promise((resolve) => {
      rl.question(prompt, resolve);
    });
  };

  while (true) {
    console.log('\n📋 ¿Qué deseas hacer?');
    console.log('1. Ver correos no leídos');
    console.log('2. Buscar correos por remitente');
    console.log('3. Buscar correos por asunto');
    console.log('4. Ver correos recientes');
    console.log('5. Salir\n');

    const choice = await question('Selecciona una opción (1-5): ');

    try {
      switch (choice) {
        case '1':
          const maxResults = await question('¿Cuántos correos mostrar? (default: 5): ');
          const unread = await gmailReader.getUnreadEmails(parseInt(maxResults) || 5);
          displayEmails(unread, 'Correos no leídos');
          break;

        case '2':
          const sender = await question('Ingresa el remitente a buscar: ');
          const fromEmails = await gmailReader.searchEmails({ from: sender, maxResults: 5 });
          displayEmails(fromEmails, `Correos de ${sender}`);
          break;

        case '3':
          const subject = await question('Ingresa palabras del asunto: ');
          const subjectEmails = await gmailReader.searchEmails({ subject: subject, maxResults: 5 });
          displayEmails(subjectEmails, `Correos con asunto: ${subject}`);
          break;

        case '4':
          const recent = await question('¿Cuántos correos recientes mostrar? (default: 5): ');
          const messages = await gmailReader.listEmails({ maxResults: parseInt(recent) || 5 });
          const recentEmails = [];
          for (const msg of messages) {
            const email = await gmailReader.getEmail(msg.id);
            recentEmails.push(email);
          }
          displayEmails(recentEmails, 'Correos recientes');
          break;

        case '5':
          console.log('👋 ¡Hasta luego!');
          rl.close();
          return;

        default:
          console.log('❌ Opción inválida');
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
    }
  }
}

function displayEmails(emails, title) {
  console.log(`\n📨 ${title}:`);
  
  if (emails.length === 0) {
    console.log('📭 No se encontraron correos\n');
    return;
  }

  emails.forEach((email, index) => {
    console.log(`\n${index + 1}. 📧 De: ${email.from}`);
    console.log(`   📝 Asunto: ${email.subject}`);
    console.log(`   📅 Fecha: ${email.date}`);
    console.log(`   👁️ Leído: ${email.isRead ? 'Sí' : 'No'}`);
    console.log(`   📄 Resumen: ${email.snippet}`);
  });
  console.log('');
}

// Ejecutar la aplicación
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main };
