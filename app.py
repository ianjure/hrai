import pandas as pd
import streamlit as st
from PIL import Image
from utils import extract_text, summarize_resume, score_resume

# INITIALIZE GEMINI API KEY
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# PAGE CONFIGURATION
icon = Image.open("icon.png")
st.set_page_config(page_title="WorkFit AI", layout="wide", page_icon=icon)
st.logo("logo.svg")
with open( "style.css" ) as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# HANDLING SESSION STATES
if 'job_description' not in st.session_state:
    st.session_state.job_description = None
if 'resume_files' not in st.session_state:
    st.session_state.resume_files = None
if 'results_table' not in st.session_state:
    st.session_state.results_table = None
if 'top_results' not in st.session_state:
    st.session_state.top_results = None
if 'run_button' in st.session_state and st.session_state.run_button == True:
    st.session_state.running = True
else:
    st.session_state.running = False

# MAIN USER INTERFACE
st.markdown("<h2 style='text-align: center; padding-bottom: 0; margin-top: -0.5rem;'>HR Resume Screening Assistance Tool</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='font-size: 1.2rem; text-align: center; font-weight: 300; margin-top: -0.5rem;'>Analyze and rank applications in seconds!</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.05,1,0.05])
with col2:
    with st.container(border=True):
        job_description = st.text_area("**Job Description**", height=200,
                                       help="Provide a detailed job description.")
        resume_files = st.file_uploader("**Upload the Resume/s**", type=['pdf'],
                                        help="PDF files only.",
                                        accept_multiple_files=True)
        
        col1_b, col2_b, col3_b = st.columns([0.6,1,0.6])
        with col2_b:
            if job_description and resume_files:
                automate_button = st.button("**AUTOMATE SCREENING**", disabled=st.session_state.running,
                                            key='run_button', type="primary", use_container_width=True)
            else:
                automate_button = st.button("**AUTOMATE SCREENING**", disabled=True,
                                            type="primary", use_container_width=True)

    # WHEN BUTTON IS CLICKED
    if automate_button:
        st.session_state.job_description = job_description
        st.session_state.resume_files = resume_files

        with st.spinner("Analyzing and ranking the applicants. Please wait."):
            name_list = []
            summary_list = []
            score_list = []
            analysis_list = []
        
            # LOOP THROUGH ALL THE RESUME
            for resume in resume_files:
                
                # EXTRACT APPLICANT NAME
                applicant_name = resume.name.replace(".pdf", "")
                name_list.append(applicant_name)
        
                # EXTRACT TEXT AND SUMMARIZE RESUME CONTENT
                content = extract_text(resume)
                content_summary = summarize_resume(content, GOOGLE_API_KEY)
                summary_list.append(content_summary)
        
                # GENERATE RESUME SCORE AND ANALYSIS
                resume_score, resume_analysis = score_resume(content_summary, job_description, GOOGLE_API_KEY)
                score_list.append(resume_score)
                analysis_list.append(resume_analysis)
        
        # CREATE AND SHOW DATAFRAME FROM THE SUMMARIES, SCORES, AND DESCRIPTIONS
        results_table = pd.DataFrame({"Name": name_list,
                           "Summary": summary_list,
                           "Analysis": analysis_list,
                           "Score": score_list,})
        results_table = results_table.sort_values(by="Score", ascending=False)
        results_table = results_table.set_index("Name")
        st.table(results_table.head())

        st.session_state.generated = True
        st.session_state.results_table = results_table
        st.session_state.top_results = results_table.head()

        show_col, export_col = st.columns(2)
        with show_col:
            show_button = st.button("**SHOW ALL RESULTS**", type="secondary", use_container_width=True)
        with export_col:
            export_button = st.button("**EXPORT AS CSV**", type="secondary", use_container_width=True)
