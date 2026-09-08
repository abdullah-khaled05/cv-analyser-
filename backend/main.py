import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException

from .gap_analyzer import analyze_experience
from .parser import extract_text_from_pdf
from .extractor import extract_cv_data


app = FastAPI(
    title="CV Intelligence Analyzer",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "CV Intelligence Analyzer API"
    }


@app.post("/analyze")
async def analyze_cv(file: UploadFile = File(...)):

    # Check file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    temp_path = None

    try:
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(await file.read())
            temp_path = temp_file.name

        # Step 1: Extract text from PDF
        cv_text = extract_text_from_pdf(temp_path)

        print("PDF TEXT EXTRACTED:")
        print(cv_text[:1000])

        # Check if text was extracted
        if not cv_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF."
            )

        # Step 2: Extract structured CV data
        # Gemini → Groq fallback
        cv_data = extract_cv_data(cv_text)

        print("CV DATA EXTRACTED SUCCESSFULLY")

        # Step 3: Analyze employment gaps
        # and total experience after graduation
        experience_analysis = analyze_experience(cv_data)

        print("EXPERIENCE ANALYSIS:")
        print(experience_analysis)

        # Step 4: Return final result
        return {
            "success": True,
            "data": cv_data.model_dump(),
            "experience_analysis": experience_analysis
        }

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        # Delete temporary PDF
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)