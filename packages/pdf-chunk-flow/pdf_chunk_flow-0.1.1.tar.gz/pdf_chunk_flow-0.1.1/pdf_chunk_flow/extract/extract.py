from pdf_chunk_flow.contracts.contracts import extractor
import requests
import os
import logging
from pathlib import Path
from urllib.parse import urlparse

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class pdf_extractor(extractor):
    def __init__(self, pdf_folder: str = "pdf"):
        """
        Inicializa el extractor de PDFs.
        
        Args:
            pdf_folder: Carpeta donde se guardarán los PDFs descargados
        """
        self.pdf_folder = pdf_folder
        # Crear la carpeta si no existe
        Path(self.pdf_folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"PDF extractor inicializado. Carpeta de destino: {self.pdf_folder}")
    
    def extract(self, url: str) -> str:
        """
        Descarga un PDF desde una URL y lo guarda en la carpeta pdf.
        
        Args:
            url: URL del PDF a descargar
            
        Returns:
            Ruta del archivo PDF guardado
        """
        try:
            logger.info(f"Iniciando descarga de PDF desde: {url}")
            
            # Realizar la petición para descargar el PDF
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Lanza excepción si hay error HTTP
            
            logger.debug(f"Respuesta HTTP recibida. Status code: {response.status_code}")
            
            # Obtener el nombre del archivo desde la URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Determinar el nombre del archivo
            if not filename:
                # Si no hay path, usar hash
                filename = f"documento_{hash(url) % 1000000}.pdf"
                logger.warning(f"Nombre de archivo no encontrado en URL. Usando nombre generado: {filename}")
            elif not filename.endswith('.pdf'):
                # Si hay nombre pero no termina en .pdf, agregárselo
                filename = f"{filename}.pdf"
                logger.info(f"Nombre de archivo detectado (agregando .pdf): {filename}")
            else:
                logger.info(f"Nombre de archivo detectado: {filename}")
            
            # Ruta completa donde se guardará el archivo
            filepath = os.path.join(self.pdf_folder, filename)
            
            # Guardar el PDF en la carpeta
            logger.info(f"Guardando PDF en: {filepath}")
            bytes_downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
            
            logger.info(f"PDF descargado exitosamente. Tamaño: {bytes_downloaded / 1024:.2f} KB")
            logger.info(f"Archivo guardado en: {filepath}")
            
            return filepath
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al descargar PDF desde {url}: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Error al guardar el archivo: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            raise

# Instancia global para importar
pdf_extractor_instance = pdf_extractor()