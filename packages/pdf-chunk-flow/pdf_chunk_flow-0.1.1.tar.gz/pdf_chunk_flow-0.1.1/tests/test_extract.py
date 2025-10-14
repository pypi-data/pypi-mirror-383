import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pdf_chunk_flow.extract.extract import pdf_extractor


class TestPdfExtractor:
    """Tests para el componente de extracción de PDFs"""
    
    @pytest.fixture
    def temp_folder(self):
        """Crea una carpeta temporal para tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def extractor(self, temp_folder):
        """Crea una instancia del extractor"""
        return pdf_extractor(pdf_folder=temp_folder)
    
    def test_extractor_initialization(self, temp_folder):
        """Test: El extractor se inicializa correctamente"""
        extractor = pdf_extractor(pdf_folder=temp_folder)
        assert extractor.pdf_folder == temp_folder
        assert os.path.exists(temp_folder)
    
    def test_folder_creation(self, temp_folder):
        """Test: La carpeta se crea si no existe"""
        test_folder = os.path.join(temp_folder, "new_folder")
        assert not os.path.exists(test_folder)
        
        extractor = pdf_extractor(pdf_folder=test_folder)
        assert os.path.exists(test_folder)
    
    @patch('pdf_chunk_flow.extract.extract.requests.get')
    def test_extract_pdf_with_pdf_extension(self, mock_get, extractor, temp_folder):
        """Test: Descarga PDF con extensión .pdf en la URL"""
        # Mock de la respuesta HTTP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'PDF content'])
        mock_get.return_value = mock_response
        
        url = "https://example.com/document.pdf"
        result = extractor.extract(url)
        
        assert result == os.path.join(temp_folder, "document.pdf")
        assert os.path.exists(result)
        mock_get.assert_called_once_with(url, stream=True)
    
    @patch('pdf_chunk_flow.extract.extract.requests.get')
    def test_extract_pdf_without_pdf_extension(self, mock_get, extractor, temp_folder):
        """Test: Descarga PDF sin extensión .pdf en la URL"""
        # Mock de la respuesta HTTP
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'PDF content'])
        mock_get.return_value = mock_response
        
        url = "https://example.com/1517360615001"
        result = extractor.extract(url)
        
        expected_file = os.path.join(temp_folder, "1517360615001.pdf")
        assert result == expected_file
        assert os.path.exists(result)
    
    @patch('pdf_chunk_flow.extract.extract.requests.get')
    def test_extract_handles_http_error(self, mock_get, extractor):
        """Test: Maneja errores HTTP correctamente"""
        mock_get.return_value.raise_for_status.side_effect = Exception("HTTP 404")
        
        url = "https://example.com/nonexistent.pdf"
        
        with pytest.raises(Exception):
            extractor.extract(url)
    
    @patch('pdf_chunk_flow.extract.extract.requests.get')
    def test_extract_downloads_content(self, mock_get, extractor, temp_folder):
        """Test: El contenido se descarga correctamente"""
        # Mock de la respuesta HTTP con contenido
        mock_response = Mock()
        mock_response.status_code = 200
        test_content = b'Test PDF content with multiple chunks'
        mock_response.iter_content = Mock(return_value=[test_content[:10], test_content[10:]])
        mock_get.return_value = mock_response
        
        url = "https://example.com/test.pdf"
        result = extractor.extract(url)
        
        # Verificar que el archivo se creó y tiene contenido
        assert os.path.exists(result)
        with open(result, 'rb') as f:
            content = f.read()
        assert content == test_content

