from flask import Flask, render_template, request
from google import genai
from google.genai import errors
from google.genai import types
from dotenv import load_dotenv
import os
import time

app = Flask(__name__)

# Load API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Connect to Gemini
client = genai.Client(api_key=API_KEY) if API_KEY else None

# Main model and backup model
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite"
]


# AI response function with automatic retries
def generate_ai_response(prompt):

    if client is None:
        return "Error: API key not found. Check your .env file."

    for model in MODELS:

        for attempt in range(2):

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.5,
                        max_output_tokens=700
                    )
                )

                return response.text or "No response generated."

            except errors.APIError as e:

                # Retry temporary server or rate-limit errors
                if e.code in [429, 500, 502, 503, 504]:
                    time.sleep(2 * (attempt + 1))
                    continue

                # Try backup model for other API errors
                break

            except Exception as e:
                return "AI Error: " + str(e)

    return "Gemini is currently busy. Please try again in a minute."


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# EXPLAIN FEATURE
@app.route("/explain", methods=["GET", "POST"])
def explain():

    result = ""

    if request.method == "POST":
        content = request.form.get("content", "").strip()

        if content:
            prompt = (
                "You are a friendly AI study assistant. "
                "Explain the following topic in very simple language "
                "for a college student. Keep it short and easy to understand. "
                "Use simple examples only when useful. "
                "Avoid complicated vocabulary and unnecessary details. "
                "Use these sections: Meaning, Simple Explanation, "
                "Example, and Key Takeaway. "
                "Keep the answer under 250 words.\n\n"
                "Topic: " + content
            )

            result = generate_ai_response(prompt)

        else:
            result = "Please enter a topic."

    return render_template("explain.html", result=result)


# SUMMARIZE FEATURE
@app.route("/summarize", methods=["GET", "POST"])
def summarize():

    result = ""

    if request.method == "POST":
        content = request.form.get("content", "").strip()

        if content:
            prompt = (
                "You are a student-friendly summarization assistant. "
                "Summarize the following text using simple language. "
                "Include only the important points. "
                "Use short bullet points. "
                "Avoid adding information that is not in the original text. "
                "Keep the summary concise.\n\n"
                "Text: " + content
            )

            result = generate_ai_response(prompt)

        else:
            result = "Please enter some text to summarize."

    return render_template("summarize.html", result=result)


# QUIZ FEATURE
@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    result = ""

    if request.method == "POST":
        content = request.form.get("content", "").strip()

        if content:
            prompt = (
                "You are an AI quiz generator for college students. "
                "Create exactly 5 multiple-choice questions about the topic. "
                "Each question must have 4 options: A, B, C, and D. "
                "Show the correct answer after each question. "
                "Keep the questions clear and suitable for students. "
                "Do not add unnecessary explanations.\n\n"
                "Topic: " + content
            )

            result = generate_ai_response(prompt)

        else:
            result = "Please enter a topic for your quiz."

    return render_template("quiz.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)