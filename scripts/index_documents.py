import os
from pathlib import Path
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    VectorSearchAlgorithmKind
)
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("OPENAI_KEY")
INDEX_NAME = "openshift-docs"
DOCS_FOLDER = "sample-docs"

# Initialize clients
search_index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=AzureKeyCredential(SEARCH_KEY)
)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)

openai_client = AzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_KEY,
    api_version="2024-02-01"
)

def create_index():
    """Create the search index with vector search capabilities"""
    
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="vector-profile"
        ),
        SimpleField(name="filepath", type=SearchFieldDataType.String)
    ]
    
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )
    
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search
    )
    
    try:
        search_index_client.delete_index(INDEX_NAME)
        print(f"Deleted existing index: {INDEX_NAME}")
    except:
        pass
    
    search_index_client.create_index(index)
    print(f"Created index: {INDEX_NAME}")

def get_embedding(text):
    """Generate embedding vector for text"""
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def index_documents():
    """Read documents from folder and index them"""
    
    docs_path = Path(DOCS_FOLDER)
    documents = []
    
    for file_path in docs_path.glob("*.md"):
        print(f"Processing: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from first heading or use filename
        title = file_path.stem.replace('-', ' ').title()
        if content.startswith('#'):
            title = content.split('\n')[0].replace('#', '').strip()
        
        # Generate embedding
        embedding = get_embedding(content)
        
        doc = {
            "id": file_path.stem,
            "title": title,
            "content": content,
            "content_vector": embedding,
            "filepath": str(file_path)
        }
        
        documents.append(doc)
    
    # Upload to search index
    if documents:
        result = search_client.upload_documents(documents=documents)
        print(f"\nIndexed {len(documents)} documents")
        for item in result:
            print(f"  - {item.key}: {'Success' if item.succeeded else 'Failed'}")
    else:
        print("No documents found to index")

if __name__ == "__main__":
    print("Creating search index...")
    create_index()
    
    print("\nIndexing documents...")
    index_documents()
    
    print("\n✓ Indexing complete!")
EOF

# Now run it
# python scripts/index_documents.py