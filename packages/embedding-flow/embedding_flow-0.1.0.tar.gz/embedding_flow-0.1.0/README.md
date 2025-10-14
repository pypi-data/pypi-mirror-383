# embedding-flow

Pipeline for transforming text chunks into 768-dimensional embeddings and loading to Qdrant.

## Installation

```bash
pip install embedding-flow
```

## Usage

```python
from transform.transform import transform_embedding
from load.load import load_embedding

# Transform
transformer = transform_embedding()
output_path = transformer.transform_data("chunks.parquet")

# Load to Qdrant
loader = load_embedding()
loader.load_data(output_path)
```

## Environment Variables

```bash
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=embeddings_collection
VECTOR_SIZE=768
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```

