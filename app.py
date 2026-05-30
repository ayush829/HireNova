import streamlit as st
import os
import time
from datetime import datetime

# Import services
from services.parser import read_pdf, read_docx
from services.ats_score import extract_skills, compare_skills, ats_score
from services.ai_service import optimize_resume
from services.pdf_generator import create_pdf

# Set page config
st.set_page_config(
    page_title="HireNova - AI Resume Tailor & ATS Optimizer",
    page_icon="⚡",
    layout="wide"
)

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)

# Inject custom modern theme-adaptive CSS (Adapts to both Light and Dark modes dynamically)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
    
    /* 1. THEME-AGNOSTIC ADAPTIVE BASE FONTS (No global background overrides to preserve native light/dark mode) */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Global font headers config */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text-color) !important;
    }
    
    /* Ensure regular markdown texts adapt cleanly to light/dark text colors */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] li {
        color: var(--text-color) !important;
        font-size: 0.95rem;
        line-height: 1.6;
        opacity: 0.95;
    }
    
    /* Header Gradient styling - Clean high contrast theme-agnostic gradient */
    .header-gradient {
        background: linear-gradient(135deg, #2563eb, #3b82f6, #60a5fa) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        font-size: 3.6rem !important;
        font-weight: 800;
        margin-bottom: 0.1rem;
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.03em;
    }
    
    .subtitle-text {
        color: var(--text-color) !important;
        opacity: 0.7;
        font-size: 1.15rem;
        margin-bottom: 2.2rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }
    
    /* File Uploader Custom Styling Wrapper (Theme-Adaptive) */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(59, 130, 246, 0.25) !important;
        border-radius: 16px !important;
        background: var(--secondary-background-color) !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(37, 99, 235, 0.6) !important;
    }
    [data-testid="stFileUploader"] label {
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }
    
    /* Make the helper description text highly visible in both themes */
    [data-testid="stFileUploader"] section div, 
    [data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stFileUploader"] small {
        color: var(--text-color) !important;
        opacity: 0.8;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }
    
    /* Style all input fields to have a clean border without overriding native backgrounds */
    .stTextArea textarea, .stTextInput input {
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
        outline: none !important;
    }
    
    /* Dynamic skill tags with vibrant styling (Adaptive) */
    .skill-tag {
        display: inline-block;
        padding: 7px 14px;
        border-radius: 24px;
        font-size: 0.82rem;
        font-weight: 700;
        margin: 5px;
        letter-spacing: 0.02em;
        text-transform: capitalize;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .skill-matched {
        background: rgba(16, 185, 129, 0.12) !important;
        color: #10b981 !important; /* Vivid theme-agnostic green */
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }
    .skill-matched:hover {
        background: rgba(16, 185, 129, 0.2) !important;
        transform: translateY(-2px) scale(1.02);
    }
    
    .skill-missing {
        background: rgba(245, 158, 11, 0.12) !important;
        color: #f59e0b !important; /* Vivid theme-agnostic amber */
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
    }
    .skill-missing:hover {
        background: rgba(245, 158, 11, 0.2) !important;
        transform: translateY(-2px) scale(1.02);
    }
    
    /* Unified custom button styling for ALL button containers in Streamlit */
    div.stButton > button,
    div.stDownloadButton > button,
    div.stFormSubmitButton > button {
        background-color: #2563eb !important; /* Solid accent royal blue */
        color: #ffffff !important; /* Bright white text */
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15) !important;
        width: 100% !important;
        text-align: center !important;
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    div.stButton > button:hover,
    div.stDownloadButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background-color: #1d4ed8 !important; /* Darker blue on hover */
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        transform: translateY(-1px) !important;
    }
    
    div.stButton > button:active,
    div.stDownloadButton > button:active,
    div.stFormSubmitButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Guarantee bright white text labels on all customized action buttons */
    div.stButton > button p,
    div.stDownloadButton > button p,
    div.stFormSubmitButton > button p,
    div.stButton > button span,
    div.stDownloadButton > button span,
    div.stFormSubmitButton > button span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* High-end rating card design (Theme-Adaptive) */
    .metric-container {
        background: var(--secondary-background-color) !important;
        border-radius: 20px;
        padding: 28px 24px;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
        text-align: center;
        max-width: 330px;
        margin: 15px auto;
        transition: all 0.3s ease;
    }
    .metric-container:hover {
        border-color: rgba(59, 130, 246, 0.3) !important;
        transform: translateY(-2px);
    }
    .metric-title {
        color: var(--text-color) !important;
        opacity: 0.8;
        margin-bottom: 8px;
        font-size: 1.0rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 4.0rem !important;
        font-weight: 800 !important;
        background: linear-gradient(to right, #3b82f6, #60a5fa, #2563eb) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        margin: 8px 0 !important;
        letter-spacing: -0.04em !important;
        filter: drop-shadow(0 2px 8px rgba(37, 99, 235, 0.12)) !important;
    }
    .metric-label {
        font-size: 0.95rem !important;
        line-height: 1.4 !important;
        padding: 4px 8px !important;
        border-radius: 8px !important;
    }
    
    /* Clean expander headers styling (Theme-Adaptive) */
    .streamlit-expanderHeader {
        background-color: var(--secondary-background-color) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 10px !important;
        color: var(--text-color) !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure API key directly from environment variable
effective_api_key = os.getenv("GEMINI_API_KEY")

# --- MAIN PAGE LAYOUT ---
st.markdown('<div class="header-gradient">HireNova</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Transform your resume into a laser-focused, ATS-optimized ticket to your dream interview.</div>', unsafe_allow_html=True)

# Render Single-Page Main Optimization Interface
col_input, col_results = st.columns([1, 1], gap="medium")

with col_input:
    st.markdown("### 📤 Upload & Analyze")
    
    # Resume File Uploader (Max 10MB limit)
    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"],
        help="Supported formats: PDF (.pdf) and Microsoft Word (.docx) - Max 10MB"
    )
    
    # Enforce 10MB file size limit
    if resume_file:
        if resume_file.size > 10 * 1024 * 1024:
            st.error("❌ The uploaded file exceeds the 10MB size limit. Please upload a smaller resume.")
            resume_file = None
    
    # Job Description Text Area
    jd_text = st.text_area(
        "Paste Job Description",
        height=250,
        placeholder="Paste the full job posting text here to analyze keyword matches..."
    )
    
    # Hidden parsing state
    resume_parsed_text = ""
    
    if resume_file:
        # Parse resume file
        file_ext = resume_file.name.split(".")[-1].lower()
        with st.spinner("Extracting text from resume..."):
            if file_ext == "pdf":
                resume_parsed_text = read_pdf(resume_file)
            elif file_ext == "docx":
                resume_parsed_text = read_docx(resume_file)
                
        if resume_parsed_text.startswith("Error"):
            st.error(resume_parsed_text)
            resume_parsed_text = ""
        else:
            st.success(f"Successfully parsed: {resume_file.name}")
            # Optional preview
            with st.expander("View Extracted Resume Text (Preview)"):
                st.text_area("Extracted Content", resume_parsed_text[:2000] + "...", height=150, disabled=True)
    
    # Analyze Button
    analyze_btn = st.button("Analyze Resume & JD")
    
with col_results:
    st.markdown("### 📈 ATS Compatibility Analysis")
    
    # Set states in session_state to avoid losing variables on re-run
    if 'analysis_run' not in st.session_state:
        st.session_state.analysis_run = False
        st.session_state.score = 0
        st.session_state.matched = []
        st.session_state.missing = []
        st.session_state.resume_text_cache = ""
        st.session_state.jd_text_cache = ""
        st.session_state.filename_cache = ""
        st.session_state.optimized_resume = ""
        st.session_state.pdf_generated = False
        
    if analyze_btn:
        if not resume_parsed_text:
            st.warning("Please upload a valid PDF or Word resume first.")
        elif not jd_text.strip():
            st.warning("Please paste the job description to run comparisons.")
        else:
            # Save caches
            st.session_state.resume_text_cache = resume_parsed_text
            st.session_state.jd_text_cache = jd_text
            st.session_state.filename_cache = resume_file.name
            
            # Extract skills from both text bodies
            resume_skills = extract_skills(st.session_state.resume_text_cache)
            jd_skills = extract_skills(st.session_state.jd_text_cache)
            
            # Compare skills
            matched, missing = compare_skills(resume_skills, jd_skills)
            
            # ATS Score
            score = ats_score(matched, len(jd_skills))
            
            # Save results to session state
            st.session_state.score = score
            st.session_state.matched = matched
            st.session_state.missing = missing
            st.session_state.analysis_run = True
            
            st.session_state.optimized_resume = ""
            st.session_state.pdf_generated = False
    
    # Display analysis results if available
    if st.session_state.analysis_run:
        score = st.session_state.score
        
        # Determine rating label & theme-agnostic colors
        if score >= 80:
            rating = "Excellent ATS Match! ready to apply."
            text_color = "#10b981"
        elif score >= 50:
            rating = "Moderate Match. Tailoring recommended to pass the ATS."
            text_color = "#f59e0b"
        else:
            rating = "Low Match. Highly recommended to inject missing skills."
            text_color = "#ef4444"
            
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">ATS Match Rating</div>
            <div class="metric-value">{score}%</div>
            <div class="metric-label" style="color: {text_color}; font-weight:600;">{rating}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Skill Breakdown
        st.markdown("#### Key Skill Matching")
        
        # Matched terms
        st.markdown(f"**✅ Matched Keywords ({len(st.session_state.matched)}):**")
        if st.session_state.matched:
            tags_html = "".join([f'<span class="skill-tag skill-matched">{skill}</span>' for skill in st.session_state.matched])
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.markdown("*No matching keywords identified in your resume. Check your spelling or formatting.*")
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Missing terms
        st.markdown(f"**⚠️ Missing Keywords ({len(st.session_state.missing)}):**")
        if st.session_state.missing:
            tags_html = "".join([f'<span class="skill-tag skill-missing">{skill}</span>' for skill in st.session_state.missing])
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.markdown("*Congratulations! You have 100% skill keyword coverage for this job description.*")
            
        st.markdown("<hr style='border-color: rgba(148, 163, 184, 0.2);' />", unsafe_allow_html=True)
        
        # --- AI OPTIMIZER TRIGGER ---
        st.markdown("### 🤖 Tailor & Optimize Resume with AI")
        st.markdown("Incorporate missing keywords and optimize bullets using STAR formatting powered by Gemini 2.5 Flash.")
        
        # Check for API Key
        if not effective_api_key:
            st.warning("⚠️ Gemini API Key not configured. Please check the GEMINI_API_KEY in your .env file or Streamlit Cloud Secrets to enable AI optimization.")
        
        # Tailor button
        tailor_btn = st.button("Generate Tailored Resume", disabled=not effective_api_key)
        
        if tailor_btn and effective_api_key:
            with st.spinner("Gemini AI is tailoring your resume... This may take up to 20 seconds."):
                optimized_text = optimize_resume(
                    st.session_state.resume_text_cache, 
                    st.session_state.jd_text_cache, 
                    effective_api_key
                )
                
                if optimized_text.startswith("Error"):
                    st.error(optimized_text)
                else:
                    st.session_state.optimized_resume = optimized_text
                    st.success("Successfully optimized resume! Preview below.")
                    
                    # Instantly trigger PDF compilation
                    pdf_path = "generated/resume.pdf"
                    with st.spinner("Generating styled PDF document..."):
                        success = create_pdf(optimized_text, pdf_path)
                        if success:
                            st.session_state.pdf_generated = True
                        else:
                            st.error("Could not compile styled PDF. Using backup text output.")

    else:
        st.info("Upload your resume and paste the job description on the left, then click 'Analyze Resume & JD' to see details.")
        
# Show optimized resume preview and download button in a full-width container below
if st.session_state.optimized_resume:
    st.markdown("<hr style='margin-top: 30px; border-color: rgba(148, 163, 184, 0.2);' />", unsafe_allow_html=True)
    st.markdown("### 📝 Tailored Resume Preview & Download")
    
    col_preview, col_dl = st.columns([2, 1])
    
    with col_preview:
        with st.container():
            st.markdown("""
            <div style="background-color: var(--secondary-background-color); border: 1px solid rgba(148, 163, 184, 0.2); padding: 25px; border-radius: 16px; max-height: 500px; overflow-y: scroll; box-shadow: 0 10px 25px rgba(0,0,0,0.03);">
                <style>
                    /* Style text inside preview sheet to always match current theme colors */
                    div[data-testid="stMarkdownContainer"] {
                        color: var(--text-color) !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.optimized_resume)
            st.markdown("</div>", unsafe_allow_html=True)
            
    with col_dl:
        st.markdown("#### Get Your Tailored Resume")
        st.markdown("Your optimized resume is ready for download as a professional, ATS-compliant PDF with modern design and spacing.")
        
        if st.session_state.pdf_generated and os.path.exists("generated/resume.pdf"):
            with open("generated/resume.pdf", "rb") as file:
                st.download_button(
                    label="📥 Download Tailored Resume PDF",
                    data=file,
                    file_name=f"Tailored_Resume_{st.session_state.filename_cache.replace('.pdf', '').replace('.docx', '')}.pdf",
                    mime="application/pdf"
                )
            st.info("💡 Open the downloaded PDF in your preferred viewer. It has been pre-formatted with professional standard margins (0.5 inch) and typography.")
        else:
            st.error("Error generating PDF file. You can copy the markdown text preview directly.")
