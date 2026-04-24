---
id: embeddings
title: "Text and Image Embeddings with Titan"
description: "Generate embeddings for semantic search, RAG, and similarity matching"
difficulty: intermediate
duration: "15 minutes"
prerequisites:
  - Understanding of text generation
  - Basic knowledge of vectors/embeddings
models:
  - Amazon Titan Multimodal Embeddings G1
apis:
  - bedrock-runtime.invoke_model
---

# Text and Image Embeddings with Titan

This learning path teaches how to generate embeddings for text and images using Amazon Titan Multimodal Embeddings. Embeddings are vector representations that capture semantic meaning, enabling similarity search, RAG systems, and recommendation engines.

## Teaching Flow

### Step 1: Text Embeddings Basics
**Goal:** Generate embeddings for text and understand the output

**What to show:**
- Use Nova 2 Multimodal Embeddings via Converse API
- Generate embedding vectors for text input
- Understand embedding dimensions and normalization

**Code pattern:**
```python
import boto3
import json

client = boto3.client('bedrock-runtime', region_name='REGION')

# Generate embedding for a text query
request_body = {
    "inputText": "What is machine learning?"
}

response = client.invoke_model(
    modelId='amazon.titan-embed-image-v1',
    body=json.dumps(request_body)
)

# Extract embedding from response
result = json.loads(response['body'].read())
embedding = result['embedding']

print(f"Embedding dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

**Key points to emphasize:**
- Titan Multimodal Embeddings returns 1024-dimensional vectors
- Use InvokeModel API (not Converse) for embeddings
- Embeddings capture semantic meaning - similar texts have similar vectors
- Model ID: `amazon.titan-embed-image-v1`

**Common pitfalls:**
- Trying to use Converse API (embeddings use InvokeModel)
- Expecting text output instead of embedding vectors
- Not understanding that embeddings are for downstream tasks, not human-readable

---

### Step 2: Computing Similarity Between Texts
**Goal:** Use embeddings to measure how similar two texts are

**What to show:**
- Generate embeddings for multiple texts
- Calculate cosine similarity between vectors
- Demonstrate semantic similarity vs keyword matching

**Code pattern:**
```python
import numpy as np

def get_embedding(text):
    """Helper to get embedding for a text."""
    response = client.invoke_model(
        modelId='amazon.titan-embed-image-v1',
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response['body'].read())
    return np.array(result['embedding'])

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Compare texts
query = "How do I train a neural network?"
doc1 = "A guide to training deep learning models with backpropagation"
doc2 = "Best restaurants in San Francisco"

query_emb = get_embedding(query)
doc1_emb = get_embedding(doc1)
doc2_emb = get_embedding(doc2)

print(f"Query vs Doc1 similarity: {cosine_similarity(query_emb, doc1_emb):.4f}")
print(f"Query vs Doc2 similarity: {cosine_similarity(query_emb, doc2_emb):.4f}")
```

**Key points to emphasize:**
- Cosine similarity ranges from -1 to 1 (1 = identical, 0 = unrelated, -1 = opposite)
- Embeddings capture meaning beyond keywords
- High similarity = semantically related content
- This is the foundation for semantic search

**Best practices:**
- Normalize embeddings before computing similarity (Nova may already do this)
- Use cosine similarity for high-dimensional vectors
- Consider using libraries like `scipy` or `scikit-learn` for production

---

### Step 3: Building a Simple Semantic Search
**Goal:** Search through documents using embeddings

**What to show:**
- Create embeddings for a document collection
- Find most relevant documents for a query
- Demonstrate ranking by similarity

**Code pattern:**
```python
# Document collection
documents = [
    "Python is a programming language for general-purpose coding",
    "Machine learning enables computers to learn from data",
    "AWS provides cloud computing services and infrastructure",
    "Neural networks are inspired by biological brain structure",
    "Docker containers package applications with their dependencies"
]

# Generate embeddings for all documents
doc_embeddings = [get_embedding(doc) for doc in documents]

# Search query
query = "What is AI and deep learning?"
query_emb = get_embedding(query)

# Calculate similarities
similarities = [cosine_similarity(query_emb, doc_emb) for doc_emb in doc_embeddings]

# Rank documents
ranked_results = sorted(zip(documents, similarities), key=lambda x: x[1], reverse=True)

print("Search results (ranked by relevance):")
for doc, score in ranked_results[:3]:
    print(f"  {score:.4f}: {doc}")
```

**Key points to emphasize:**
- Semantic search finds relevant content even without exact keyword matches
- Pre-compute document embeddings once, reuse for multiple queries
- Ranking by similarity score shows most relevant results first
- This scales to millions of documents with vector databases

**Real-world applications:**
- RAG (Retrieval Augmented Generation) systems
- Document search engines
- Recommendation systems
- Duplicate detection

---

### Step 4: Image and Multimodal Embeddings
**Goal:** Generate embeddings for images and compare cross-modal similarity

**What to show:**
- Embed images using the multimodal model
- Compare text queries to images
- Demonstrate cross-modal retrieval

**Code pattern:**
```python
import base64

# Load and encode an image
with open('product_image.jpg', 'rb') as f:
    image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

# Generate embedding for image
image_request = {
    "inputImage": image_base64
}

image_response = client.invoke_model(
    modelId='amazon.titan-embed-image-v1',
    body=json.dumps(image_request)
)

image_result = json.loads(image_response['body'].read())
image_emb = np.array(image_result['embedding'])

# Compare with text queries
text_queries = [
    "a red sports car",
    "a laptop computer",
    "a mountain landscape"
]

print("Image-to-text similarities:")
for query in text_queries:
    query_emb = get_embedding(query)
    similarity = cosine_similarity(image_emb, query_emb)
    print(f"  '{query}': {similarity:.4f}")
```

**Key points to emphasize:**
- Titan Multimodal Embeddings handles both text and images
- Text and image embeddings live in the same vector space (both 1024-dim)
- Enables cross-modal search (text query → find images)
- Useful for: image search, visual recommendation, multimodal RAG

**Use cases:**
- E-commerce: "Find products that look like this"
- Content moderation: Match images to policy text
- Visual search: Text description → find matching images
- Multimodal RAG: Include images in knowledge retrieval

**Best practices:**
- Use JPEG or PNG format for images
- Preprocess images for consistency (resize, normalize)
- Store embeddings in vector databases for scale (Pinecone, OpenSearch, pgvector)

---

## Summary

By the end of this path, learners should be able to:
- Generate embeddings for text using Titan Multimodal Embeddings
- Calculate similarity between texts using cosine similarity
- Build a simple semantic search system
- Work with image embeddings for multimodal search

## Next Steps
- Integrate with vector databases (OpenSearch, Pinecone)
- Build a RAG system with embeddings + text generation
- Explore advanced retrieval strategies (hybrid search, reranking)

## Technical Notes

**Model ID:** `amazon.titan-embed-image-v1`

**API:** InvokeModel (not Converse)

**Embedding Dimensions:** 1024

**Supported Inputs:**
- Text (up to model's context limit)
- Images (JPEG, PNG)

**Output:** Vector of floats representing semantic meaning

**Cost Considerations:**
- Embeddings are charged per input token/image
- Pre-compute and cache embeddings when possible
- Batch processing for large document collections
