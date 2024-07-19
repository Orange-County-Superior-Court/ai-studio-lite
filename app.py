import os

import uuid
import json
from flask import Flask, redirect, render_template, request, url_for, flash
from flask import send_from_directory

from flask import session, Response
from werkzeug.utils import secure_filename

from langchain.document_loaders import PyPDFLoader
from flows.chat import Chat
from components.file_storage.files import FileStorage
from components.security.guards import Security
from database.local_storage import LocalStorage
from flows.embed_docs import embed_docs as udf_embedding_flow
from flows.reset_index import reset_index as udf_reset_index

UPLOAD_FOLDER = './local_storage/documents'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','py','pptx','docx','csv','xlsx','xml'}
CHAT_CONFIG_FOLDER = './local_storage/chat_config'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CHAT_CONFIG_FOLDER'] = CHAT_CONFIG_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=("GET", "POST"))
def index():
    result = request.args.get("result")
    return render_template("index.html", result=result)

@app.route('/local_storage/documents/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/chat/basic_flow',methods=["POST"])
def send_chat():
    user_message = request.form["prompt"]
    """
    from flows.chat import Chat
    user_message = "hello"
    """
    local_storage = LocalStorage()
    chatbot_data = local_storage.read_chatbot(1)
    history_dict = {'role':'user', 'content':user_message, 'chatbot_id':1}
    chat_metadata = {'chatbot_id':'chatbot-generic'}
    cls_chat = Chat(chat_metadata) 

    #switch on/off security
    security = chatbot_data['security']
    if security == 'On':
        #llm guard
        llm_guard = Security()
        scan_result = llm_guard.scan_input(user_message)
        if scan_result['was_flagged']:
            print("Scan Results: ", scan_result)
            flags = scan_result['flagged_scanners']
            user_message = f"This message does not comply with the security guard rails. Here are the security guard rails that were triggered {flags}"
            user_message_redacted = 'REDACTED_MESSAGE'
            history_dict = {'role':'user', 'content':user_message_redacted, 'chatbot_id':1}
            stream = cls_chat.chat_stream_security(user_message)
        else:
            stream = cls_chat.chat_stream(user_message)
    else:
        chat_metadata = {'chatbot_id':'chatbot-generic'}
        cls_chat = Chat(chat_metadata)
        stream = cls_chat.chat_stream(user_message)

    local_storage.create_chat_history(history_dict)     

    # Now you can read the 'text' variable and also return the stream
    return Response(stream, mimetype='text/event-stream')

@app.route('/data', methods=["GET"])
def read_data():
    """
    from database.local_storage import LocalStorage
    """
    local_storage = LocalStorage()
    chatbot_data = local_storage.read_chatbot(1)
    chat_history_data = local_storage.read_chat_history(1)
    if chat_history_data:
        chat_history_data_final = [{'Role': item['role'], 'Content': item['content']} for item in chat_history_data] 
    system_messages_data = local_storage.read_system_message(1)
    
    data = {
        'chat_config': {
            "temperature": chatbot_data['temperature'],
            'security': chatbot_data['security'],
            "chat_model_provider": chatbot_data['chat_model_provider'],
            "chat_model_deployment": chatbot_data['chat_model_deployment'],
            "embedding_model_provider": chatbot_data['embedding_model_provider'],
            "embedding_model_deployment": chatbot_data['embedding_model_deployment'],
            "past_messages": chatbot_data['past_messages'],
            "search_top_k": chatbot_data['search_top_k'],
            "max_tokens": chatbot_data['max_tokens'],

            "top_p": chatbot_data['top_p'],
            "chain_type": chatbot_data['chain_type']
        },
        'chat_history': chat_history_data_final,
                
        'system_messages': system_messages_data['system_message'],
        'prompt_template': chatbot_data['prompt_template']
    }

    return data

@app.route('/upload-file', methods=["PUT"])
def upload_file_new():
    if request.method == 'PUT':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
                
            file.save(file_path)
            embed_result = udf_embedding_flow(file_path)
        print(file_path)
    return ("", 200)

@app.route('/chat-history', methods=["DELETE"])
def delete_chat_history():
    local_storage = LocalStorage()
    local_storage.delete_chat_history()
    return ("", 200)

@app.route('/chat-history', methods=["POST"])
def append_to_chat_history():
    bot_response = request.json["bot_response"];
    local_storage = LocalStorage()
    bot_response = request.json["bot_response"];
    history_dict = {'role':'assistant', 'content':bot_response, 'chatbot_id':1}
    local_storage.create_chat_history(history_dict)
    return ("", 200)

@app.route('/save-config', methods=["PUT"])
def save_config_new():
    """
    dict_data = {'chat_config': {'ChatModel': {'chat_model_deployment': 'phi3:mini', 'model_provider': 'ollama'}, 'EmbeddingModel': {'model_deployment': 'nomic-embed-text', 'model_provider': 'ollama'}, 'MaxTokens': 1000, 'SearchTopK': 100, 'Temperature': 0.1, 'TopP': 1, 'chain_type': 'basic', 'past_messages': 0, 'template_subtype': 'safe', 'template_type': 'basic'}, 'prompt_template': '{user_message}', 'system_messages': 'do not answer inappropriate questions'}

    """
    dict_data = request.json

    chat_config = dict_data['chat_config']
    system_message = dict_data['system_messages']
    local_storage = LocalStorage()

    local_storage.update_system_messages({'chatbot_id':1,'system_message':system_message})

    chat_config = dict_data['chat_config']
    chat_config['prompt_template'] = dict_data['prompt_template']
    chat_config['chatbot_id'] = 1
    chat_config['chatbot_name'] = 'spongebob'

    local_storage.update_chatbot(chat_config)

    return ("", 200)

@app.route('/index', methods=['DELETE'])
def reset_index():
    result = udf_reset_index()
    return ("", 200)

@app.route('/last_message', methods=["GET"])
def last_message():
    """
    from database.local_storage import LocalStorage
    """
    flagged = 'no'
    try:
        local_storage = LocalStorage()
        chatbot_data = local_storage.read_chatbot(1)
        chat_history_data = local_storage.read_chat_history(1)
        if chat_history_data:
            chat_history_data_final = [{'Role': item['role'], 'Content': item['content']} for item in chat_history_data]
        last_message = chat_history_data_final[-2]['Content']
    except:
        last_message = 'No message found'

    if last_message == 'REDACTED_MESSAGE':
        flagged = 'yes'
    
    response = {'flagged': flagged, 'last_message': last_message}

    return (response, 200)

if __name__ == '__main__':
   app.run()