import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
from datetime import datetime

# Import services
from services.parser import read_pdf, read_docx
from services.ats_score import extract_skills, compare_skills, ats_score
from services.ai_service import optimize_resume
from services.pdf_generator import create_pdf
from services.db import init_db, save_analysis, get_history_records, clear_db

# Set page config
st.set_page_config(
    page_title="HireNova - AI Resume Tailor & ATS Optimizer",
    page_icon="⚡",
    layout="wide"
)

# Initialize database
init_db()

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)# Inject custom modern CSS for beautiful aesthetics (Glassmorphism, gradients, clean fonts)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
    
    /* 1. LOCK APPLICATION IN PREMIUM LIGHT MODE */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stApp"],
    .main,
    html, body {
        background-color: #f8fafc !important; /* Premium Slate 50 Off-White */
        color: #1e293b !important; /* Slate 800 Dark Grey Text */
        font-family: 'Inter', sans-serif;
    }
    
    /* Global font headers config */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0f172a !important; /* Slate 900 Black */
    }
    
    /* Ensure regular markdown texts are dark slate grey for excellent legibility */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stMarkdownContainer"] span {
        color: #334155 !important; /* Slate 700 */
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Header Gradient styling */
    .header-gradient {
        background: linear-gradient(135deg, #4f46e5, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.6rem !important;
        font-weight: 800;
        margin-bottom: 0.1rem;
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.03em;
        filter: drop-shadow(0 2px 6px rgba(37, 99, 235, 0.1));
    }
    
    .subtitle-text {
        color: #64748b !important; /* Slate 500 */
        font-size: 1.15rem;
        margin-bottom: 2.2rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }
    
    /* Premium Frosted Glassmorphic cards for Light Mode */
    .glass-card {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 10px 30px 0 rgba(15, 23, 42, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        margin-bottom: 22px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        box-shadow: 0 15px 35px 0 rgba(99, 102, 241, 0.06), 0 10px 30px 0 rgba(15, 23, 42, 0.06);
        transform: translateY(-2px);
    }
    
    /* File Uploader Custom Styling Wrapper (Light Mode) */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(59, 130, 246, 0.25) !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.5) !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.6) !important;
        background: rgba(99, 102, 241, 0.02) !important;
    }
    [data-testid="stFileUploader"] label {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    
    /* File Uploader buttons are styled natively by Streamlit to avoid overlapping cancel/remove layout glitches */
    
    /* Make the helper description text (Max size and types) highly visible in Light Mode */
    [data-testid="stFileUploader"] section div, 
    [data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stFileUploader"] small {
        color: #475569 !important; /* Slate 600 */
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }
    
    /* Dynamic skill tags with vibrant styling (Light Mode) */
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
        background: rgba(16, 185, 129, 0.08) !important;
        color: #065f46 !important; /* Deep Green for perfect legibility */
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        box-shadow: 0 2px 10px rgba(16, 185, 129, 0.03);
    }
    .skill-matched:hover {
        background: rgba(16, 185, 129, 0.15) !important;
        border-color: rgba(16, 185, 129, 0.45) !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.08);
        transform: translateY(-2px) scale(1.02);
    }
    
    .skill-missing {
        background: rgba(245, 158, 11, 0.08) !important;
        color: #92400e !important; /* Deep Amber/Bronze for perfect legibility */
        border: 1px solid rgba(245, 158, 11, 0.25) !important;
        box-shadow: 0 2px 10px rgba(245, 158, 11, 0.03);
    }
    .skill-missing:hover {
        background: rgba(245, 158, 11, 0.15) !important;
        border-color: rgba(245, 158, 11, 0.45) !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.08);
        transform: translateY(-2px) scale(1.02);
    }
    
    /* Premium visual buttons with animated gradient slides */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5, #2563eb, #7c3aed);
        background-size: 200% auto;
        color: white !important;
        border: none;
        padding: 12px 28px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25);
        width: 100%;
    }
    div.stButton > button:hover {
        background-position: right center;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
    }
    
    /* High-end circular rating card design (Light Mode) */
    .metric-container {
        background: linear-gradient(135deg, #ffffff, #f8fafc) !important;
        border-radius: 24px;
        padding: 32px 24px;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.03), inset 0 1px 1px rgba(255, 255, 255, 0.8);
        text-align: center;
        max-width: 330px;
        margin: 15px auto;
        transition: all 0.3s ease;
    }
    .metric-container:hover {
        border-color: rgba(59, 130, 246, 0.35) !important;
        box-shadow: 0 12px 35px rgba(59, 130, 246, 0.08), 0 10px 30px rgba(15, 23, 42, 0.05);
        transform: translateY(-3px);
    }
    .metric-title {
        color: #64748b !important; /* Muted slate */
        margin-bottom: 10px;
        font-size: 1.05rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 4.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(to right, #1d4ed8, #2563eb, #3b82f6) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        color: transparent !important;
        margin: 8px 0 !important;
        letter-spacing: -0.04em !important;
        filter: drop-shadow(0 2px 8px rgba(37, 99, 235, 0.15)) !important;
    }
    .metric-label {
        color: #334155 !important;
        font-size: 0.95rem;
        line-height: 1.4;
        padding: 4px 8px;
        border-radius: 8px;
    }
    
    /* 2. HIGH-CONTRAST SOLID LIGHT NAVIGATION TAB BAR */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        background-color: #f1f5f9 !important; /* Clean light slate background */
        padding: 8px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(15, 23, 42, 0.06) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        color: #475569 !important; /* Strong dark slate text for perfect contrast */
        transition: all 0.25s ease-in-out !important;
        font-family: 'Outfit', sans-serif !important;
        border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0f172a !important;
        background-color: rgba(15, 23, 42, 0.04) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important; /* Vibrant Indigo-Blue background for selected tab */
        color: #ffffff !important; /* Bright White text */
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        border-bottom: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure API key directly from environment variable
effective_api_key = os.getenv("GEMINI_API_KEY")

# --- MAIN PAGE LAYOUT ---
st.markdown('<div class="header-gradient">HireNova</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Transform your resume into a laser-focused, ATS-optimized ticket to your dream interview.</div>', unsafe_allow_html=True)

# Setup tabs
tab_optimizer, tab_analytics = st.tabs([
    "⚡ Resume Optimizer", 
    "📊 Analytics Dashboard"
])

# ==================== TAB 1: RESUME OPTIMIZER ====================
with tab_optimizer:
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
                
                # Trigger a clear database state if optimized is dirty
                st.session_state.optimized_resume = ""
                st.session_state.pdf_generated = False
                
                # Log score in SQL Database
                try:
                    # Parse a basic Job Title from JD (first line or dynamic fallback)
                    lines = [l.strip() for l in jd_text.split('\n') if l.strip()]
                    job_title = lines[0][:50] if lines else "Target Position"
                    save_analysis(score, resume_file.name, job_title, matched, missing)
                except Exception as db_err:
                    st.error(f"DB Logging Error: {str(db_err)}")
        
        # Display analysis results if available
        if st.session_state.analysis_run:
            # Custom styled ATS Score gauge
            score = st.session_state.score
            
            # Determine rating label
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
                
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1);' />", unsafe_allow_html=True)
            
            # --- AI OPTIMIZER TRIGGER ---
            st.markdown("### 🤖 Tailor & Optimize Resume with AI")
            st.markdown("Incorporate missing keywords and optimize bullets using STAR formatting powered by Gemini 2.5 Flash.")
            
            # Check for API Key
            if not effective_api_key:
                st.warning("⚠️ Gemini API Key not configured. Please check the GEMINI_API_KEY in your .env file to enable AI optimization.")
            
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
        st.markdown("<hr style='margin-top: 30px; border-color: rgba(255,255,255,0.1);' />", unsafe_allow_html=True)
        st.markdown("### 📝 Tailored Resume Preview & Download")
        
        col_preview, col_dl = st.columns([2, 1])
        
        with col_preview:
            with st.container():
                st.markdown("""
                <div style="background-color: #ffffff; border: 1px solid rgba(15,23,42,0.08); padding: 25px; border-radius: 16px; max-height: 500px; overflow-y: scroll; box-shadow: 0 10px 30px rgba(0,0,0,0.03);">
                    <style>
                        /* Set custom styled scrollbar and dark text for the paper resume preview sheet */
                        div[data-testid="stMarkdownContainer"] {
                            color: #1e293b !important;
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


# ==================== TAB 2: ANALYTICS DASHBOARD ====================
with tab_analytics:
    st.markdown("### 📊 Historical Analytics Dashboard")
    st.markdown("Track your resume improvement progress over time and see aggregates.")
    
    # Refresh logs
    records = get_history_records()
    
    if not records:
        st.info("No analysis history logged yet. Go to 'Resume Optimizer' and run an analysis to view charts!")
    else:
        # Load records into pandas DataFrame
        df = pd.DataFrame(records, columns=['ID', 'Score', 'Date', 'Filename', 'Job Title', 'Matched Skills', 'Missing Skills'])
        
        # Convert Date column to datetime objects
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Display aggregate KPI metrics
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        
        with col_kpi1:
            st.metric(
                label="Total Analyses Logged", 
                value=len(df),
                help="The total number of resumes tested."
            )
        with col_kpi2:
            st.metric(
                label="Highest ATS Score", 
                value=f"{df['Score'].max()}%",
                help="The maximum score achieved."
            )
        with col_kpi3:
            st.metric(
                label="Average ATS Score", 
                value=f"{int(df['Score'].mean())}%",
                help="Average rating across all logs."
            )
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Divide dashboard into visual columns
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### 📈 Compatibility Trend Over Time")
            # Line chart showing score improvement timeline
            df_sorted = df.sort_values('Date')
            fig_trend = px.line(
                df_sorted, 
                x='Date', 
                y='Score', 
                markers=True,
                labels={'Score': 'ATS Score (%)', 'Date': 'Analysis Date'},
                title="ATS Score Trend",
                template="plotly_white"
            )
            fig_trend.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                yaxis=dict(range=[0, 105])
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with col_chart2:
            st.markdown("#### 🔍 Frequently Missing vs. Matched Skills")
            
            # Calculate skills counts
            all_missing = []
            all_matched = []
            
            for index, row in df.iterrows():
                if row['Missing Skills']:
                    all_missing.extend([s.strip().lower() for s in row['Missing Skills'].split(',') if s.strip()])
                if row['Matched Skills']:
                    all_matched.extend([s.strip().lower() for s in row['Matched Skills'].split(',') if s.strip()])
                    
            missing_counts = pd.Series(all_missing).value_counts().head(8)
            matched_counts = pd.Series(all_matched).value_counts().head(8)
            
            if not missing_counts.empty:
                # Plotly Bar chart for missing skills
                fig_missing = px.bar(
                    x=missing_counts.values,
                    y=missing_counts.index,
                    orientation='h',
                    labels={'x': 'Appearances in Scans', 'y': 'Missing Skill'},
                    title="Top Missing Skills (Add these to your profile!)",
                    color_discrete_sequence=['#f59e0b'],
                    template="plotly_white"
                )
                fig_missing.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_family="Inter"
                )
                st.plotly_chart(fig_missing, use_container_width=True)
            else:
                st.markdown("*Not enough skill match history to render skill frequencies yet.*")
                
        # History Table Expandable
        st.markdown("#### 🕒 Detailed Scan Logs")
        with st.expander("Show History Log File Details"):
            st.dataframe(
                df[['Date', 'Filename', 'Job Title', 'Score', 'Matched Skills', 'Missing Skills']],
                use_container_width=True
            )
            
            # Option to Clear Database
            clear_db_btn = st.button("🗑️ Reset Analysis Database Logs")
            if clear_db_btn:
                clear_db()
                st.success("Successfully cleared all history records!")
                st.rerun()


# All requested visual cleanups have been successfully completed.
