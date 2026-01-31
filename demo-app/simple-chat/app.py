from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import traceback
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery

load_dotenv()

app = Flask(__name__)
CORS(app)

print("Environment check:")
print(f"OPENAI_ENDPOINT: {os.getenv('OPENAI_ENDPOINT')}")
print(f"SEARCH_ENDPOINT: {os.getenv('SEARCH_ENDPOINT')}")
print(f"GPT4_DEPLOYMENT: {os.getenv('GPT4_DEPLOYMENT')}")

# Initialize Azure OpenAI client (new SDK)
print("Initializing OpenAI client...")
openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_KEY"),
    api_version="2024-02-01"
)
print("OpenAI client initialized!")

# Initialize Azure Cognitive Search client
print("Initializing Search client...")
search_client = SearchClient(
    endpoint=os.getenv("SEARCH_ENDPOINT"),
    index_name="openshift-docs",
    credential=AzureKeyCredential(os.getenv("SEARCH_KEY"))
)
print("Search client initialized!")


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        print(f"\n=== USER QUESTION: {user_message} ===")

        # Generate embedding for user question
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=user_message
        )
        question_embedding = embedding_response.data[0].embedding
        print(f"Generated embedding: {len(question_embedding)} dimensions")

        # Vector search using embeddings
        vector_query = VectorizedQuery(
            vector=question_embedding,
            k_nearest_neighbors=3,
            fields="content_vector"
        )

        search_results = search_client.search(
            search_text=user_message,
            vector_queries=[vector_query],
            select=["content", "title", "filepath"],
            top=3
        )

        # Convert to list to inspect results
        result_list = list(search_results)
        print(f"=== RETRIEVED {len(result_list)} DOCUMENTS ===")
        
        # Build context with better formatting
        context_parts = []
        for idx, r in enumerate(result_list):
            source = r.get('filepath', 'NO_FILEPATH')
            title = r.get('title', 'NO_TITLE')
            content = r.get('content', 'NO_CONTENT')[:1000]
            
            print(f"\nDoc {idx+1}:")
            print(f"  Filepath: {source}")
            print(f"  Title: {title}")
            print(f"  Content preview: {content[:200]}...")
            
            context_parts.append(f"Source: {source}\n{content}")
        
        context = "\n\n---\n\n".join(context_parts)
        print(f"\n=== CONTEXT LENGTH: {len(context)} chars ===")

        # Generate answer with GPT-4
        response = openai_client.chat.completions.create(
            model=os.getenv("GPT4_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are an OpenShift expert. Use the provided context from our documentation and YAML configurations to provide accurate, specific answers. Always reference the source files when answering."},
                {"role": "user", "content": f"Context from our OpenShift documentation:\n\n{context}\n\nQuestion: {user_message}"}
            ],
            temperature=0.3,
            max_tokens=800
        )

        answer = response.choices[0].message.content
        print(f"=== GENERATED ANSWER ===\n{answer[:200]}...\n")

        return jsonify({'answer': answer})

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)