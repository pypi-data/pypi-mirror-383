import pytest
import pandas as pd
import tempfile
from pathlib import Path
from transform.transform import transform_embedding


def test_transform_creates_embeddings():
    """Test que transform genera embeddings de 768 dimensiones"""
    # Crear parquet temporal con texto
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
        df = pd.DataFrame({
            'text': ['test text 1', 'test text 2', 'test text 3']
        })
        df.to_parquet(tmp.name, index=False)
        tmp_path = tmp.name
    
    try:
        # Transformar
        transformer = transform_embedding()
        output_path = transformer.transform_data(tmp_path)
        
        # Verificar
        assert output_path is not None
        assert Path(output_path).exists()
        
        # Verificar dimensiones
        result_df = pd.read_parquet(output_path)
        assert 'embedding' in result_df.columns
        assert len(result_df['embedding'][0]) == 768
        
    finally:
        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)
        if output_path:
            Path(output_path).unlink(missing_ok=True)


def test_transform_missing_text_column():
    """Test que transform falla sin columna 'text'"""
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
        df = pd.DataFrame({
            'wrong_column': ['data 1', 'data 2']
        })
        df.to_parquet(tmp.name, index=False)
        tmp_path = tmp.name
    
    try:
        transformer = transform_embedding()
        output_path = transformer.transform_data(tmp_path)
        assert output_path is None
    finally:
        Path(tmp_path).unlink(missing_ok=True)

