#!/usr/bin/env python3
"""
Zotero RAG (Retrieval-Augmented Generation) System
Searches PDF files and metadata in Zotero library based on user queries
"""

import os
import json
import sqlite3
import webbrowser
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse

# Install required packages:
# pip install sentence-transformers faiss-cpu PyPDF2 scikit-learn

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import PyPDF2
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install with: pip install sentence-transformers faiss-cpu PyPDF2 scikit-learn")
    exit(1)


class ZoteroRAG:
    def __init__(self, zotero_dir: str = None, use_gpu: bool = False):
        """Initialize the Zotero RAG system."""
        self.zotero_dir = self._find_zotero_directory(zotero_dir)
        self.storage_dir = os.path.join(self.zotero_dir, "storage")
        self.db_path = os.path.join(self.zotero_dir, "zotero.sqlite")
        self.use_gpu = use_gpu
        
        # Initialize embedding model
        print("Loading sentence transformer model...")
        device = 'cuda' if hasattr(self, 'use_gpu') and self.use_gpu else 'cpu'
        self.model = SentenceTransformer('intfloat/e5-large-v2', device=device)
        
        # Storage for documents and embeddings
        self.documents = []
        self.embeddings = None
        self.faiss_index = None
        
        print(f"Zotero directory: {self.zotero_dir}")
        print(f"Storage directory: {self.storage_dir}")

    def _find_zotero_directory(self, custom_dir: str = None) -> str:
        """Find Zotero data directory."""
        if custom_dir and os.path.exists(custom_dir):
            return custom_dir
            
        # Common Zotero locations
        possible_paths = [
            # Windows
            os.path.expanduser("~/Zotero"),
            os.path.expanduser("~/AppData/Roaming/Zotero/Zotero/Profiles/"),
            # macOS
            os.path.expanduser("~/Zotero"),
            os.path.expanduser("~/Library/Application Support/Zotero/Profiles/"),
            # Linux
            os.path.expanduser("~/Zotero"),
            os.path.expanduser("~/.zotero/zotero/"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # For profile directories, find the actual profile
                if "Profiles" in path:
                    try:
                        profiles = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
                        if profiles:
                            return os.path.join(path, profiles[0])
                    except:
                        continue
                else:
                    return path
        
        raise FileNotFoundError("Could not find Zotero directory. Please specify it manually.")

    def extract_zotero_metadata(self) -> Dict[str, Dict]:
        """Extract metadata from Zotero database."""
        if not os.path.exists(self.db_path):
            print("Warning: Zotero database not found. Proceeding without metadata.")
            return {}
            
        metadata = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query to get item metadata with attachments
            query = """
            SELECT 
                items.key,
                itemAttachments.path,
                itemData.valueID,
                fields.fieldName,
                itemDataValues.value
            FROM items
            LEFT JOIN itemAttachments ON items.itemID = itemAttachments.parentItemID
            LEFT JOIN itemData ON items.itemID = itemData.itemID
            LEFT JOIN fields ON itemData.fieldID = fields.fieldID
            LEFT JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
            WHERE itemAttachments.path IS NOT NULL
            AND itemAttachments.path LIKE '%.pdf'
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                key, path, value_id, field_name, value = row
                if key and path:
                    if key not in metadata:
                        metadata[key] = {'path': path, 'fields': {}}
                    if field_name and value:
                        metadata[key]['fields'][field_name] = value
            
            conn.close()
            print(f"Extracted metadata for {len(metadata)} items")
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            
        return metadata

    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def find_pdf_files(self) -> List[Dict]:
        """Find all PDF files in Zotero storage directory."""
        pdf_files = []
        metadata = self.extract_zotero_metadata()
        
        if not os.path.exists(self.storage_dir):
            print(f"Storage directory not found: {self.storage_dir}")
            return pdf_files
            
        print("Scanning for PDF files...")
        for root, dirs, files in os.walk(self.storage_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    folder_name = os.path.basename(root)
                    
                    # Try to match with metadata
                    doc_metadata = {}
                    for key, meta in metadata.items():
                        if key in root or folder_name == key:
                            doc_metadata = meta.get('fields', {})
                            break
                    
                    pdf_info = {
                        'path': file_path,
                        'filename': file,
                        'folder': folder_name,
                        'title': doc_metadata.get('title', file),
                        'author': doc_metadata.get('firstCreator', ''),
                        'year': doc_metadata.get('date', ''),
                        'journal': doc_metadata.get('publicationTitle', ''),
                        'abstract': doc_metadata.get('abstractNote', ''),
                        'tags': doc_metadata.get('extra', ''),
                        'url': doc_metadata.get('url', ''),
                        'doi': doc_metadata.get('DOI', ''),
                    }
                    
                    pdf_files.append(pdf_info)
        
        print(f"Found {len(pdf_files)} PDF files")
        return pdf_files

    def build_search_corpus(self, pdf_files: List[Dict]) -> List[str]:
        """Build searchable text corpus from PDF metadata and content."""
        corpus = []
        
        print("Building search corpus...")
        for i, pdf_info in enumerate(pdf_files):
            if i % 10 == 0:
                print(f"Processing {i+1}/{len(pdf_files)} files...")
                
            # Combine metadata for searching
            search_text_parts = [
                pdf_info.get('title', ''),
                pdf_info.get('author', ''),
                pdf_info.get('journal', ''),
                pdf_info.get('abstract', ''),
                pdf_info.get('tags', ''),
                pdf_info.get('filename', ''),
            ]
            
            # Extract some PDF text (first few pages for performance)
            try:
                pdf_text = self.extract_pdf_text(pdf_info['path'])
                # Take first 2000 characters to avoid memory issues
                if pdf_text:
                    search_text_parts.append(pdf_text[:2000])
            except:
                pass
            
            search_text = ' '.join(filter(None, search_text_parts))
            corpus.append(search_text)
            
        return corpus

    def build_index(self):
        """Build FAISS index for similarity search."""
        print("Finding PDF files...")
        self.documents = self.find_pdf_files()
        
        if not self.documents:
            print("No PDF files found!")
            return
            
        print("Building search corpus...")
        corpus = self.build_search_corpus(self.documents)
        
        print("Generating embeddings...")
        embeddings = self.model.encode(corpus, show_progress_bar=True)
        
        # Build FAISS index
        print("Building FAISS index...")
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.faiss_index.add(embeddings.astype('float32'))
        
        self.embeddings = embeddings
        print(f"Index built with {len(self.documents)} documents")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Search for relevant documents."""
        if self.faiss_index is None:
            print("Index not built. Please run build_index() first.")
            return []
            
        print(f"Searching for: '{query}'")
        
        # Encode query
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
                
        return results

    def open_pdf(self, pdf_path: str):
        """Open PDF file in default browser/viewer."""
        try:
            # Convert to file URL for browser
            file_url = f"file://{os.path.abspath(pdf_path)}"
            webbrowser.open(file_url)
            print(f"Opened: {pdf_path}")
        except Exception as e:
            print(f"Error opening file: {e}")

    def interactive_search(self):
        """Interactive search interface."""
        print("\n=== Zotero RAG Search System ===")
        print("Enter your search query (or 'quit' to exit)")
        print("Example: 'Proba Unlearn ICLR'")
        print("-" * 40)
        
        while True:
            query = input("\nSearch query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query:
                continue
                
            results = self.search(query, top_k=5)
            
            if not results:
                print("No results found.")
                continue
                
            print(f"\nFound {len(results)} results:")
            print("-" * 60)
            
            for i, (doc, score) in enumerate(results, 1):
                print(f"{i}. [{score:.3f}] {doc['title']}")
                if doc['author']:
                    print(f"   Author: {doc['author']}")
                if doc['year']:
                    print(f"   Year: {doc['year']}")
                if doc['journal']:
                    print(f"   Journal: {doc['journal']}")
                print(f"   File: {doc['filename']}")
                print()
            
            # Ask user which file to open
            try:
                choice = input("Enter number to open (or press Enter to search again): ").strip()
                if choice and choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        self.open_pdf(results[idx][0]['path'])
                    else:
                        print("Invalid selection.")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    def save_index(self, index_path: str = "zotero_index.json"):
        """Save the built index to disk."""
        if not self.documents:
            print("No index to save.")
            return
            
        data = {
            'documents': self.documents,
            'zotero_dir': self.zotero_dir
        }
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Save FAISS index
        if self.faiss_index:
            faiss.write_index(self.faiss_index, index_path.replace('.json', '.faiss'))
            
        print(f"Index saved to {index_path}")

    def load_index(self, index_path: str = "zotero_index.json"):
        """Load a previously saved index."""
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.documents = data['documents']
            
            # Load FAISS index
            faiss_path = index_path.replace('.json', '.faiss')
            if os.path.exists(faiss_path):
                self.faiss_index = faiss.read_index(faiss_path)
                
            print(f"Index loaded from {index_path}")
            print(f"Loaded {len(self.documents)} documents")
            
        except Exception as e:
            print(f"Error loading index: {e}")


def main():
    parser = argparse.ArgumentParser(description="Zotero RAG Search System")
    parser.add_argument("--zotero-dir", help="Path to Zotero data directory")
    parser.add_argument("--build-index", action="store_true", help="Build search index")
    parser.add_argument("--load-index", help="Load existing index file")
    parser.add_argument("--save-index", help="Save index to file")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration for embeddings")
    
    args = parser.parse_args()
    
    try:
        # Initialize system
        rag = ZoteroRAG(args.zotero_dir, args.gpu)
        
        # Load or build index
        if args.load_index and os.path.exists(args.load_index):
            rag.load_index(args.load_index)
        else:
            print("Building index (this may take a while)...")
            rag.build_index()
            
        # Save index if requested
        if args.save_index:
            rag.save_index(args.save_index)
            
        # Handle query or start interactive mode
        if args.query:
            results = rag.search(args.query)
            if results:
                print(f"Best match: {results[0][0]['title']}")
                rag.open_pdf(results[0][0]['path'])
            else:
                print("No results found.")
        else:
            rag.interactive_search()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
