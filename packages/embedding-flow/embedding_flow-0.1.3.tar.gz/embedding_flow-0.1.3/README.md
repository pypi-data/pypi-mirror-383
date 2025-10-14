# embedding-flow

Biblioteca para transformar chunks de texto en embeddings de 768 dimensiones y cargarlos en Qdrant.

## Instalación

```bash
# Instalación básica (instala torch según tu sistema)
pip install embedding-flow

# O instalar con torch CPU (recomendado si no tenés GPU)
pip install embedding-flow torch --index-url https://download.pytorch.org/whl/cpu
```

## Uso

```python
from embedding_flow import embedding_flow

# Recibe el path del parquet con chunks y carga embeddings a Qdrant
embedding_flow("/path/to/chunks.parquet")
```

## Variables de entorno

```bash
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=embeddings_collection
VECTOR_SIZE=768
```

## Flujo

1. Lee chunks desde parquet
2. Genera embeddings (768 dim) con `all-mpnet-base-v2`
3. Carga embeddings a Qdrant (Docker local)

## Licencia

MIT

