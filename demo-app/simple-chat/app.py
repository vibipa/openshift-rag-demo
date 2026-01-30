from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

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

        # Search for relevant documents
        search_results = search_client.search(
            search_text=user_message,
            top=3
        )

        # Build context
        context = "\n\n".join([r.get('content', '')[:1000] for r in search_results])

        # Generate answer with GPT-4
        response = openai_client.chat.completions.create(
            model=os.getenv("GPT4_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are an OpenShift expert. Provide step-by-step troubleshooting guidance."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}"}
            ],
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000, debug=True)