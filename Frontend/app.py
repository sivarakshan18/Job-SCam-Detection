from flask import Flask, render_template, request, jsonify
import joblib
import re
import numpy as np

app = Flask(__name__)

# --- 1. Load the Saved Models ---
# Ensure these files are in the same folder as app.py
try:
    model = joblib.load('fake_job_detector_svm.pkl')
    tfidf = joblib.load('tfidf_vectorizer.pkl')
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    print("Make sure 'fake_job_detector.pkl' and 'tfidf_vectorizer.pkl' are in the same folder.")

# --- 2. Preprocessing Function ---
# This MUST match the logic used during training
def clean_text(text):
    text = str(text).lower()                    
    text = re.sub(r'http\S+', '', text)         
    text = re.sub(r'[^a-zA-Z\s]', '', text)     
    text = re.sub(r'\s+', ' ', text).strip()    
    return text

# --- 3. Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get text from either JSON (Postman) or Form (Browser)
    if request.is_json:
        data = request.get_json()
        user_input = data.get('text', '')
    else:
        user_input = request.form.get('job_text', '')

    if not user_input:
        return render_template('index.html', prediction_text="Please enter some text.")

    # 1. Clean the text
    cleaned_text = clean_text(user_input)

    # 2. Vectorize the text (Use transform, NOT fit_transform)
    vectorized_text = tfidf.transform([cleaned_text])

    # 3. Predict
    prediction = model.predict(vectorized_text)
    
    # 4. Interpret result (0 = Real, 1 = Fraudulent)
    result = "Fraudulent (Fake)" if prediction[0] == 1 else "Real (Legitimate)"
    
    # 5. Return response based on request type
    if request.is_json:
        # Response for Postman/API
        return jsonify({'prediction': result, 'input_processed': cleaned_text})
    else:
        # Response for Web Interface
        color = "red" if prediction[0] == 1 else "green"
        return render_template('index.html', 
                               prediction_text=f"Prediction: {result}", 
                               original_text=user_input,
                               result_color=color)

if __name__ == "__main__":
    app.run(debug=True)