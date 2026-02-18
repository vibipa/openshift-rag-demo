from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import traceback
import markdown 
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

@app.route('/')
def index():
    return render_template('index.html')

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
            #select=["snippet", "blob_url", "uid"],
            top=3
        )

        # Convert to list to inspect results
        #result_list = list(search_results)
        #print(f"=== RETRIEVED {len(result_list)} DOCUMENTS ===")
        result_list = list(search_results)
        print(f"=== RETRIEVED {len(result_list)} DOCUMENTS ===")
        
        # Build context with better formatting
        context_parts = []
        for idx, r in enumerate(result_list):
            source = r.get('filepath', 'NO_FILEPATH')
            title = r.get('title', 'NO_TITLE')
            content = r.get('content', 'NO_CONTENT')[:1000]
        
        #context_parts = []
        #for idx, r in enumerate(result_list):
        #    source = r.get('blob_url', 'NO_FILEPATH')  # CHANGED
        #    title = r.get('blob_url', 'NO_TITLE')  # CHANGED
        #    content = r.get('snippet', 'NO_CONTENT')[:1000]  # CHANGED
            
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
                {"role": "system", "content": """You are a Cloud Infrastructure expert assistant for a managed services team supporting 15 enterprise clients.

You specialize in the following technologies:

1. **Microsoft Azure** - Azure infrastructure, services, architecture, troubleshooting, cost management, and governance across multi-tenant environments managed via Azure Lighthouse.

2. **OpenShift & Kubernetes** - Container platforms, pod troubleshooting, deployments, ArgoCD GitOps workflows, and cluster operations.

3. **Broadcom/VMware Private Cloud** - VMware vSphere, NSX, vSAN, Aria Suite, and private cloud infrastructure management.

When answering:
- Use the provided documentation context as your primary source
- Reference specific source files when answering
- If the documentation does not contain the answer, say so clearly - do not guess
- For topics outside Azure, OpenShift/Kubernetes, and Broadcom/VMware, politely decline and clarify your scope

Format your responses clearly:
- Use numbered lists for sequential steps (1. 2. 3.)
- Use bullet points for non-sequential items
- Use **bold** for important terms
- Use `code blocks` for commands, YAML, and configuration snippets
- Add blank lines between sections for readability"""},
                {"role": "user", "content": f"Context from our Cloud documentation:\n\n{context}\n\nQuestion: {user_message}"}
            ],
            temperature=0.3,
            max_tokens=800
        )

        answer = response.choices[0].message.content
        print(f"=== GENERATED ANSWER ===\n{answer[:200]}...\n")
        
        # Convert markdown to HTML for better formatting
        answer_html = markdown.markdown(
            answer,
            extensions=['nl2br', 'fenced_code']  # Preserve line breaks and code blocks
        )

        return jsonify({'answer': answer_html})

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    import sys
    sys.stdout = sys.stderr  # Force prints to stderr which is captured better
    app.run(host='0.0.0.0', port=5000, debug=True)