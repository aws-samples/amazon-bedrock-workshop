---
id: rag
title: "RAG with Bedrock Knowledge Bases"
description: "Build retrieval-augmented generation systems using Bedrock APIs"
difficulty: intermediate
duration: "20 minutes"
prerequisites:
  - Understanding of text generation
  - Familiarity with embeddings (recommended)
  - Knowledge Base created in Bedrock console
models:
  - Any Claude model for generation
apis:
  - bedrock-agent-runtime.retrieve
  - bedrock-agent-runtime.retrieve_and_generate
---

# RAG with Bedrock Knowledge Bases

This learning path teaches how to build Retrieval-Augmented Generation (RAG) systems using Bedrock Knowledge Bases. RAG combines retrieval of relevant documents with LLM generation for grounded, factual responses.

## Teaching Flow

### Step 1: Understanding the RetrieveAndGenerate API
**Goal:** Use the simplest RAG API to query a knowledge base

**What to show:**
- The RetrieveAndGenerate API combines retrieval + generation in one call
- Requires a Knowledge Base ID (created in Bedrock console)
- Returns generated answer with source citations

**Code pattern:**
```python
import boto3
import json

client = boto3.client('bedrock-agent-runtime', region_name='REGION')

# Simple RAG query
response = client.retrieve_and_generate(
    input={
        'text': 'What are the key features of Amazon S3?'
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'YOUR_KB_ID',  # Get from Bedrock console
            'modelArn': 'arn:aws:bedrock:REGION::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0'
        }
    }
)

# Extract answer and citations
answer = response['output']['text']
citations = response.get('citations', [])

print(f"Answer: {answer}\n")
print(f"Number of citations: {len(citations)}")
for i, citation in enumerate(citations, 1):
    print(f"\nCitation {i}:")
    for ref in citation.get('retrievedReferences', []):
        print(f"  - {ref.get('location', {}).get('s3Location', {}).get('uri', 'N/A')}")
```

**Key points to emphasize:**
- RetrieveAndGenerate is the easiest RAG API - one call does everything
- Automatically retrieves relevant chunks and generates an answer
- Returns citations showing which sources were used
- Knowledge Base must exist before using this API

**Prerequisites:**
- Create a Knowledge Base in Bedrock console (S3 data source)
- Note the Knowledge Base ID
- Wait for data source sync to complete

**Common pitfalls:**
- Using a Knowledge Base that hasn't finished syncing
- Not handling empty citations (no relevant docs found)
- Forgetting to use the full model ARN (not just model ID)

---

### Step 2: Separate Retrieval for Fine Control
**Goal:** Use the Retrieve API separately to inspect retrieved documents

**What to show:**
- Retrieve API gives you the raw retrieved chunks
- Inspect what documents were found before generation
- Useful for debugging, filtering, or custom ranking

**Code pattern:**
```python
# Retrieve documents only (no generation)
retrieve_response = client.retrieve(
    knowledgeBaseId='YOUR_KB_ID',
    retrievalQuery={
        'text': 'How do I configure S3 bucket versioning?'
    },
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 5  # How many chunks to retrieve
        }
    }
)

# Inspect retrieved documents
results = retrieve_response['retrievalResults']

print(f"Retrieved {len(results)} documents:\n")
for i, result in enumerate(results, 1):
    score = result.get('score', 0)
    content = result.get('content', {}).get('text', '')
    location = result.get('location', {}).get('s3Location', {}).get('uri', 'N/A')
    
    print(f"{i}. Score: {score:.4f}")
    print(f"   Source: {location}")
    print(f"   Preview: {content[:200]}...")
    print()
```

**Key points to emphasize:**
- Retrieve API only gets documents, doesn't generate answers
- Returns relevance scores for each chunk
- Use this when you want to:
  - Inspect what documents were retrieved
  - Filter or rerank results before generation
  - Build custom RAG logic
  - Debug why certain answers are produced

**Best practices:**
- Start with 5-10 results for most queries
- Check relevance scores - low scores may indicate poor matches
- Use numberOfResults to balance quality vs context length

---

### Step 3: Adding Filters and Metadata
**Goal:** Use metadata filters to scope retrieval to specific documents

**What to show:**
- Add metadata when indexing documents (e.g., department, date, category)
- Filter retrieval by metadata at query time
- Combine semantic search with structured filters

**Code pattern:**
```python
# Retrieve with metadata filter
filtered_response = client.retrieve(
    knowledgeBaseId='YOUR_KB_ID',
    retrievalQuery={
        'text': 'Security best practices'
    },
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 5,
            'filter': {
                'equals': {
                    'key': 'department',
                    'value': 'security'
                }
            }
        }
    }
)

# Can also use AND, OR, NOT filters
complex_filter = {
    'andAll': [
        {
            'equals': {
                'key': 'category',
                'value': 'documentation'
            }
        },
        {
            'greaterThan': {
                'key': 'year',
                'value': 2023
            }
        }
    ]
}
```

**Key points to emphasize:**
- Metadata is set when creating the Knowledge Base data source
- Filters narrow search to specific subsets of documents
- Combine semantic search (embeddings) with structured filters (metadata)
- Filter types: equals, notEquals, greaterThan, lessThan, in, notIn, and, or, not

**Use cases:**
- Multi-tenant systems (filter by customer_id)
- Time-based retrieval (only recent documents)
- Department-specific knowledge (filter by department)
- Document type filtering (policies vs guides vs FAQs)

---

### Step 4: Streaming RAG Responses
**Goal:** Stream generated answers for better UX

**What to show:**
- Use retrieve_and_generate_stream for progressive display
- Handle streaming events to show partial answers
- Maintain citations in streamed responses

**Code pattern:**
```python
# Stream RAG response
stream_response = client.retrieve_and_generate_stream(
    input={
        'text': 'Explain how S3 encryption works'
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'YOUR_KB_ID',
            'modelArn': 'arn:aws:bedrock:REGION::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0'
        }
    }
)

# Process streaming events
print("Streaming answer: ", end='', flush=True)
full_answer = ""
citations = []

for event in stream_response['stream']:
    if 'chunk' in event:
        chunk = event['chunk']
        if 'bytes' in chunk:
            text = chunk['bytes'].decode('utf-8')
            print(text, end='', flush=True)
            full_answer += text
    
    elif 'citations' in event:
        citations = event['citations']

print(f"\n\nCitations ({len(citations)}):")
for citation in citations:
    for ref in citation.get('retrievedReferences', []):
        print(f"  - {ref.get('location', {}).get('s3Location', {}).get('uri', 'N/A')}")
```

**Key points to emphasize:**
- Streaming shows partial answers as they're generated (better UX)
- Events arrive in chunks - decode and display progressively
- Citations come at the end of the stream
- Use this for chatbots and interactive applications

**Best practices:**
- Always flush output when streaming to display immediately
- Handle streaming events gracefully (check event types)
- Display citations after full answer is complete

---

### Step 5: Guardrails with RAG
**Goal:** Add content safety and quality filters to RAG responses

**What to show:**
- Configure Guardrails to filter harmful content
- Validate RAG answers meet quality standards
- Handle guardrail interventions gracefully

**Code pattern:**
```python
# RAG with guardrails
response = client.retrieve_and_generate(
    input={
        'text': 'Tell me about data security policies'
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'YOUR_KB_ID',
            'modelArn': 'arn:aws:bedrock:REGION::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0',
            'generationConfiguration': {
                'guardrailConfiguration': {
                    'guardrailId': 'YOUR_GUARDRAIL_ID',
                    'guardrailVersion': 'DRAFT'
                }
            }
        }
    }
)

# Check if guardrail intervened
if 'guardrailAction' in response:
    action = response['guardrailAction']
    if action == 'BLOCKED':
        print("Response blocked by guardrail")
        # Handle blocked content
    elif action == 'INTERVENED':
        print("Response modified by guardrail")

print(response['output']['text'])
```

**Key points to emphasize:**
- Guardrails filter harmful content, PII, hallucinations
- Create guardrails in Bedrock console
- BLOCKED = response stopped, INTERVENED = modified
- Use guardrails for: content safety, regulatory compliance, quality control

**Use cases:**
- Filter PII from customer support responses
- Block harmful or inappropriate content
- Ensure answers stay on-topic
- Validate factual grounding

---

## Summary

By the end of this path, learners should be able to:
- Use RetrieveAndGenerate for simple RAG queries
- Retrieve documents separately for inspection and custom logic
- Filter retrieval with metadata for scoped search
- Stream RAG responses for better UX
- Add guardrails for content safety and quality

## Next Steps
- Create custom chunking strategies in Knowledge Bases
- Implement hybrid search (semantic + keyword)
- Build conversation history into RAG queries
- Explore Agents for multi-step RAG workflows

## Technical Notes

**APIs Used:**
- `bedrock-agent-runtime.retrieve` - Get relevant documents only
- `bedrock-agent-runtime.retrieve_and_generate` - Retrieve + generate in one call
- `bedrock-agent-runtime.retrieve_and_generate_stream` - Streaming RAG

**Prerequisites:**
- Knowledge Base created in Bedrock console
- Data source (S3, Web Crawler, etc.) synced
- Knowledge Base ID noted

**Supported Models:**
- Any Claude model (Sonnet, Haiku, Opus)
- Use full ARN format: `arn:aws:bedrock:REGION::foundation-model/MODEL_ID`

**Retrieval Configuration:**
- numberOfResults: 1-100 (default: 5)
- Metadata filters: equals, in, greaterThan, etc.
- Vector search is automatic (embeddings handled by KB)

**Cost Considerations:**
- Charged per retrieval query + generation tokens
- More numberOfResults = more context = higher cost
- Streaming has same cost as non-streaming
