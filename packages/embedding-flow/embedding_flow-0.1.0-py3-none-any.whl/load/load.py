from contracts.contracts import load_data
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import pandas as pd
import logging
import os
from typing import List
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class load_embedding(load_data):
    def __init__(self):
        """Inicializa el cliente de Qdrant"""
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        self.collection_name = os.getenv("QDRANT_COLLECTION", "embeddings_collection")
        self.vector_size = int(os.getenv("VECTOR_SIZE", "768"))
        
        # Inicializar cliente
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )
        
        # Crear colección si no existe
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Crea la colección en Qdrant si no existe"""
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(col.name == self.collection_name for col in collections)
            
            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Colección '{self.collection_name}' creada en Qdrant")
            else:
                logger.info(f"ℹ️ Colección '{self.collection_name}' ya existe")
        except Exception as e:
            logger.error(f"❌ Error al verificar/crear colección: {e}", exc_info=True)
            raise
    
    def load_data(self, parquet_path: str) -> bool:
        """
        Carga los embeddings desde un parquet a Qdrant
        
        Args:
            parquet_path: Ruta al archivo parquet con embeddings
            
        Returns:
            True si la carga fue exitosa, False si falló
        """
        try:
            # Leer parquet
            df = pd.read_parquet(parquet_path)
            
            if "embedding" not in df.columns:
                raise ValueError(f"El parquet {parquet_path} no contiene columna 'embedding'")
            
            # Preparar puntos para Qdrant
            points: List[PointStruct] = []
            
            for idx, row in df.iterrows():
                # Generar ID único
                point_id = str(uuid.uuid4())
                
                # Preparar payload (todos los campos excepto embedding)
                payload = {col: row[col] for col in df.columns if col != "embedding"}
                
                # Crear punto
                point = PointStruct(
                    id=point_id,
                    vector=row["embedding"],
                    payload=payload
                )
                points.append(point)
            
            # Insertar en Qdrant (en batch)
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ {len(points)} embeddings cargados a Qdrant desde {parquet_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al cargar embeddings a Qdrant desde {parquet_path}: {e}", exc_info=True)
            return False