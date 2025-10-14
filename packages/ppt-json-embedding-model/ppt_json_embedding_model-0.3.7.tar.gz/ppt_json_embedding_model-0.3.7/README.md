## Custom JSON Embedding Model (from scratch)

A from-scratch character-CNN encoder trained with a contrastive objective to embed JSON records (devices, tickets, customers) into dense vectors for vector stores.

### Features
- Char-level tokenizer (no external models)
- Multi-kernel 1D CNN + max-pooling
- Projection head to target dimension
- NT-Xent (InfoNCE) contrastive training with simple JSON augmentations
- JSON flattening utilities and CLI tools
- Conversation role tokens to structure prompts/responses

**[Model Card](MODEL_CARD.md)** - Detailed model documentation, limitations, and usage guidelines

### Installation

#### For Team Members (Recommended)

```bash
# Install directly from GitHub (requires access to the repo)
pip install git+https://github.com/PPT-ProdEng-Sandbox/ppt-json-embedding-model.git

# Or install a specific version/tag
pip install git+https://github.com/PPT-ProdEng-Sandbox/ppt-json-embedding-model.git@v0.1.5

# For development (editable install)
git clone https://github.com/PPT-ProdEng-Sandbox/ppt-json-embedding-model.git
cd ppt-json-embedding-model
pip install -e .
```

#### Using Pre-trained Model

**Auto-download (Recommended):**
```bash
# The model auto-downloads on first use - no manual download needed!
json-embed --input your-data.jsonl --output embeddings.npy

# Or search with auto-download
json-embed-search --pairs data.jsonl=embeddings.npy --query "find records" --topk 5
```

**GitHub Authentication (For Private Repositories):**

If you encounter 404 errors when downloading model weights, you may need to set up GitHub authentication:

```bash
# Set your GitHub Personal Access Token (PAT)
export GITHUB_TOKEN=your_personal_access_token

# Or alternatively
export GITHUB_PAT=your_personal_access_token

# Then run the commands as usual
json-embed --input your-data.jsonl --output embeddings.npy
```

To create a Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with `repo` scope for private repositories
3. Copy the token and set it as an environment variable

**Manual download (Optional):**
```bash
# Download the pre-trained model (model weights v0.1.4)
curl -L -o model.pt https://github.com/PPT-ProdEng-Sandbox/ppt-json-embedding-model/releases/download/v0.1.4/ppt-json-embedding-model-v0.1.4.pt

# Generate embeddings using downloaded model
json-embed --model model.pt --input your-data.jsonl --output embeddings.npy
```

#### Alternative: Local Development

```bash
# create venv (recommended)
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# or install as package
pip install -e .

# Train
json-embed-train --config config/default.yaml --data devices.jsonl tickets.jsonl customers.jsonl --out runs/exp1

# Embed (streaming, avoids OOM) - using trained model
json-embed --checkpoint runs/exp1/last.pt --input data/records.jsonl --output runs/exp1/records.npy --config config/default.yaml --batch-size 64 --limit 5000

# Embed using auto-downloaded pre-trained model
json-embed --input data/records.jsonl --output records.npy --batch-size 64

# Local search (cosine) across one or more JSONL=NPY pairs - with auto-download
json-embed-search --pairs data/records.jsonl=records.npy --query "find related records" --topk 5

# Prefilter exact fields before cosine (AND). Example: SerialNumber filter
json-embed-search --pairs data/qa-tickets_from_xlsx.fixed.jsonl=records.npy \
  --where SerialNumber=APM00111003159 --query "Find tickets for this serial" --topk 5
```

### Python API for Applications

For integrating into applications and agents, use the high-level Python API:

```python
from embedding_model import JSONEmbeddingModel

# Initialize model (set JSON_EMBED_MODEL_PATH environment variable)
model = JSONEmbeddingModel("path/to/your/model.pt")

# Embed documents
documents = [
    {"title": "Product A", "description": "High-quality widget", "price": 299},
    {"title": "Service B", "description": "Professional installation", "price": 199}
]
embeddings = model.embed_documents(documents)

# Search documents
results = model.search(
    query="affordable installation service", 
    documents=documents, 
    embeddings=embeddings,
    top_k=5
)

for similarity, idx, doc in results:
    print(f"Score: {similarity:.3f} | {doc['title']}")
```

**Convenience functions for quick usage:**
```python
from embedding_model import search_documents

results = search_documents(
    query="your search query",
    documents=your_json_documents,
    model_path="path/to/model.pt",
    top_k=5
)
```

See `examples/python_api_example.py` for complete usage examples.

### Benchmarking

Evaluate model performance with the benchmarking suite:

```bash
# Install benchmark dependencies
pip install -e ".[benchmark]"

# Run quick benchmark
python benchmarks/run_benchmarks.py --type quick

# Run comprehensive benchmark
python benchmarks/run_benchmarks.py --type comprehensive --model-path path/to/model.pt --data-dir data/
```

See `benchmarks/README.md` for detailed benchmarking documentation.

### Data Format
- JSONL files containing one record per line.
- Records can be any JSON structure; flattening will convert to text.
- Example: `{"title": "Product A", "description": "High-quality widget", "price": 299}`

### Notes
- Steps per epoch ≈ ceil(total_records / batch_size). Use `max_steps` in config to cap.
- CPU-only runs are slower; consider reducing `max_chars`, `batch_size`, or `conv_channels`.
- Use the cleaned `.fixed.jsonl` you trained on when embedding for consistency.

### License
This project is licensed under the MIT License - see the `LICENSE` file for details.
