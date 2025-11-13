from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import traceback
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins (useful for Gmail Extension)

# --------------------------------------
# 1️⃣ Load TF-IDF Vectorizer & Model
# --------------------------------------
try:
    print("⏳ Loading TF-IDF Vectorizer and Model...")
    tfidf = joblib.load('tfidf_vectorizer.pkl')
    model = joblib.load('fake_job_detector.pkl')
    print("✅ TF-IDF Vectorizer and Model loaded successfully!")
except Exception as e:
    print("❌ Error loading model/vectorizer:", e)
    tfidf = None
    model = None


# --------------------------------------
# 2️⃣ Text Cleaning Function (MUST MATCH training)
# --------------------------------------
def clean_text(text):
    """Cleans text exactly as done during training."""
    text = str(text).lower()
    text = re.sub(r"http\S+", " ", text)         # Remove URLs
    text = re.sub(r"[^a-z0-9\s]", " ", text)     # Keep only letters/numbers/spaces
    text = re.sub(r"\s+", " ", text).strip()     # Normalize whitespace
    return text


# --------------------------------------
# 3️⃣ Home Endpoint
# --------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🚀 Fake Job Detection API is running!",
        "endpoints": {
            "POST /predict": {
                "description": "Predict whether a job posting is fake or real",
                "example_input": {"text": "Earn $5000 per week working from home!"}
            }
        }
    })


# --------------------------------------
# 4️⃣ Prediction Endpoint
# --------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if tfidf is None or model is None:
        return jsonify({"error": "Model or vectorizer not loaded properly"}), 500

    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field in JSON body"}), 400

        input_text = data["text"]
        cleaned_text = clean_text(input_text)

        # ✅ Transform text using TF-IDF
        X = tfidf.transform([cleaned_text])

        # ✅ Predict
        prediction = int(model.predict(X)[0])
        result = "Fake Job Posting" if prediction == 1 else "Real Job Posting"

        print(f"\n🧠 INPUT: {input_text}\n🧹 CLEANED: {cleaned_text}\n📊 PREDICTION: {result}")

        return jsonify({
            "input_text": input_text,
            "prediction": prediction,
            "result": result
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


# --------------------------------------
# 5️⃣ Run Flask App
# --------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
