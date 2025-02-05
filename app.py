import json
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import random
import pickle
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
import os

# Initialize Flask app
app = Flask(__name__)

# Load intents data
with open('intents.json', encoding="utf-8") as f:
    data = json.load(f)

# Try loading the pre-trained chatbot model and associated data
try:
    model = tf.keras.models.load_model('chatbot_model.h5')  # Your trained model file
    with open('words.pkl', 'rb') as f:
        words = pickle.load(f)
    with open('classes.pkl', 'rb') as f:
        classes = pickle.load(f)
    print("✅ Model, words, and classes loaded successfully!")
except FileNotFoundError:
    print("❌ Error: One or more files (model, words, classes) not found.")
    exit()
except Exception as e:
    print(f"❌ Error loading model or data: {e}")
    exit()

# Ignore these words during processing
ignore_words = ["?", "!", "'s", "%", ",","-"]

# Lemmatize and lower each word and remove duplicates
lemmatizer = WordNetLemmatizer()
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# ---- ROUTES ----

@app.route('/')
def home():
    """ Serve the chatbot UI. """
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    """ Handle user input and return chatbot response. """
    user_message = request.json.get('message', '')

    if not user_message.strip():
        return jsonify({'response': "I'm sorry, I didn't understand that. Can you try again?"})

    # Predict chatbot response
    intents = predict_class(user_message, model, words, classes)
    bot_response = getResponse(intents, data)
    
    return jsonify({'response': bot_response})

@app.route('/favicon.ico')
def favicon():
    """ Serve favicon. """
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ---- CHATBOT FUNCTIONS ----

def predict_class(sentence, model, words, classes):
    """ Predict the intent of a user's message. """
    bow_vector = bow(sentence, words)
    res = model.predict(np.array([bow_vector]))[0]
    
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)  # Sort by probability

    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]

def getResponse(intents, intents_json):
    """ Fetch a random response based on the predicted intent. """
    if not intents:
        return "I'm sorry, I didn't understand that."

    tag = intents[0]['intent']
    for intent in intents_json['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    
    return "I'm not sure how to respond to that."

def bow(sentence, words):
    """ Convert a sentence into a bag-of-words vector. """
    sentence_words = clean_up_sentence(sentence)
    bag = [1 if w in sentence_words else 0 for w in words]
    return np.array(bag)

def clean_up_sentence(sentence):
    """ Tokenize and lemmatize user input. """
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

# ---- RUN FLASK ----
if __name__ == '__main__':
    app.run(debug=True)
