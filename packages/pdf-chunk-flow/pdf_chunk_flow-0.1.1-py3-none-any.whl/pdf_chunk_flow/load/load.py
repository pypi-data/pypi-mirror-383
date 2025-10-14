from pdf_chunk_flow.contracts.contracts import loader
import logging
import os
import shutil
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class parquet_loader(loader):
    def __init__(self, output_folder: str = "parquet_chunk"):
        """
        Inicializa el loader/validador de parquet.
        
        Args:
            output_folder: Carpeta donde se cargarán los parquet validados
        """
        self.output_folder = output_folder
        # Crear la carpeta si no existe
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"Parquet loader inicializado. Carpeta de destino: {self.output_folder}")
    
    def validate_parquet(self, parquet_path: str) -> tuple[bool, str]:
        """
        Valida que el archivo parquet esté bien formado y tenga la estructura correcta.
        
        Args:
            parquet_path: Ruta al archivo parquet a validar
            
        Returns:
            Tupla (es_valido, mensaje)
        """
        try:
            logger.info(f"Validando archivo parquet: {parquet_path}")
            
            # 1. Verificar que el archivo existe
            if not os.path.exists(parquet_path):
                return False, f"El archivo no existe: {parquet_path}"
            
            # 2. Intentar leer el parquet
            try:
                df = pd.read_parquet(parquet_path)
            except Exception as e:
                return False, f"Error al leer el parquet: {str(e)}"
            
            # 3. Verificar que no esté vacío
            if len(df) == 0:
                return False, "El parquet está vacío (0 filas)"
            
            # 4. Verificar columnas requeridas
            required_columns = ['chunk_id', 'chunk_text', 'chunk_size', 'start_position', 
                              'end_position', 'has_overlap', 'timestamp']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Faltan columnas requeridas: {missing_columns}"
            
            # 5. Verificar que los chunks tengan contenido
            empty_chunks = df[df['chunk_text'].str.strip() == ''].shape[0]
            if empty_chunks > 0:
                logger.warning(f"Se encontraron {empty_chunks} chunks vacíos")
            
            # 6. Verificar que los chunk_ids sean consecutivos
            expected_ids = list(range(len(df)))
            actual_ids = df['chunk_id'].tolist()
            if expected_ids != actual_ids:
                return False, "Los chunk_ids no son consecutivos"
            
            # 7. Validar tipos de datos
            if not pd.api.types.is_integer_dtype(df['chunk_id']):
                return False, "chunk_id debe ser entero"
            
            if not pd.api.types.is_integer_dtype(df['chunk_size']):
                return False, "chunk_size debe ser entero"
            
            # Estadísticas del parquet
            total_chunks = len(df)
            total_chars = df['chunk_size'].sum()
            avg_chunk_size = df['chunk_size'].mean()
            chunks_with_overlap = df['has_overlap'].sum()
            
            logger.info(f"✓ Validación exitosa:")
            logger.info(f"  - Total de chunks: {total_chunks}")
            logger.info(f"  - Total de caracteres: {total_chars}")
            logger.info(f"  - Tamaño promedio de chunk: {avg_chunk_size:.2f} caracteres")
            logger.info(f"  - Chunks con overlap: {chunks_with_overlap}")
            
            return True, "Parquet válido"
            
        except Exception as e:
            logger.error(f"Error durante la validación: {str(e)}")
            return False, f"Error inesperado: {str(e)}"
    
    def load(self, parquet_path: str) -> str:
        """
        Valida y carga el archivo parquet a la carpeta de destino.
        
        Args:
            parquet_path: Ruta al archivo parquet (salida del transformer)
            
        Returns:
            Ruta del archivo parquet en la carpeta de destino
        """
        try:
            logger.info(f"Iniciando carga de parquet: {parquet_path}")
            
            # 1. Validar el parquet
            is_valid, message = self.validate_parquet(parquet_path)
            
            if not is_valid:
                logger.error(f"Validación falló: {message}")
                raise ValueError(f"Parquet inválido: {message}")
            
            logger.info(f"✓ {message}")
            
            # 2. Copiar el archivo a la carpeta de destino
            filename = os.path.basename(parquet_path)
            destination_path = os.path.abspath(os.path.join(self.output_folder, filename))
            
            logger.info(f"Copiando parquet validado a: {destination_path}")
            shutil.copy2(parquet_path, destination_path)
            
            # 3. Verificar que la copia fue exitosa
            if os.path.exists(destination_path):
                src_size = os.path.getsize(parquet_path)
                dst_size = os.path.getsize(destination_path)
                
                if src_size == dst_size:
                    logger.info(f"✓ Archivo copiado exitosamente. Tamaño: {dst_size / 1024:.2f} KB")
                else:
                    raise ValueError(f"Error: tamaños no coinciden (src: {src_size}, dst: {dst_size})")
            else:
                raise ValueError("Error: el archivo no se copió correctamente")
            
            logger.info(f"Carga completada exitosamente: {destination_path}")
            return destination_path
            
        except Exception as e:
            logger.error(f"Error en el proceso de carga: {str(e)}")
            raise

# Instancia global para importar
parquet_loader_instance = parquet_loader()