from flask import Flask, render_template, request, jsonify 
import openai
import sqlite3

app = Flask(__name__)

# OpenAI API key
openai.api_key = "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"

# Function to generate a response using the GPT model
def generate_response(question):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Answer the following as a tax auditor for Deloitte:\n{question}\nAnswer:",
        max_tokens=100
    )
    return response.choices[0].text

# Function to create the SQLite database and responses table
def create_database():
    conn = sqlite3.connect('tax_responses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY,
            prompt TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_database()

@app.route('/', methods=['GET'])
def index():
    return render_template('question.html')

@app.route('/responses')
def responses():
    responses = get_all_responses()
    last_entry = get_last_entry()
    return render_template('responses.html', responses=responses, last_request=last_entry[0], last_response=last_entry[1])

@app.route('/last_request_response', methods=['GET'])
def last_request_response():
    last_entry = get_last_entry()
    return jsonify({'last_request': last_entry[0], 'last_response': last_entry[1]})

@app.route('/ajax_response', methods=['POST'])
def ajax_response():
    question = request.form['question']
    response = generate_response(question)
    save_response(question, response)
    return jsonify({'response': response})

def save_response(prompt, response):
    conn = sqlite3.connect('tax_responses.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO responses (prompt, response) VALUES (?, ?)", (prompt, response))
    conn.commit()
    conn.close()

def get_all_responses():
    conn = sqlite3.connect('tax_responses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responses")
    responses = cursor.fetchall()
    conn.close()
    return responses

def get_last_entry():
    conn = sqlite3.connect('tax_responses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, response FROM responses ORDER BY id DESC LIMIT 1")
    last_entry = cursor.fetchone()
    conn.close()
    return last_entry

# Start your Flask application here
if __name__ == '__main__':
    app.run(debug=True)
