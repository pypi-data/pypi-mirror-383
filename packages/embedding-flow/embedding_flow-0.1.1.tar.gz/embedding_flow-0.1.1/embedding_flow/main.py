from embedding_flow.transform.transform import transform_embedding
from embedding_flow.load.load import load_embedding
import logging

logging.basicConfig(
    level=logging.INFO,              # Nivel mínimo de logs a mostrar
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='appMain.log',             # Opcional: guarda los logs en un archivo
    filemode='a'                    # 'a' append, 'w' overwrite
)


def embedding_flow(parquet_path: str)-> str | None  :
    
    transformer = transform_embedding(parquet_path)
    of = load_embedding(transformer)
    if of is None:
        logging.error("❌ Pipeline failed")
        return None
    else:
        logging.info("✅ Pipeline completed successfully")
        return of