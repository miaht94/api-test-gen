"""
RAG (Retrieval Augmented Generation) module for document processing and vector storage.
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

import logging

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document representation for RAG storage."""
    id: str
    name: str
    content: str
    type: str  # 'document' or 'code'
    file_extension: str
    size: int
    upload_time: datetime
    processed: bool = False
    metadata: Optional[Dict[str, Any]] = None

class DocumentStore:
    """Simple document storage using SQLite."""
    
    def __init__(self, db_path: str = "documents.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                file_extension TEXT,
                size INTEGER,
                upload_time TEXT,
                processed BOOLEAN DEFAULT FALSE,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_document(self, document: Document) -> bool:
        """Store a document in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (id, name, content, type, file_extension, size, upload_time, processed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document.id,
                document.name,
                document.content,
                document.type,
                document.file_extension,
                document.size,
                document.upload_time.isoformat(),
                document.processed,
                json.dumps(document.metadata) if document.metadata else None
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error storing document: {e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return Document(
                    id=row[0],
                    name=row[1],
                    content=row[2],
                    type=row[3],
                    file_extension=row[4],
                    size=row[5],
                    upload_time=datetime.fromisoformat(row[6]),
                    processed=bool(row[7]),
                    metadata=json.loads(row[8]) if row[8] else None
                )
            return None
        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            return None
    
    def list_documents(self) -> List[Document]:
        """List all documents."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM documents ORDER BY upload_time DESC")
            rows = cursor.fetchall()
            conn.close()
            
            documents = []
            for row in rows:
                documents.append(Document(
                    id=row[0],
                    name=row[1],
                    content=row[2],
                    type=row[3],
                    file_extension=row[4],
                    size=row[5],
                    upload_time=datetime.fromisoformat(row[6]),
                    processed=bool(row[7]),
                    metadata=json.loads(row[8]) if row[8] else None
                ))
            
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    def mark_processed(self, doc_id: str) -> bool:
        """Mark a document as processed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE documents SET processed = TRUE WHERE id = ?", (doc_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error marking document as processed: {e}")
            return False

class VectorStore:
    """Vector storage using ChromaDB."""
    
    def __init__(self, collection_name: str = "api_documents"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.embedder = None
        
        if CHROMADB_AVAILABLE:
            try:
                self.client = chromadb.Client(Settings(anonymized_telemetry=False))
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"description": "API documents and code for test generation"}
                )
            except Exception as e:
                logger.error(f"Error initializing ChromaDB: {e}")
                self.client = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Error loading sentence transformer: {e}")
    
    def is_available(self) -> bool:
        """Check if vector store is available."""
        return self.client is not None and self.embedder is not None
    
    def add_document(self, document: Document, chunk_size: int = 1000) -> bool:
        """Add a document to the vector store."""
        if not self.is_available():
            logger.warning("Vector store not available - missing dependencies")
            return False
        
        try:
            # Split document into chunks
            chunks = self._split_text(document.content, chunk_size)
            
            # Generate embeddings
            embeddings = self.embedder.encode(chunks).tolist()
            
            # Prepare metadata
            metadatas = []
            ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document.id}_chunk_{i}"
                ids.append(chunk_id)
                metadatas.append({
                    "document_id": document.id,
                    "document_name": document.name,
                    "document_type": document.type,
                    "file_extension": document.file_extension,
                    "chunk_index": i,
                    "upload_time": document.upload_time.isoformat()
                })
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        if not self.is_available():
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode([query]).tolist()
            
            # Search
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document from vector store."""
        if not self.is_available():
            return False
        
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
            
            return True
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {e}")
            return False
    
    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
            
            if current_length >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

class RAGManager:
    """Main RAG manager that coordinates document storage and vector operations."""
    
    def __init__(self, db_path: str = "documents.db"):
        self.document_store = DocumentStore(db_path)
        self.vector_store = VectorStore()
    
    def add_document(self, name: str, content: str, doc_type: str, file_extension: str) -> str:
        """Add a new document to both stores."""
        # Generate document ID
        doc_id = hashlib.md5(f"{name}_{content[:100]}_{datetime.now()}".encode()).hexdigest()
        
        # Create document object
        document = Document(
            id=doc_id,
            name=name,
            content=content,
            type=doc_type,
            file_extension=file_extension,
            size=len(content),
            upload_time=datetime.now(),
            processed=False
        )
        
        # Store in document store
        if self.document_store.store_document(document):
            return doc_id
        else:
            raise Exception("Failed to store document")
    
    def process_documents(self) -> Dict[str, Any]:
        """Process all unprocessed documents into vector store."""
        documents = self.document_store.list_documents()
        unprocessed = [doc for doc in documents if not doc.processed]
        
        results = {
            "processed_count": 0,
            "failed_count": 0,
            "errors": []
        }
        
        for doc in unprocessed:
            try:
                if self.vector_store.add_document(doc):
                    self.document_store.mark_processed(doc.id)
                    results["processed_count"] += 1
                else:
                    results["failed_count"] += 1
                    results["errors"].append(f"Failed to process {doc.name}")
            except Exception as e:
                results["failed_count"] += 1
                results["errors"].append(f"Error processing {doc.name}: {str(e)}")
        
        return results
    
    def search_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant context documents."""
        return self.vector_store.search(query, n_results)
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get all documents with their status."""
        documents = self.document_store.list_documents()
        return [
            {
                "id": doc.id,
                "name": doc.name,
                "type": doc.type,
                "size": doc.size,
                "uploaded_at": doc.upload_time.isoformat(),
                "processed": doc.processed
            }
            for doc in documents
        ]
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from both stores."""
        success = True
        
        # Delete from vector store
        if not self.vector_store.delete_document(doc_id):
            success = False
        
        # Delete from document store
        if not self.document_store.delete_document(doc_id):
            success = False
        
        return success
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG system status."""
        documents = self.document_store.list_documents()
        return {
            "total_documents": len(documents),
            "processed_documents": len([doc for doc in documents if doc.processed]),
            "has_processed_documents": any(doc.processed for doc in documents),
            "vector_store_available": self.vector_store.is_available(),
            "dependencies": {
                "chromadb": CHROMADB_AVAILABLE,
                "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE
            }
        }