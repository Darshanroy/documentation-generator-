from flask import Flask, request, jsonify, render_template, send_from_directory
from generator import CodeArtifact
from retriever import ConversationalRAG
from dataclasses import dataclass
import os
from utils import GitHubUrlParser

app = Flask(__name__, static_folder='static', template_folder='templates')

@dataclass
class Credentials:
    repo = "Darshanroy/synthetic-data-generator"
    branch = "dev"
    github_api_url = "https://api.github.com"
    model = "intfloat/multilingual-e5-large"
    persist_directory = "./chroma_db"

sessions = {}

@app.route('/')
def serve_index():
    """Serve the React index.html (frontend)."""
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    """Handle the query and provide a response."""
    data = request.get_json()

    github_url = data.get('github_url')
    file_filter = data.get('file_filter', ".py")  # Default to .py if no filter is provided
    question = data.get('question', "")
    branch = data.get("branch", "main")
    session_id = data.get("session_id")

    if not github_url or not question:
        return jsonify({'error': 'GitHub URL and Question are required'}), 400

    if session_id not in sessions:
        # Parse the GitHub URL for username/repo-name format
        parser = GitHubUrlParser(github_url)
        parsed_url = parser.get_result()

        # Process the request using CodeArtifact and ConversationalRAG
        artifact = CodeArtifact(
            parsed_url,
            branch,
            os.getenv("GITHUB_API_TOKEN"),
            Credentials.github_api_url,
            lambda file_path: file_path.endswith(file_filter),  # Apply file filter here
            Credentials.model,
            os.getenv("HUGGINGFACE_HUB_API_TOKEN"),
            Credentials.persist_directory
        )
        docs = artifact.load_documents(branch)
        vector_store = artifact.create_embeddings(docs)

        sessions[session_id] = {
            'artifact': artifact,
            'vector_store': vector_store
        }
    else:
        artifact = sessions[session_id]['artifact']
        vector_store = sessions[session_id]['vector_store']

    # Example usage:
    groq_api = os.getenv("GROQ_API_KEY")
    conversational_rag = ConversationalRAG(groq_api, vector_store)
    response = conversational_rag.ask_question(session_id, question)

    return jsonify({'answer': response['answer']})

@app.route('/download_files/<path:filename>')
def download_file(filename):
    return send_from_directory('download_files', filename)

if __name__ == '__main__':
    app.run(debug=True)