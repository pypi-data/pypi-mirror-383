import pytest
import pandas as pd
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch
from load.load import load_embedding


@patch('load.load.QdrantClient')
def test_load_with_embeddings(mock_qdrant_client):
    """Test que load carga correctamente embeddings de 768 dims"""
    # Mock del cliente
    mock_client = MagicMock()
    mock_qdrant_client.return_value = mock_client
    mock_client.get_collections.return_value.collections = []
    
    # Crear parquet con embeddings de 768 dims
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
        df = pd.DataFrame({
            'text': ['test 1', 'test 2'],
            'embedding': [np.random.rand(768).tolist(), np.random.rand(768).tolist()]
        })
        df.to_parquet(tmp.name, index=False)
        tmp_path = tmp.name
    
    try:
        loader = load_embedding()
        success = loader.load_data(tmp_path)
        
        assert success is True
        mock_client.upsert.assert_called_once()
        
        # Verificar que se llamó con 2 puntos
        call_args = mock_client.upsert.call_args
        points = call_args.kwargs['points']
        assert len(points) == 2
        
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@patch('load.load.QdrantClient')
def test_load_without_embeddings(mock_qdrant_client):
    """Test que load falla sin columna 'embedding'"""
    mock_client = MagicMock()
    mock_qdrant_client.return_value = mock_client
    mock_client.get_collections.return_value.collections = []
    
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
        df = pd.DataFrame({
            'text': ['test 1', 'test 2']
        })
        df.to_parquet(tmp.name, index=False)
        tmp_path = tmp.name
    
    try:
        loader = load_embedding()
        success = loader.load_data(tmp_path)
        assert success is False
    finally:
        Path(tmp_path).unlink(missing_ok=True)

