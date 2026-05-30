import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_gemini_client(api_key: str = None):
    """
    Configures and returns the Gemini model.
    Checks parameters first, then environment variables.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key not found. Please set GEMINI_API_KEY in your .env or enter it in the sidebar.")
        
    genai.configure(api_key=key)
    # Using gemini-2.5-flash as specified by the user
    return genai.GenerativeModel("gemini-2.5-flash")

def optimize_resume(resume: str, jd: str, api_key: str = None) -> str:
    """
    Sends the resume and job description to Gemini 2.5 Flash to generate a tailored, ATS-friendly resume.
    Ensures that missing skills and relevant industry terms are naturally integrated while remaining truthful.
    """
    try:
        model = get_gemini_client(api_key)
    except ValueError as e:
        return str(e)
        
    prompt = f"""
You are an expert ATS (Applicant Tracking System) optimizer and professional resume writer.
Your goal is to tailor the following Resume to match the Job Description perfectly, while keeping all information truthful.

---

### JOB DESCRIPTION:
{jd}

---

### ORIGINAL RESUME:
{resume}

---

### CRITICAL LINK INSTRUCTIONS:
1. **Preserve All URLs Exactly**: You MUST preserve all URLs and hyperlinks present in the original resume exactly. Never modify, truncate, shorten, or remove any URLs. Keep all domain names and complete paths completely unchanged.
2. **Absolute, Fully-Qualified Hyperlink Paths**: You MUST output fully qualified absolute URLs containing complete domain names and protocols (e.g. `[LinkedIn](https://linkedin.com/in/username)` and `[GitHub](https://github.com/username)`). You are STRICTLY FORBIDDEN from shortening or truncating URLs into local paths or domain shortcuts (e.g., writing `[GitHub](github)` or `[LinkedIn](linkedin)` is an error; you MUST include the full `.com` and the complete profile path).
3. **Map Extracted Hyperlinks**: At the end of the original resume text, there may be a section called `=== EXTRACTED HYPERLINKS ===` containing the actual URLs associated with hyperlinked labels in the original document (e.g. `- "LinkedIn": https://linkedin.com/in/username`). You MUST map these actual URLs back to their respective clickable markdown links in the optimized resume header and text. For example, if you output a link for 'LinkedIn', you MUST use the exact URL from the extracted list (e.g., `[LinkedIn](https://linkedin.com/in/username)`). Do NOT output the `=== EXTRACTED HYPERLINKS ===` section itself in the final markdown output.
4. **Horizontal Contact Header Links**: For contact information links (such as LinkedIn, GitHub, Portfolios, LeetCode, HackerRank, etc.), format them on a single, clean horizontal line separated by a pipe character ` | ` instead of bullet points, using the following syntax:
   `[LinkedIn](URL) | [GitHub](URL) | [Portfolio](URL) | [LeetCode](URL)`
   Keep this header compact, professional, and elegant.

---

### INSTRUCTIONS:
1. **Incorporate Keywords**: Naturally insert missing skills and relevant industry keywords from the job description into the professional summary, projects, work experience, and skills sections. Avoid keyword stuffing.
2. **Enhance Work Experience**: For each role, rewrite bullet points using the **STAR method** (Situation, Task, Action, Result) starting with strong action verbs (e.g., "Spearheaded", "Optimized", "Architected", "Increased"). Focus on achievements, quantify results where possible, and match the tone of the job description.
3. **Refine Professional Summary**: Write a compelling, results-oriented 3-4 sentence professional summary that immediately highlights matching experience and technical skills.
4. **Tailor Projects (Add a Job-Specific Project)**: Add one new, highly relevant, and tailored project (or optimize an existing one) under the `## Projects` section that directly aligns with a key technical challenge or core requirement described in the Job Description. The project should showcase the candidate's existing technical skills applied to solve a realistic industry problem, making their practical capabilities immediately clear.
5. **Format Cleanly**: Output the optimized resume using standard Markdown formatting with clear headers:
   - `# [Full Name]` (at the top)
   - Contact info (Email | Phone | Address | Pipe-separated links: `[LinkedIn](URL) | [GitHub](URL) | [Portfolio](URL)`)
   - `## Professional Summary`
   - `## Skills` (Group by Technical, Databases, DevOps, etc.)
   - `## Work Experience`
   - `## Projects`
   - `## Education`
6. **Truthfulness**: Maintain the core truth of the resume. Do not invent entirely new jobs, degrees, or companies, but express existing experience in a way that matches what the job description is seeking.
7. **Output format**: Return *only* the tailored resume text in clean Markdown format. Do not add any conversational preambles or post-scripts.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during Gemini optimization: {str(e)}"
