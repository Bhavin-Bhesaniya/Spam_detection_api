from nltk.corpus import stopwords
import pandas as pd
import pickle
import re
from nltk.corpus import stopwords
import nltk
import string
import joblib

tfidf = pickle.load(open('Model/vectorizer.pkl','rb'))

model_names = ['rfmodel.pkl', 'knmodel.pkl', 'gbdtmodel.pkl','mnbmodel.pkl']
models = {model_name: joblib.load(f'Model/{model_name}') for model_name in model_names}

user_data = []

def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    y = []
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            if i.isalnum():
                y.append(i)
    return " ".join(y)


def is_malicious(text):
    for pattern in malicious_patterns:
        if re.search(pattern, text):
            return True
    return False


def classify_spam(user_message, select_model):
    if user_message is None:
        result_message = "Please enter text"
        return result_message
    user_message = ''.join(user_message.splitlines())

    # if not is_malicious(user_message):
    if user_message:
        transformed_text = transform_text(user_message)
        vector_input = tfidf.transform([transformed_text])
        
        if select_model in models:
            select_model = models[select_model]
            result = select_model.predict(vector_input)[0]
            if result == 1:
                result_message = "Spam"
            else:
                result_message = "Not Spam"
            
            existing_data = pd.read_csv("Model/user_insert_value.csv")
            if not existing_data[(existing_data['target'] == result) & (existing_data['text'] == user_message)].empty:
                return result_message
            else:
                user_data.append({'target': result, 'text': user_message})
                df = pd.DataFrame(user_data)
                df.to_csv("Model/user_insert_value.csv", mode='a', header=False, index=False)
                return result_message
        else:
            result_message = "Model Not found. Please select provided model only"
            return result_message
    else:
        result_message = "Malicious code detected in the input. Please enter a valid message."
        return result_message