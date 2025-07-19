const BCPEmailFilter = require('./src/bcpEmailFilter');
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

async function main() {
  console.log('🏦 FILTRO DE CORREOS BCP - CONSUMOS');
  console.log('===================================\n');

  const bcpFilter = new BCPEmailFilter();

  try {
    // Inicializar el filtro
    await bcpFilter.initialize();

    // Menú interactivo
    while (true) {
      console.log('\n📋 ¿Qué deseas hacer?');
      console.log('1. Buscar todos los correos de consumo BCP');
      console.log('2. Buscar correos de un período específico');
      console.log('3. Buscar correos de los últimos 30 días');
      console.log('4. Buscar correos de los últimos 7 días');
      console.log('5. Salir');

      const option = await question('\n🔢 Selecciona una opción (1-5): ');

      switch (option.trim()) {
        case '1':
          await searchAllBCPEmails(bcpFilter);
          break;
        case '2':
          await searchBCPEmailsByDateRange(bcpFilter);
          break;
        case '3':
          await searchBCPEmailsLastDays(bcpFilter, 30);
          break;
        case '4':
          await searchBCPEmailsLastDays(bcpFilter, 7);
          break;
        case '5':
          console.log('👋 ¡Hasta luego!');
          rl.close();
          return;
        default:
          console.log('❌ Opción inválida. Por favor, selecciona 1-5.');
      }
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
    rl.close();
  }
}

async function searchAllBCPEmails(bcpFilter) {
  try {
    const maxResults = await question('📊 ¿Cuántos correos máximo quieres buscar? (default: 50): ');
    const max = parseInt(maxResults.trim()) || 50;

    const emails = await bcpFilter.getBCPConsumptionEmails({ maxResults: max });
    const analysis = bcpFilter.analyzeBCPEmails(emails);
    
    if (emails.length > 0) {
      const exportChoice = await question('\n💾 ¿Quieres exportar los resultados a JSON? (s/n): ');
      if (exportChoice.toLowerCase() === 's' || exportChoice.toLowerCase() === 'sí') {
        await bcpFilter.exportToJSON(emails);
      }
    }
  } catch (error) {
    console.error('❌ Error al buscar correos:', error.message);
  }
}

async function searchBCPEmailsByDateRange(bcpFilter) {
  try {
    console.log('\n📅 Ingresa el rango de fechas (formato: YYYY/MM/DD)');
    const afterDate = await question('🗓️ Fecha desde (opcional, presiona Enter para omitir): ');
    const beforeDate = await question('🗓️ Fecha hasta (opcional, presiona Enter para omitir): ');
    const maxResults = await question('📊 Máximo de correos (default: 50): ');

    const options = {
      maxResults: parseInt(maxResults.trim()) || 50
    };

    if (afterDate.trim()) {
      options.afterDate = afterDate.trim();
    }

    if (beforeDate.trim()) {
      options.beforeDate = beforeDate.trim();
    }

    const emails = await bcpFilter.getBCPConsumptionEmails(options);
    const analysis = bcpFilter.analyzeBCPEmails(emails);
    
    if (emails.length > 0) {
      const exportChoice = await question('\n💾 ¿Quieres exportar los resultados a JSON? (s/n): ');
      if (exportChoice.toLowerCase() === 's' || exportChoice.toLowerCase() === 'sí') {
        await bcpFilter.exportToJSON(emails);
      }
    }
  } catch (error) {
    console.error('❌ Error al buscar correos por fecha:', error.message);
  }
}

async function searchBCPEmailsLastDays(bcpFilter, days) {
  try {
    console.log(`\n📅 Buscando correos de los últimos ${days} días...`);

    const now = new Date();
    const pastDate = new Date(now.getTime() - (days * 24 * 60 * 60 * 1000));
    
    const afterDate = pastDate.toISOString().slice(0, 10).replace(/-/g, '/');
    
    const emails = await bcpFilter.getBCPConsumptionEmails({
      afterDate: afterDate,
      maxResults: 100
    });
    
    const analysis = bcpFilter.analyzeBCPEmails(emails);
    
    if (emails.length > 0) {
      const exportChoice = await question('\n💾 ¿Quieres exportar los resultados a JSON? (s/n): ');
      if (exportChoice.toLowerCase() === 's' || exportChoice.toLowerCase() === 'sí') {
        await bcpFilter.exportToJSON(emails, `bcp-consumos-ultimos-${days}-dias.json`);
      }
    }
  } catch (error) {
    console.error(`❌ Error al buscar correos de los últimos ${days} días:`, error.message);
  }
}

// Manejo de cierre del programa
process.on('SIGINT', () => {
  console.log('\n👋 Programa interrumpido. ¡Hasta luego!');
  rl.close();
  process.exit(0);
});

// Ejecutar el programa principal
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { BCPEmailFilter };
