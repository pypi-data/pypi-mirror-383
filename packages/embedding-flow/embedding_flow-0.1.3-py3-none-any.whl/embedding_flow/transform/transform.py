from embedding_flow.contracts.contracts import transform_data
from pathlib import Path
import pandas as pd
from sentence_transformers import SentenceTransformer
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class transform_embedding(transform_data):
    def transform_data(self, parquet_path: str) -> Optional[str]:
        try:
            # Cargar datos del parquet
            df = pd.read_parquet(parquet_path)
            if "text" not in df.columns:
                raise ValueError("El parquet no contiene una columna 'text' para generar embeddings.")

            # Inicializar modelo con embeddings de 768 dimensiones
            model = SentenceTransformer("all-mpnet-base-v2")

            # Generar embeddings
            embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)
            df["embedding"] = embeddings.tolist()  # guardar como lista

            # Guardar parquet procesado
            output_dir = Path("datos_embeddings")
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / Path(parquet_path).name
            df.to_parquet(output_file, index=False)

            logger.info(f"✅ Embeddings (768 dim) generados y guardados en: {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"❌ Error al transformar en embeddings {parquet_path}: {e}", exc_info=True)
            return None
