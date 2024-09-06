from flask import Flask, request, jsonify
import chatbot

app = Flask(__name__)

@app.route('/')
def root():
    return "conect successfully"

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    user_input = request.json.get('message')
    # 여기에 챗봇 로직을 추가하세요.
    response = chatbot.ask_query(user_input, chatbot.history)
    return jsonify({'response': str(response)})

if __name__ == '__main__':
    app.run(port=5000)