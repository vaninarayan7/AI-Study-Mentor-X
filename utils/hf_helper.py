import requests
import streamlit as st
import os
import json
import re

# Explicit model and endpoint - no auto-routing
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"

def get_token():
    """
    Resolves the Hugging Face token from session state, environment variables, or Streamlit secrets.
    """
    token = None

    # 1. Check session state (sidebar input)
    if "hf_token" in st.session_state and st.session_state.hf_token:
        token = st.session_state.hf_token
    # 2. Check environment variables
    elif os.environ.get("HF_TOKEN"):
        token = os.environ.get("HF_TOKEN")
    elif os.environ.get("HUGGINGFACE_CODELAB_KEY"):
        token = os.environ.get("HUGGINGFACE_CODELAB_KEY")
    # 3. Check Streamlit secrets
    else:
        try:
            token = st.secrets["HF_TOKEN"]
        except Exception:
            try:
                token = st.secrets["HUGGINGFACE_CODELAB_KEY"]
            except Exception:
                pass

    if not token:
        raise ValueError(
            "⚠️ Hugging Face Token is missing. Please enter your token in the sidebar on the Home page."
        )
    return token


def chat_completion(messages, max_tokens=2000):
    """
    Sends a chat completion request directly to the Hugging Face router endpoint.
    Returns the assistant's message content string.
    """
    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
    except requests.exceptions.Timeout:
        raise RuntimeError("Request to Hugging Face API timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Could not connect to the Hugging Face API. Check your internet connection.")

    # Handle HTTP errors with descriptive messages
    if response.status_code == 401:
        raise ValueError(
            "❌ Invalid Hugging Face Token. Please verify your token is correct and has inference access."
        )
    elif response.status_code == 403:
        raise ValueError(
            "❌ Access denied. Your token may not have permission for this model. "
            "Ensure your HF token has read access and you've accepted the model's terms."
        )
    elif response.status_code == 429:
        raise RuntimeError(
            "⏳ Rate limit exceeded. Please wait a moment before trying again."
        )
    elif response.status_code >= 500:
        raise RuntimeError(
            f"🔧 Hugging Face server error (HTTP {response.status_code}). Please try again shortly."
        )
    elif not response.ok:
        try:
            err_detail = response.json().get("error", response.text[:300])
        except Exception:
            err_detail = response.text[:300]
        raise RuntimeError(f"Hugging Face API error (HTTP {response.status_code}): {err_detail}")

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to parse Hugging Face API response: {e}. Response: {response.text[:500]}")


def parse_json_response(text_response):
    """
    Extracts and parses a JSON array from raw model text responses,
    stripping markdown code fences if present.
    """
    cleaned = text_response.strip()

    # Remove markdown code fences: ```json ... ``` or ``` ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    cleaned = cleaned.strip()

    # Try to extract a JSON array directly using regex as fallback
    match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    return json.loads(cleaned)


def generate_summary(text):
    """
    Generates a structured study summary from notes using Qwen.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert academic tutor. Summarize these study notes. "
                "Provide the summary structured strictly in markdown format with the following three sections:\n\n"
                "### Key Concepts\n"
                "[Provide bulleted key concepts, with explanations of core terms]\n\n"
                "### Important Topics\n"
                "[Highlight the most crucial topics and sub-topics from the text]\n\n"
                "### Exam Tips\n"
                "[Give strategic advice on what to focus on for exams, potential questions, and memorization tips]"
            ),
        },
        {"role": "user", "content": f"Study Notes Text:\n{text[:8000]}"},
    ]
    return chat_completion(messages, max_tokens=2000)


def tutor_answer(text, question, chat_history=None):
    """
    Answers a tutoring question based on notes context using Qwen.
    """
    system_instruction = (
        "You are a helpful, patient, and knowledgeable AI Tutor. You are helping a student study their uploaded notes. "
        "Use the following notes context to answer the student's question. "
        "If the answer cannot be found in the notes, use your general academic knowledge but mention it is not in the notes.\n"
        "Keep your explanations clear, structured, and easy to understand.\n\n"
        f"Uploaded Notes Context:\n{text[:6000]}"
    )

    messages = [{"role": "system", "content": system_instruction}]

    # Append last 6 conversation turns for memory context
    if chat_history:
        for msg in chat_history[-6:]:
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["content"]})

    messages.append({"role": "user", "content": question})
    return chat_completion(messages, max_tokens=1500)


def generate_quiz(text):
    """
    Generates 10 MCQs in structured JSON format using Qwen.
    """
    prompt = (
        "Generate exactly 10 Multiple Choice Questions (MCQs) from the study notes provided below.\n"
        "Your response MUST be a valid JSON array of exactly 10 objects, and absolutely nothing else.\n"
        "Do NOT wrap the output in markdown code blocks. Do NOT write any preamble or postscript. Output ONLY the raw JSON array.\n\n"
        "Each object in the array must have the following keys:\n"
        "- 'question_num': (integer, 1 to 10)\n"
        "- 'question': (string, the question text)\n"
        "- 'options': (array of 4 strings, starting with 'A) ', 'B) ', 'C) ', 'D) ')\n"
        "- 'correct_answer': (string, exactly one character: 'A', 'B', 'C', or 'D')\n"
        "- 'topic': (string, the academic topic name, e.g. 'Normalization')\n\n"
        f"Notes:\n{text[:7000]}"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a quiz generation engine. You output only valid JSON arrays, "
                "nothing else. No explanations, no markdown, no preamble. Only JSON."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    raw_text = chat_completion(messages, max_tokens=2500)

    try:
        quiz_data = parse_json_response(raw_text)
        return quiz_data
    except Exception as e:
        print(f"[hf_helper] Error parsing quiz JSON: {e}\nRaw response:\n{raw_text}")
        raise RuntimeError(
            "Failed to parse the quiz response as JSON. "
            "The model returned an unexpected format. Please try generating again."
        )


def analyze_weak_topics(wrong_answers):
    """
    Identifies and summarizes weak topics based on wrong quiz answers using Qwen.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert academic tutor. Analyze the student's incorrect quiz answers. "
                "Identify their weak topics and explain briefly what the student should review for each weak topic.\n"
                "Provide the output as a clean, bulleted markdown list with topic names in bold, "
                "followed by brief 2-sentence study advice for each topic."
            ),
        },
        {
            "role": "user",
            "content": f"Incorrect Answers Data:\n{json.dumps(wrong_answers, indent=2)}",
        },
    ]
    return chat_completion(messages, max_tokens=1500)


def generate_study_plan(text, weak_topics, days):
    """
    Generates a day-by-day study schedule based on days remaining, notes context, and weak topics.
    """
    system_prompt = (
        "You are an expert academic counselor. Create a highly customized and realistic day-by-day study plan "
        f"for the next {days} days leading up to the exam. "
        "Focus extra attention on the student's identified weak topics while covering all core concepts.\n"
        "Structure the schedule day-by-day with concrete tasks and self-test checkpoints.\n"
        "Provide the output in clean, structured markdown."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Weak Topics:\n{weak_topics}\n\nNotes Context Summary:\n{text[:6000]}",
        },
    ]
    return chat_completion(messages, max_tokens=2000)
