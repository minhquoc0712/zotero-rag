# Zotero RAG Search System

A powerful Retrieval-Augmented Generation (RAG) system for searching and retrieving PDF documents from your Zotero library using semantic similarity and natural language queries.

## Features

- 🔍 **Semantic Search**: Uses sentence transformers for intelligent document retrieval
- 📚 **Zotero Integration**: Automatically extracts metadata from Zotero database
- 🚀 **Fast Indexing**: FAISS-powered similarity search for instant results
- 🌐 **Browser Integration**: Opens relevant PDFs directly in your browser
- 💬 **Interactive Interface**: Command-line interface with search suggestions
- 🏷️ **Rich Metadata**: Searches through titles, authors, abstracts, and content
- 💾 **Persistent Index**: Save and load search indices for faster startup

## Installation

### From PyPI (Recommended)

```bash
pip install zotero-rag
```

### With GPU Support (Optional)

For faster embedding generation on CUDA-compatible GPUs:

```bash
pip install zotero-rag[gpu]
```

### Development Installation

```bash
git clone https://github.com/yourusername/zotero-rag.git
cd zotero-rag
pip install -e .[dev]
```

## Quick Start

1. **Build the search index** (first time only):
   ```bash
   zotero-rag --build-index
   ```

2. **Search your library**:
   ```bash
   zotero-rag --query "machine learning transformers"
   ```

3. **Interactive mode**:
   ```bash
   zotero-rag
   ```

## Usage Examples

### Command Line Interface

```bash
# Build index and start interactive search
zotero-rag --build-index

# Direct search from command line
zotero-rag --query "deep learning ICLR 2023"

# Specify custom Zotero directory
zotero-rag --zotero-dir "/path/to/zotero" --build-index

# Save index for faster subsequent runs
zotero-rag --build-index --save-index my_library.json

# Load existing index
zotero-rag --load-index my_library.json --query "neural networks"
```

### Interactive Mode

When you run `zotero-rag` without arguments, you get an interactive interface:

```
=== Zotero RAG Search System ===
Enter your search query (or 'quit' to exit)
Example: 'Proba Unlearn ICLR'

Search query: attention mechanisms transformers

Found 5 results:
------------------------------------------------------------
1. [0.847] Attention Is All You Need
   Author: Vaswani et al.
   Year: 2017
   Journal: NIPS
   File: attention_is_all_you_need.pdf

2. [0.783] BERT: Pre-training of Deep Bidirectional Transformers
   Author: Devlin et al.
   Year: 2019
   Journal: NAACL
   File: bert_pretraining.pdf

Enter number to open (or press Enter to search again): 1
```

### Python API

```python
from zotero_rag import ZoteroRAG

# Initialize the system
rag = ZoteroRAG()

# Build index
rag.build_index()

# Search
results = rag.search("quantum computing", top_k=5)

# Open best match
if results:
    rag.open_pdf(results[0][0]['path'])
```

## Configuration

### Zotero Directory Detection

The system automatically detects your Zotero directory on:
- **Windows**: `~/Zotero` or `~/AppData/Roaming/Zotero/`
- **macOS**: `~/Zotero` or `~/Library/Application Support/Zotero/`
- **Linux**: `~/Zotero` or `~/.zotero/`

You can override this with `--zotero-dir /custom/path`.

### Search Index Management

```bash
# Build and save index
zotero-rag --build-index --save-index ~/my_zotero_index.json

# Load existing index (much faster)
zotero-rag --load-index ~/my_zotero_index.json

# Update index with new papers
zotero-rag --build-index --save-index ~/my_zotero_index.json
```

## How It Works

1. **Discovery**: Scans your Zotero storage directory for PDF files
2. **Metadata Extraction**: Reads bibliographic data from Zotero's SQLite database
3. **Content Extraction**: Extracts text from PDF files using PyPDF2
4. **Embedding Generation**: Creates semantic embeddings using sentence transformers
5. **Index Building**: Builds a FAISS index for fast similarity search
6. **Query Processing**: Converts your search query to embeddings
7. **Retrieval**: Finds most similar documents using cosine similarity
8. **Presentation**: Ranks and displays results with metadata

## Performance Tips

- **First run**: Building the index takes time (5-10 minutes for 1000+ papers)
- **Subsequent runs**: Load saved indices for instant startup
- **GPU acceleration**: Install with `[gpu]` extra for faster embedding generation
- **Memory usage**: ~1-2GB RAM for moderate libraries (500-1000 papers)

## Supported File Types

- **PDF files**: Primary support with text extraction
- **Metadata**: Title, authors, journal, year, abstract, DOI, tags
- **Zotero database**: SQLite-based metadata extraction

## Troubleshooting

### Common Issues

1. **"Zotero directory not found"**
   ```bash
   zotero-rag --zotero-dir "/path/to/your/zotero/directory"
   ```

2. **"No PDF files found"**
   - Check that your Zotero library has PDF attachments
   - Verify the storage directory exists: `{zotero-dir}/storage/`

3. **"Database not found"**
   - Ensure Zotero is closed when running the indexer
   - Check for `zotero.sqlite` in your Zotero directory

4. **Memory issues with large libraries**
   - Process PDFs in batches
   - Use `--save-index` to avoid rebuilding

### Debug Mode

```bash
# Enable verbose output
zotero-rag --build-index --verbose

# Check detected paths
zotero-rag --info
```

## Requirements

- Python 3.8+
- 2GB+ RAM recommended
- 1GB+ free disk space for indices
- Internet connection (first run only, for downloading models)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{zotero_rag,
  title={Zotero RAG Search System},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/zotero-rag}
}
```

## Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) for semantic embeddings
- [FAISS](https://faiss.ai/) for efficient similarity search
- [Zotero](https://www.zotero.org/) for reference management
- The open-source community for making this possible

## Support

- 📖 [Documentation](https://github.com/yourusername/zotero-rag#readme)
- 🐛 [Issue Tracker](https://github.com/yourusername/zotero-rag/issues)
- 💬 [Discussions](https://github.com/yourusername/zotero-rag/discussions)
