#!/usr/bin/env python3
"""
Pipeline ETL con inyección de dependencias
"""
from pdf_chunk_flow.extract.extract import pdf_extractor_instance
from pdf_chunk_flow.tranform.transform import pdf_transformer_instance
from pdf_chunk_flow.load.load import parquet_loader_instance
import logging
from dotenv import load_dotenv

# Cargar variables de entorno si tienes un .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='etl_pipeline.log',
    filemode='a'
)


def MacroEtlPdfChunks(url: str) -> str | None:
    """
    Se le pasa la URL de un PDF, lo descarga, lo transforma en chunks
    y los guarda en formato parquet validado.
    Retorna la ruta del archivo parquet final.

    You pass the URL of a PDF file, download it, transform it into chunks,
    and save them as a validated parquet file.
    """

    # 1️⃣ Extraer
    try:
        pdf_path = pdf_extractor_instance.extract(url)
        if not pdf_path:
            logging.error(f"Error al descargar el PDF desde {url}")
            return None
    except Exception as e:
        logging.error(f"Error al descargar el PDF desde {url}: {str(e)}")
        return None

    # 2️⃣ Transformar
    try:
        parquet_path = pdf_transformer_instance.transform(pdf_path)
        if not parquet_path:
            logging.error(f"Error al transformar el PDF {pdf_path}")
            return None
    except Exception as e:
        logging.error(f"Error al transformar el PDF {pdf_path}: {str(e)}")
        return None

    # 3️⃣ Cargar/Validar
    try:
        final_parquet = parquet_loader_instance.load(parquet_path)
        if not final_parquet:
            logging.error(f"Error al cargar/validar el parquet {parquet_path}")
            return None
    except Exception as e:
        logging.error(f"Error al cargar/validar el parquet {parquet_path}: {str(e)}")
        return None

    # 4️⃣ Retornar ruta del parquet final
    logging.info(f"✓ Pipeline completado exitosamente: {final_parquet}")
    return final_parquet
