"""
pdf-chunk-flow: ETL pipeline for PDF processing with chunking and parquet storage
"""

from pdf_chunk_flow.extract.extract import pdf_extractor, pdf_extractor_instance
from pdf_chunk_flow.tranform.transform import pdf_transformer, pdf_transformer_instance
from pdf_chunk_flow.load.load import parquet_loader, parquet_loader_instance
from pdf_chunk_flow.main import MacroEtlPdfChunks

__version__ = "0.1.1"

__all__ = [
    # Classes
    "pdf_extractor",
    "pdf_transformer",
    "parquet_loader",
    # Instances
    "pdf_extractor_instance",
    "pdf_transformer_instance",
    "parquet_loader_instance",
    # Main function
    "MacroEtlPdfChunks",
]

