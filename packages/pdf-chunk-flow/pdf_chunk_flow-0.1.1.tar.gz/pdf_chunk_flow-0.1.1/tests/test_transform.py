import pytest
import os
import tempfile
import shutil
import pandas as pd
from pypdf import PdfWriter
from pdf_chunk_flow.tranform.transform import pdf_transformer


class TestPdfTransformer:
    """Tests para el componente de transformación de PDFs"""
    
    @pytest.fixture
    def temp_folders(self):
        """Crea carpetas temporales para input y output"""
        input_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        yield input_dir, output_dir
        shutil.rmtree(input_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_pdf(self, temp_folders):
        """Crea un PDF de prueba"""
        input_dir, _ = temp_folders
        pdf_path = os.path.join(input_dir, "test.pdf")
        
        # Crear un PDF simple con pypdf
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        
        with open(pdf_path, 'wb') as f:
            writer.write(f)
        
        return pdf_path
    
    @pytest.fixture
    def transformer(self, temp_folders):
        """Crea una instancia del transformer"""
        _, output_dir = temp_folders
        return pdf_transformer(
            chunk_size=100,
            chunk_overlap=20,
            output_folder=output_dir
        )
    
    def test_transformer_initialization(self, temp_folders):
        """Test: El transformer se inicializa correctamente"""
        _, output_dir = temp_folders
        transformer = pdf_transformer(
            chunk_size=600,
            chunk_overlap=100,
            output_folder=output_dir
        )
        
        assert transformer.chunk_size == 600
        assert transformer.chunk_overlap == 100
        assert transformer.output_folder == output_dir
        assert os.path.exists(output_dir)
    
    def test_create_chunks_no_overlap(self):
        """Test: Crear chunks sin overlap"""
        transformer = pdf_transformer(chunk_size=10, chunk_overlap=0)
        text = "0123456789" * 3  # 30 caracteres
        
        chunks = transformer.create_chunks(text)
        
        assert len(chunks) == 3
        assert chunks[0]['chunk_text'] == "0123456789"
        assert chunks[1]['chunk_text'] == "0123456789"
        assert chunks[2]['chunk_text'] == "0123456789"
    
    def test_create_chunks_with_overlap(self):
        """Test: Crear chunks con overlap"""
        transformer = pdf_transformer(chunk_size=10, chunk_overlap=3)
        text = "0123456789ABCDEFGHIJ"  # 20 caracteres
        
        chunks = transformer.create_chunks(text)
        
        # Chunk size 10, overlap 3, step = 7
        assert len(chunks) == 3
        assert chunks[0]['start_position'] == 0
        assert chunks[1]['start_position'] == 7
        assert chunks[2]['start_position'] == 14
        assert chunks[1]['has_overlap'] is True
        assert chunks[0]['has_overlap'] is False
    
    def test_create_chunks_metadata(self):
        """Test: Los chunks tienen toda la metadata necesaria"""
        transformer = pdf_transformer(chunk_size=10, chunk_overlap=2)
        text = "Hello World!"
        
        chunks = transformer.create_chunks(text)
        
        assert len(chunks) > 0
        chunk = chunks[0]
        
        # Verificar que tiene todas las columnas requeridas
        assert 'chunk_id' in chunk
        assert 'chunk_text' in chunk
        assert 'chunk_size' in chunk
        assert 'start_position' in chunk
        assert 'end_position' in chunk
        assert 'has_overlap' in chunk
        assert 'timestamp' in chunk
    
    def test_save_to_parquet(self, transformer, temp_folders):
        """Test: Guardar chunks en formato parquet"""
        _, output_dir = temp_folders
        
        chunks = [
            {
                'chunk_id': 0,
                'chunk_text': 'Test chunk',
                'chunk_size': 10,
                'start_position': 0,
                'end_position': 10,
                'has_overlap': False,
                'timestamp': '2025-01-01T00:00:00'
            }
        ]
        
        pdf_path = "test.pdf"
        result = transformer.save_to_parquet(chunks, pdf_path)
        
        assert result.endswith('.parquet')
        assert os.path.exists(result)
        
        # Leer y verificar el parquet
        df = pd.read_parquet(result)
        assert len(df) == 1
        assert df.iloc[0]['chunk_text'] == 'Test chunk'
    
    def test_parquet_has_correct_columns(self, transformer, temp_folders):
        """Test: El parquet tiene todas las columnas requeridas"""
        _, output_dir = temp_folders
        
        chunks = [
            {
                'chunk_id': 0,
                'chunk_text': 'Test',
                'chunk_size': 4,
                'start_position': 0,
                'end_position': 4,
                'has_overlap': False,
                'timestamp': '2025-01-01T00:00:00'
            }
        ]
        
        result = transformer.save_to_parquet(chunks, "test.pdf")
        df = pd.read_parquet(result)
        
        required_columns = ['chunk_id', 'chunk_text', 'chunk_size', 
                          'start_position', 'end_position', 'has_overlap', 'timestamp']
        
        for col in required_columns:
            assert col in df.columns
    
    def test_chunk_size_parameter(self):
        """Test: El chunk_size se respeta"""
        transformer = pdf_transformer(chunk_size=50, chunk_overlap=0)
        text = "a" * 150
        
        chunks = transformer.create_chunks(text)
        
        # Verificar que los primeros chunks tienen el tamaño correcto
        assert chunks[0]['chunk_size'] == 50
        assert chunks[1]['chunk_size'] == 50
        assert chunks[2]['chunk_size'] == 50

