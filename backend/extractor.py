import os
import json

from dotenv import load_dotenv
from google import genai
from groq import Groq

from .schemas import CVData


load_dotenv()


# ==============================
# API Clients
# ==============================

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ==============================
# Gemini
# ==============================

def extract_with_gemini(cv_text: str) -> CVData:

    prompt = f"""
You are a professional CV information extraction system.

Extract all available information from the CV below.

Rules:
- Do not invent information.
- Use null when information is unavailable.
- Use empty lists when there are no items.
- Preserve dates exactly when possible.
- Extract education, work experience, projects,
  skills and certifications.

CV TEXT:

{cv_text}
"""

    response = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": CVData.model_json_schema()
        }
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return CVData.model_validate_json(response.text)


# ==============================
# Groq
# ==============================

def extract_with_groq(cv_text: str) -> CVData:

    schema = CVData.model_json_schema()

    prompt = f"""
You are a professional CV information extraction system.

Extract all available information from the CV below.

Return ONLY valid JSON.

Rules:
- Do not invent information.
- Use null when information is unavailable.
- Use empty lists when there are no items.
- Preserve dates exactly when possible.
- Extract education, work experience, projects,
  skills and certifications.

The JSON must follow this schema:

{json.dumps(schema, indent=2)}

CV TEXT:

{cv_text}
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a CV information extraction system. "
                    "Return only valid JSON."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned an empty response.")

    data = json.loads(content)

    return CVData.model_validate(data)


# ==============================
# Primary + Fallback
# ==============================

def extract_cv_data(cv_text: str) -> CVData:

    gemini_error = None
    groq_error = None

    # --------------------------------
    # 1. Try Gemini
    # --------------------------------

    try:

        print("\n==============================")
        print("Trying Gemini...")
        print("==============================")

        result = extract_with_gemini(cv_text)

        print("Gemini succeeded.")

        return result

    except Exception as e:

        gemini_error = e

        print("\nGemini failed:")
        print(repr(e))

    # --------------------------------
    # 2. Fallback to Groq
    # --------------------------------

    try:

        print("\n==============================")
        print("Trying Groq fallback...")
        print("==============================")

        result = extract_with_groq(cv_text)

        print("Groq succeeded.")

        return result

    except Exception as e:

        groq_error = e

        print("\nGroq also failed:")
        print(repr(e))

    # --------------------------------
    # 3. Both failed
    # --------------------------------

    raise RuntimeError(
        "Both AI providers failed.\n\n"
        f"Gemini error: {repr(gemini_error)}\n\n"
        f"Groq error: {repr(groq_error)}"
    )