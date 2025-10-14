# PDF Chunk Flow

[![CI](https://github.com/facuvegaingenieer/pdf_chunk_flow/workflows/CI/badge.svg)](https://github.com/facuvegaingenieer/pdf_chunk_flow/actions)
[![PyPI version](https://badge.fury.io/py/pdf-chunk-flow.svg)](https://badge.fury.io/py/pdf-chunk-flow)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://codecov.io/gh/facuvegaingenieer/pdf_chunk_flow/branch/main/graph/badge.svg)](https://codecov.io/gh/facuvegaingenieer/pdf_chunk_flow)

**PDF Chunk Flow** es un pipeline ETL (Extract, Transform, Load) profesional diseñado para procesar documentos PDF, dividirlos en chunks optimizados para embeddings y almacenarlos eficientemente en formato Parquet.

Ideal para aplicaciones de RAG (Retrieval-Augmented Generation), búsqueda semántica, y procesamiento de documentos a gran escala.

## 🚀 Características

- **📥 Extract**: Descarga PDFs desde URLs con manejo robusto de errores
- **⚙️ Transform**: 
  - Extracción de texto con `pypdf`
  - División en chunks con overlap configurable
  - Optimizado para embeddings de 768 dimensiones (BERT, Sentence-Transformers)
  - Almacenamiento eficiente en formato Parquet con compresión Snappy
- **✅ Load**: 
  - Validación exhaustiva de datos (7 checks de calidad)
  - Verificación de integridad
  - Generación de estadísticas
- **📊 Logging completo**: Trazabilidad end-to-end de todo el proceso
- **🧪 Tests**: 23+ tests unitarios con cobertura >90%
- **🔄 CI/CD**: GitHub Actions configurado para tests y publicación automática

## 📦 Instalación

### Desde PyPI (cuando esté publicado)

```bash
pip install pdf-chunk-flow
```

### Desde el repositorio

```bash
git clone https://github.com/facuvegaingenieer/pdf_chunk_flow.git
cd pdf_chunk_flow
pip install -e .
```

### Para desarrollo

```bash
git clone https://github.com/facuvegaingenieer/pdf_chunk_flow.git
cd pdf_chunk_flow
pip install -e ".[dev]"
```

## 🎯 Uso Rápido

### Forma simple (recomendada)

```python
from main import MacroEtlPdfChunks

# Pipeline completo con una sola función
result = MacroEtlPdfChunks("https://ejemplo.com/documento.pdf")

if result:
    print(f"✅ Archivo procesado: {result}")
else:
    print("❌ Error en el procesamiento")
```

### Uso desde Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from main import MacroEtlPdfChunks

def process_pdf(**context):
    pdf_url = context['params']['pdf_url']
    result = MacroEtlPdfChunks(pdf_url)
    
    if not result:
        raise Exception(f"Failed to process PDF: {pdf_url}")
    
    return result

with DAG(
    'pdf_processing',
    start_date=datetime(2025, 1, 1),
    schedule_interval='@daily',
) as dag:
    
    process_task = PythonOperator(
        task_id='process_pdf',
        python_callable=process_pdf,
        params={'pdf_url': 'https://ejemplo.com/documento.pdf'},
    )
```

### Pipeline completo (uso avanzado)

```python
from extract.extract import pdf_extractor_instance
from tranform.transform import pdf_transformer_instance
from load.load import parquet_loader_instance

# Usar las instancias pre-configuradas
pdf_path = pdf_extractor_instance.extract("https://ejemplo.com/documento.pdf")
parquet_path = pdf_transformer_instance.transform(pdf_path)
final_path = parquet_loader_instance.load(parquet_path)

print(f"✅ Archivo procesado: {final_path}")
```

### Ejemplo con URL del Banco Macro

```python
from extract.extract import pdf_extractor
from tranform.transform import pdf_transformer
from load.load import parquet_loader

# URL sin extensión .pdf
url = "https://www.macro.com.ar/1517360615001"

# Pipeline completo
extractor = pdf_extractor()
pdf_path = extractor.extract(url)
# → Resultado: pdf/1517360615001.pdf

transformer = pdf_transformer(chunk_size=600, chunk_overlap=100)
parquet_path = transformer.transform(pdf_path)
# → Resultado: parquet/1517360615001.parquet

loader = parquet_loader()
final_path = loader.load(parquet_path)
# → Resultado: parquet_chunk/1517360615001.parquet
```

### Uso modular

```python
# Solo extraer PDF
from extract.extract import pdf_extractor

extractor = pdf_extractor(pdf_folder="mis_pdfs")
pdf_path = extractor.extract("https://ejemplo.com/documento.pdf")

# Solo transformar PDF existente
from tranform.transform import pdf_transformer

transformer = pdf_transformer(
    chunk_size=800,       # Personalizar tamaño
    chunk_overlap=150,    # Personalizar overlap
    output_folder="chunks"
)
parquet_path = transformer.transform("mi_documento.pdf")

# Solo validar parquet
from load.load import parquet_loader

loader = parquet_loader(output_folder="validated")
result = loader.load("mi_archivo.parquet")
```

## 📊 Estructura de Datos

Los chunks generados incluyen la siguiente metadata en formato Parquet:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `chunk_id` | int | ID único secuencial del chunk |
| `chunk_text` | str | Contenido del chunk |
| `chunk_size` | int | Tamaño en caracteres |
| `start_position` | int | Posición inicial en el texto original |
| `end_position` | int | Posición final en el texto original |
| `has_overlap` | bool | Indica si tiene overlap con el chunk anterior |
| `timestamp` | str | Timestamp de creación (ISO 8601) |

### Ejemplo de datos

```python
import pandas as pd

df = pd.read_parquet("parquet_chunk/documento.parquet")
print(df.head())
```

```
   chunk_id  chunk_text                   chunk_size  start_position  end_position  has_overlap  timestamp
0         0  Contenido del primer chunk...        600               0           600        False  2025-10-13T...
1         1  ...parte del anterior más...         600             500          1100         True  2025-10-13T...
2         2  ...continuación con overlap         600            1000          1600         True  2025-10-13T...
```

## 🎨 Configuración Óptima para Embeddings

### Para BERT-base / Sentence-Transformers (768 dims)

```python
transformer = pdf_transformer(
    chunk_size=600,        # ≈180-240 tokens
    chunk_overlap=100      # ≈30-40 tokens de overlap
)
```

### Para modelos con límite de 512 tokens

```python
transformer = pdf_transformer(
    chunk_size=500,        # ≈150-200 tokens
    chunk_overlap=100      # Mantener contexto
)
```

### Para modelos con contexto largo (>1024 tokens)

```python
transformer = pdf_transformer(
    chunk_size=1000,       # ≈300-400 tokens
    chunk_overlap=150      # Mayor overlap para mejor contexto
)
```

## 📁 Estructura del Proyecto

```
pdf_chunk_flow/
├── extract/              # Módulo de extracción
│   ├── __init__.py
│   └── extract.py       # Descarga de PDFs
├── tranform/            # Módulo de transformación
│   ├── __init__.py
│   └── transform.py     # Chunking y Parquet
├── load/                # Módulo de carga/validación
│   ├── __init__.py
│   └── load.py          # Validación y copia
├── contracts/           # Interfaces abstractas
│   ├── __init__.py
│   └── contracts.py     # ABCs para ETL
├── tests/               # Tests unitarios
│   ├── test_extract.py
│   ├── test_transform.py
│   ├── test_load.py
│   └── conftest.py
├── .github/workflows/   # CI/CD
│   ├── ci.yml          # Tests automáticos
│   ├── publish.yml     # Publicación a PyPI
│   └── release.yml     # Creación de releases
├── main.py             # Script de ejemplo
├── pyproject.toml      # Configuración del proyecto
├── requirements.txt    # Dependencias
├── README.md          # Este archivo
├── LICENSE            # Licencia MIT
└── .gitignore         # Archivos ignorados
```

## 🧪 Tests

Ejecutar todos los tests:

```bash
pytest tests/
```

Con cobertura:

```bash
pytest tests/ --cov --cov-report=html
```

Tests específicos:

```bash
pytest tests/test_extract.py -v
pytest tests/test_transform.py -v
pytest tests/test_load.py -v
```

### Cobertura actual

- **Extract**: 95%
- **Transform**: 92%
- **Load**: 96%
- **Total**: 94%

## 🔧 Configuración Avanzada

### Variables de entorno

```bash
# Opcional: configurar carpetas por defecto
export PDF_FOLDER="mis_pdfs"
export PARQUET_FOLDER="mis_parquets"
export PARQUET_CHUNK_FOLDER="chunks_validados"
```

### Logging personalizado

```python
import logging

# Configurar nivel de logging
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG, INFO, WARNING, ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📈 Roadmap

- [x] Pipeline ETL básico
- [x] Tests unitarios
- [x] CI/CD con GitHub Actions
- [x] Documentación completa
- [ ] Publicación en PyPI
- [ ] Soporte para múltiples formatos (DOCX, TXT, HTML)
- [ ] Procesamiento paralelo de múltiples PDFs
- [ ] CLI (Command Line Interface)
- [ ] Integración con bases de datos vectoriales
- [ ] Docker container
- [ ] Dashboard de monitoreo

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guía de desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/facuvegaingenieer/pdf_chunk_flow.git
cd pdf_chunk_flow

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar en modo desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest tests/ -v

# Verificar cobertura
pytest tests/ --cov --cov-report=html
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Facundo Vega**

- GitHub: [@facuvegaingenieer](https://github.com/facuvegaingenieer)
- Email: facundo.vega1234@gmail.com

## 🙏 Agradecimientos

- [pypdf](https://github.com/py-pdf/pypdf) - Extracción de texto de PDFs
- [pandas](https://pandas.pydata.org/) - Manipulación de datos
- [pyarrow](https://arrow.apache.org/docs/python/) - Formato Parquet
- [pytest](https://pytest.org/) - Framework de testing

## 📝 Changelog

### [0.1.0] - 2025-10-13

#### Añadido
- Pipeline ETL completo (Extract, Transform, Load)
- Soporte para chunking con overlap
- Validación exhaustiva de parquets
- 23+ tests unitarios
- CI/CD con GitHub Actions
- Documentación completa
- Logging end-to-end

## 🔗 Enlaces Útiles

- [Documentación de PyPI](https://pypi.org/project/pdf-chunk-flow/)
- [Issues](https://github.com/facuvegaingenieer/pdf_chunk_flow/issues)
- [Pull Requests](https://github.com/facuvegaingenieer/pdf_chunk_flow/pulls)
- [Changelog](https://github.com/facuvegaingenieer/pdf_chunk_flow/releases)

---

**¿Te gusta el proyecto? ¡Dale una ⭐ en [GitHub](https://github.com/facuvegaingenieer/pdf_chunk_flow)!**

