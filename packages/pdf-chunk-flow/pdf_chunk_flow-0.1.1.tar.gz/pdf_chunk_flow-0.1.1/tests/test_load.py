import pytest
import os
import tempfile
import shutil
import pandas as pd
from pdf_chunk_flow.load.load import parquet_loader


class TestParquetLoader:
    """Tests para el componente de carga/validación de parquets"""
    
    @pytest.fixture
    def temp_folders(self):
        """Crea carpetas temporales para input y output"""
        input_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        yield input_dir, output_dir
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)
    
    @pytest.fixture
    def valid_parquet(self, temp_folders):
        """Crea un parquet válido para testing"""
        input_dir, _ = temp_folders
        parquet_path = os.path.join(input_dir, "test.parquet")
        
        data = {
            'chunk_id': [0, 1, 2],
            'chunk_text': ['chunk 1', 'chunk 2', 'chunk 3'],
            'chunk_size': [7, 7, 7],
            'start_position': [0, 5, 10],
            'end_position': [7, 12, 17],
            'has_overlap': [False, True, True],
            'timestamp': ['2025-01-01T00:00:00'] * 3
        }
        
        df = pd.DataFrame(data)
        df.to_parquet(parquet_path, index=False)
        
        return parquet_path
    
    @pytest.fixture
    def loader(self, temp_folders):
        """Crea una instancia del loader"""
        _, output_dir = temp_folders
        return parquet_loader(output_folder=output_dir)
    
    def test_loader_initialization(self, temp_folders):
        """Test: El loader se inicializa correctamente"""
        _, output_dir = temp_folders
        loader = parquet_loader(output_folder=output_dir)
        
        assert loader.output_folder == output_dir
        assert os.path.exists(output_dir)
    
    def test_validate_valid_parquet(self, loader, valid_parquet):
        """Test: Valida correctamente un parquet válido"""
        is_valid, message = loader.validate_parquet(valid_parquet)
        
        assert is_valid is True
        assert message == "Parquet válido"
    
    def test_validate_nonexistent_file(self, loader):
        """Test: Rechaza archivo que no existe"""
        is_valid, message = loader.validate_parquet("/path/to/nonexistent.parquet")
        
        assert is_valid is False
        assert "no existe" in message
    
    def test_validate_empty_parquet(self, loader, temp_folders):
        """Test: Rechaza parquet vacío"""
        input_dir, _ = temp_folders
        empty_parquet = os.path.join(input_dir, "empty.parquet")
        
        # Crear parquet vacío
        df = pd.DataFrame({
            'chunk_id': [],
            'chunk_text': [],
            'chunk_size': [],
            'start_position': [],
            'end_position': [],
            'has_overlap': [],
            'timestamp': []
        })
        df.to_parquet(empty_parquet, index=False)
        
        is_valid, message = loader.validate_parquet(empty_parquet)
        
        assert is_valid is False
        assert "vacío" in message
    
    def test_validate_missing_columns(self, loader, temp_folders):
        """Test: Rechaza parquet con columnas faltantes"""
        input_dir, _ = temp_folders
        invalid_parquet = os.path.join(input_dir, "invalid.parquet")
        
        # Crear parquet sin todas las columnas
        df = pd.DataFrame({
            'chunk_id': [0],
            'chunk_text': ['test']
            # Faltan columnas requeridas
        })
        df.to_parquet(invalid_parquet, index=False)
        
        is_valid, message = loader.validate_parquet(invalid_parquet)
        
        assert is_valid is False
        assert "columnas requeridas" in message
    
    def test_validate_non_consecutive_ids(self, loader, temp_folders):
        """Test: Rechaza parquet con IDs no consecutivos"""
        input_dir, _ = temp_folders
        invalid_parquet = os.path.join(input_dir, "invalid_ids.parquet")
        
        data = {
            'chunk_id': [0, 2, 3],  # Falta el ID 1
            'chunk_text': ['chunk 0', 'chunk 2', 'chunk 3'],
            'chunk_size': [7, 7, 7],
            'start_position': [0, 5, 10],
            'end_position': [7, 12, 17],
            'has_overlap': [False, True, True],
            'timestamp': ['2025-01-01T00:00:00'] * 3
        }
        
        df = pd.DataFrame(data)
        df.to_parquet(invalid_parquet, index=False)
        
        is_valid, message = loader.validate_parquet(invalid_parquet)
        
        assert is_valid is False
        assert "consecutivos" in message
    
    def test_load_valid_parquet(self, loader, valid_parquet, temp_folders):
        """Test: Carga un parquet válido correctamente"""
        _, output_dir = temp_folders
        
        result = loader.load(valid_parquet)
        
        # Verificar que se copió al destino
        assert result.startswith(output_dir) or os.path.isabs(result)
        assert os.path.exists(result)
        assert result.endswith('.parquet')
    
    def test_load_creates_copy(self, loader, valid_parquet):
        """Test: La carga crea una copia del archivo"""
        result = loader.load(valid_parquet)
        
        # Verificar que ambos archivos existen
        assert os.path.exists(valid_parquet)
        assert os.path.exists(result)
        
        # Verificar que tienen el mismo contenido
        df_original = pd.read_parquet(valid_parquet)
        df_copied = pd.read_parquet(result)
        
        assert df_original.equals(df_copied)
    
    def test_load_invalid_parquet_raises_error(self, loader, temp_folders):
        """Test: La carga falla con parquet inválido"""
        input_dir, _ = temp_folders
        invalid_parquet = os.path.join(input_dir, "invalid.parquet")
        
        # Crear parquet inválido
        df = pd.DataFrame({'invalid': [1, 2, 3]})
        df.to_parquet(invalid_parquet, index=False)
        
        with pytest.raises(ValueError):
            loader.load(invalid_parquet)
    
    def test_load_returns_absolute_path(self, loader, valid_parquet):
        """Test: El load retorna ruta absoluta"""
        result = loader.load(valid_parquet)
        
        assert os.path.isabs(result)

