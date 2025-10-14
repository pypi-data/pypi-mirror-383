from pdf_chunk_flow.contracts.contracts import transformer
import logging
import os
from pathlib import Path
from typing import List, Dict
import pandas as pd
import pypdf
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class pdf_transformer(transformer):
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100, output_folder: str = "parquet"):
        """
        Inicializa el transformador de PDFs.
        
        Args:
            chunk_size: Tamaño de cada chunk en caracteres
            chunk_overlap: Solapamiento entre chunks consecutivos en caracteres
            output_folder: Carpeta donde se guardarán los archivos parquet
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.output_folder = output_folder
        # Crear la carpeta si no existe
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"PDF transformer inicializado. Chunk size: {chunk_size}, Overlap: {chunk_overlap}, Output folder: {output_folder}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrae todo el texto de un PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Texto completo del PDF
        """
        try:
            logger.info(f"Extrayendo texto del PDF: {pdf_path}")
            text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                logger.info(f"PDF tiene {num_pages} páginas")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    text += page_text
                    logger.debug(f"Página {page_num}/{num_pages} procesada")
            
            logger.info(f"Texto extraído exitosamente. Total de caracteres: {len(text)}")
            return text
            
        except Exception as e:
            logger.error(f"Error al extraer texto del PDF: {str(e)}")
            raise
    
    def create_chunks(self, text: str) -> List[Dict[str, any]]:
        """
        Divide el texto en chunks de tamaño especificado con overlap.
        
        Args:
            text: Texto completo a dividir
            
        Returns:
            Lista de diccionarios con los chunks y metadata
        """
        try:
            logger.info(f"Creando chunks de tamaño {self.chunk_size} caracteres con overlap de {self.chunk_overlap}")
            chunks = []
            
            # Calcular el step (avance) considerando el overlap
            step = self.chunk_size - self.chunk_overlap
            
            # Dividir el texto en chunks con overlap
            position = 0
            while position < len(text):
                # Extraer el chunk
                chunk_text = text[position:position + self.chunk_size]
                
                # Solo agregar si el chunk tiene contenido
                if chunk_text.strip():
                    chunk_data = {
                        'chunk_id': len(chunks),
                        'chunk_text': chunk_text,
                        'chunk_size': len(chunk_text),
                        'start_position': position,
                        'end_position': position + len(chunk_text),
                        'has_overlap': position > 0,  # Indica si este chunk tiene overlap con el anterior
                        'timestamp': datetime.now().isoformat()
                    }
                    chunks.append(chunk_data)
                
                # Avanzar considerando el overlap
                position += step
                
                # Si llegamos al final, asegurarnos de no quedar en un loop infinito
                if position + self.chunk_size >= len(text) and position >= len(text):
                    break
            
            logger.info(f"Se crearon {len(chunks)} chunks con overlap")
            return chunks
            
        except Exception as e:
            logger.error(f"Error al crear chunks: {str(e)}")
            raise
    
    def save_to_parquet(self, chunks: List[Dict[str, any]], pdf_path: str) -> str:
        """
        Guarda los chunks en formato parquet.
        
        Args:
            chunks: Lista de chunks a guardar
            pdf_path: Ruta del PDF original (para generar nombre del archivo)
            
        Returns:
            Ruta del archivo parquet guardado
        """
        try:
            # Crear DataFrame con los chunks
            df = pd.DataFrame(chunks)
            
            # Generar nombre del archivo parquet basado en el PDF
            pdf_filename = os.path.basename(pdf_path)
            parquet_filename = pdf_filename.replace('.pdf', '.parquet')
            parquet_path = os.path.join(self.output_folder, parquet_filename)
            
            # Guardar como parquet
            logger.info(f"Guardando {len(chunks)} chunks en formato parquet: {parquet_path}")
            df.to_parquet(parquet_path, compression='snappy', index=False)
            
            # Calcular estadísticas de compresión
            original_size = sum(chunk['chunk_size'] for chunk in chunks)
            parquet_size = os.path.getsize(parquet_path)
            compression_ratio = (1 - parquet_size / original_size) * 100
            
            logger.info(f"Archivo parquet guardado exitosamente")
            logger.info(f"Tamaño original (texto): {original_size / 1024:.2f} KB")
            logger.info(f"Tamaño parquet: {parquet_size / 1024:.2f} KB")
            logger.info(f"Ratio de compresión: {compression_ratio:.2f}%")
            
            return parquet_path
            
        except Exception as e:
            logger.error(f"Error al guardar en formato parquet: {str(e)}")
            raise
    
    def transform(self, pdf_path: str) -> str:
        """
        Transforma un PDF en chunks y lo guarda en formato parquet.
        
        Args:
            pdf_path: Ruta al archivo PDF (normalmente la salida del extractor)
            
        Returns:
            Ruta del archivo parquet generado
        """
        try:
            logger.info(f"Iniciando transformación de PDF: {pdf_path}")
            
            # 1. Extraer texto del PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            # 2. Crear chunks
            chunks = self.create_chunks(text)
            
            # 3. Guardar en formato parquet
            parquet_path = self.save_to_parquet(chunks, pdf_path)
            
            logger.info(f"Transformación completada exitosamente. Archivo: {parquet_path}")
            return parquet_path
            
        except Exception as e:
            logger.error(f"Error en el proceso de transformación: {str(e)}")
            raise

# Instancia global para importar
pdf_transformer_instance = pdf_transformer()