# scripts/extraer_cneb.py
"""Lee y estructura los textos del CNEB en fragmentos lógicos. Dueño: Dev C."""
import os
import structlog

logger = structlog.get_logger()

def extraer_fragmentos_cneb():
    ruta_raw = "data/cneb_raw/competencias.txt"
    logger.info("Iniciando extracción de contenido CNEB", archivo=ruta_raw)
    
    # Asegurar que la carpeta de datos exista
    os.makedirs("data/cneb_raw", exist_ok=True)
    
    # Crear un archivo base de ejemplo si no existe para la demo
    if not os.path.exists(ruta_raw):
        logger.warning("Archivo de origen no encontrado, generando data dummy del CNEB")
        with open(ruta_raw, "w", encoding="utf-8") as f:
            f.write(
                "COMPETENCIA: Resuelve problemas de forma, movimiento y localización.\n"
                "DESCRIPCIÓN: El estudiante modela objetos con formas geométricas y sus transformaciones.\n"
                "ESTÁNDAR: Establece relaciones entre las características de objetos reales o imaginarios y las asocia con formas bidimensionales.\n"
                "--- \n"
                "COMPETENCIA: Resuelve problemas de cantidad.\n"
                "DESCRIPCIÓN: Consiste en que el estudiante traduzca cantidades a expresiones numéricas y operaciones.\n"
            )

    with open(ruta_raw, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Separamos los bloques usando el delimitador de tres guiones '---'
    fragmentos = [bloque.strip() for bloque in contenido.split("---") if bloque.strip()]
    logger.info("Extracción finalizada con éxito", total_fragmentos=len(fragmentos))
    return fragmentos

if __name__ == "__main__":
    fragmentos = extraer_fragmentos_cneb()
    print(f"Fragmentos extraídos listos para indexar: {len(fragmentos)}")