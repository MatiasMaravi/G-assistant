"""
API REST para el Clasificador de Consumos BCP
Permite clasificar gastos bancarios y obtener análisis financiero vía HTTP
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import uvicorn
from datetime import datetime
import tempfile
import os

# Importar clasificador con manejo de errores
try:
    from clasificador_bcp import ClasificadorBCP
    CLASIFICADOR_DISPONIBLE = True
except ImportError as e:
    print(f"⚠️  Error importando clasificador: {e}")
    CLASIFICADOR_DISPONIBLE = False

# Crear instancia de FastAPI
app = FastAPI(
    title="🏦 Clasificador de Consumos BCP API",
    description="API REST para clasificar automáticamente gastos bancarios del BCP usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir acceso desde navegadores
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para validación de datos
class ConsumoManual(BaseModel):
    empresa: str
    monto: str
    tipo_tarjeta: str
    fecha: Optional[str] = None

class RespuestaClasificacion(BaseModel):
    categoria: str
    justificacion: str
    emoji: str
    monto_numerico: float

class EstadisticasRespuesta(BaseModel):
    total_consumos: int
    total_gastado: float
    categoria_mayor_gasto: str
    periodo: str

# Instancia global del clasificador
try:
    if CLASIFICADOR_DISPONIBLE:
        clasificador = ClasificadorBCP()
    else:
        clasificador = None
except Exception as e:
    print(f"⚠️  Error inicializando clasificador: {e}")
    clasificador = None
    CLASIFICADOR_DISPONIBLE = False

@app.get("/", summary="Información de la API")
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "mensaje": "🏦 API Clasificador de Consumos BCP",
        "version": "1.0.0",
        "descripcion": "Clasifica automáticamente tus gastos bancarios usando IA",
        "estado_clasificador": "Disponible" if CLASIFICADOR_DISPONIBLE else "No disponible",
        "endpoints": {
            "clasificar_archivo": "/clasificar-archivo (POST) - Clasifica desde archivo JSON del BCP",
            "clasificar_manual": "/clasificar-manual (POST) - Clasifica un consumo individual",
            "estadisticas": "/estadisticas (GET) - Obtiene estadísticas de gastos",
            "categorias": "/categorias (GET) - Lista las categorías disponibles",
            "docs": "/docs - Documentación interactiva"
        },
        "fecha_servidor": datetime.now().isoformat()
    }

@app.get("/categorias", summary="Obtener categorías disponibles")
async def obtener_categorias():
    """Retorna las 6 categorías principales de clasificación"""
    categorias = {
        'ALIMENTACIÓN': {
            'emoji': '🍕',
            'descripcion': 'Restaurantes, supermercados, delivery, cafeterías, tiendas de conveniencia',
            'ejemplos': ['KFC', 'Plaza Vea', 'Rappi', 'Starbucks', 'Tambo']
        },
        'TRANSPORTE': {
            'emoji': '🚗',
            'descripcion': 'Uber, taxi, combustible, peajes, mantenimiento vehicular',
            'ejemplos': ['Uber', 'Primax', 'Petroperú', 'Talleres']
        },
        'COMPRAS': {
            'emoji': '🛒',
            'descripcion': 'Tiendas departamentales, online, ropa, tecnología, farmacias',
            'ejemplos': ['Falabella', 'Amazon', 'Zara', 'InkaFarma']
        },
        'SERVICIOS': {
            'emoji': '🏠',
            'descripcion': 'Servicios básicos, streaming, suscripciones, seguros',
            'ejemplos': ['Netflix', 'Google', 'Luz del Sur', 'Spotify']
        },
        'BANCARIO': {
            'emoji': '💳',
            'descripcion': 'Comisiones bancarias, transferencias, servicios financieros',
            'ejemplos': ['PLIN', 'Comisiones BCP', 'Transferencias']
        },
        'ENTRETENIMIENTO': {
            'emoji': '🎮',
            'descripcion': 'Cines, gimnasios, juegos, eventos recreativos',
            'ejemplos': ['Cineplex', 'Gimnasios', 'Steam', 'Conciertos']
        }
    }
    
    return {
        "categorias": categorias,
        "total_categorias": len(categorias),
        "sistema": "Clasificación automática con IA Gemini"
    }

@app.post("/clasificar-manual", 
         summary="Clasificar un consumo individual",
         response_model=RespuestaClasificacion)
async def clasificar_consumo_manual(consumo: ConsumoManual):
    """
    Clasifica un consumo individual proporcionado manualmente
    
    Args:
        consumo: Datos del consumo (empresa, monto, tipo_tarjeta, fecha opcional)
    
    Returns:
        Clasificación con categoría, justificación y emoji
    """
    if not CLASIFICADOR_DISPONIBLE or clasificador is None:
        raise HTTPException(status_code=503, detail="Clasificador no disponible. Verifica la configuración de Vertex AI.")
    
    try:
        # Preparar datos para clasificación
        datos_consumo = {
            'empresa': consumo.empresa,
            'monto': consumo.monto,
            'tipo_tarjeta': consumo.tipo_tarjeta,
            'fecha': consumo.fecha or datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000 (UTC)")
        }
        
        # Clasificar usando el clasificador
        resultado = clasificador.clasificar_consumo(datos_consumo)
        
        if "|" in resultado:
            categoria, justificacion = resultado.split("|", 1)
            categoria = categoria.strip()
            justificacion = justificacion.strip()
        else:
            categoria = "COMPRAS"
            justificacion = resultado
        
        # Obtener emoji de la categoría
        emojis = {
            'ALIMENTACIÓN': '🍕', 'TRANSPORTE': '🚗', 'COMPRAS': '🛒',
            'SERVICIOS': '🏠', 'BANCARIO': '💳', 'ENTRETENIMIENTO': '🎮'
        }
        
        # Extraer monto numérico
        monto_numerico = 0
        try:
            monto_str = consumo.monto.replace('S/', '').replace(',', '').strip()
            monto_numerico = float(monto_str)
        except:
            pass
        
        return RespuestaClasificacion(
            categoria=categoria,
            justificacion=justificacion,
            emoji=emojis.get(categoria, '🛒'),
            monto_numerico=monto_numerico
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clasificando consumo: {str(e)}")

@app.post("/clasificar-archivo", summary="Clasificar desde archivo JSON del BCP")
async def clasificar_desde_archivo(archivo: UploadFile = File(...)):
    """
    Clasifica todos los consumos desde un archivo JSON del BCP
    
    Args:
        archivo: Archivo JSON con formato de exportación del BCP
    
    Returns:
        JSON completo con clasificación agrupada por categorías
    """
    try:
        # Verificar que sea un archivo JSON
        if not archivo.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="El archivo debe ser un JSON")
        
        # Leer contenido del archivo
        contenido = await archivo.read()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(contenido.decode('utf-8'))
            temp_path = temp_file.name
        
        try:
            # Crear instancia del clasificador con archivo temporal
            clasificador_temp = ClasificadorBCP()
            
            # Cargar datos desde el archivo temporal
            with open(temp_path, 'r', encoding='utf-8') as f:
                clasificador_temp.datos_bcp = json.load(f)
            
            # Obtener clasificación completa
            resultado = clasificador_temp.obtener_json_clasificado()
            
            if not resultado:
                raise HTTPException(status_code=400, detail="No se pudieron procesar los datos del archivo")
            
            return resultado
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El archivo JSON no es válido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@app.get("/clasificar-archivo-default", summary="Clasificar usando archivo por defecto")
async def clasificar_archivo_default():
    """
    Clasifica usando el archivo JSON por defecto del BCP (bcp-consumos-ultimos-7-dias.json)
    
    Returns:
        JSON completo con clasificación agrupada por categorías
    """
    try:
        resultado = clasificador.obtener_json_clasificado()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="No se encontró el archivo por defecto o no contiene datos")
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clasificando archivo por defecto: {str(e)}")

@app.get("/estadisticas", 
        summary="Obtener estadísticas generales",
        response_model=EstadisticasRespuesta)
async def obtener_estadisticas():
    """
    Obtiene estadísticas generales de los consumos clasificados
    
    Returns:
        Estadísticas básicas de gastos y categorías
    """
    try:
        resultado = clasificador.obtener_json_clasificado()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="No hay datos para generar estadísticas")
        
        metadata = resultado['metadata']
        resumen = resultado['resumen_categorias']
        
        # Encontrar categoría con mayor gasto
        categoria_mayor = max(resumen.items(), key=lambda x: x[1]['total'])
        
        return EstadisticasRespuesta(
            total_consumos=metadata['total_consumos'],
            total_gastado=metadata['total_gastado'],
            categoria_mayor_gasto=f"{categoria_mayor[1]['emoji']} {categoria_mayor[0]} (S/ {categoria_mayor[1]['total']})",
            periodo=metadata['periodo_datos']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@app.get("/consumos-categoria/{categoria}", summary="Obtener consumos de una categoría específica")
async def obtener_consumos_por_categoria(categoria: str):
    """
    Obtiene todos los consumos de una categoría específica
    
    Args:
        categoria: Nombre de la categoría (ALIMENTACIÓN, COMPRAS, etc.)
    
    Returns:
        Lista de consumos de la categoría solicitada
    """
    try:
        categoria = categoria.upper()
        
        resultado = clasificador.obtener_json_clasificado()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="No hay datos disponibles")
        
        if categoria not in resultado['consumos_por_categoria']:
            raise HTTPException(status_code=404, detail=f"Categoría '{categoria}' no encontrada")
        
        return resultado['consumos_por_categoria'][categoria]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo consumos: {str(e)}")

@app.get("/health", summary="Estado de salud de la API")
async def health_check():
    """Endpoint para verificar que la API está funcionando"""
    try:
        # Verificar conexión con Vertex AI
        test_consumo = {
            'empresa': 'TEST',
            'monto': 'S/ 10.00',
            'tipo_tarjeta': 'Débito',
            'fecha': '2025-01-01'
        }
        
        # Intentar clasificar un consumo de prueba
        clasificador.clasificar_consumo(test_consumo)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "vertex_ai": "connected",
            "clasificador": "functional"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Función para ejecutar el servidor
def iniciar_servidor(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """
    Inicia el servidor de la API
    
    Args:
        host: Dirección IP (0.0.0.0 para acceso público)
        port: Puerto (8000 por defecto)
        reload: Recarga automática en desarrollo
    """
    print(f"🚀 Iniciando API Clasificador BCP en http://{host}:{port}")
    print(f"📚 Documentación disponible en: http://{host}:{port}/docs")
    print(f"🔍 API alternativa en: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "api_clasificador_bcp:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    iniciar_servidor()
