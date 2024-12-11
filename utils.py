import re
from pypdf import PdfReader
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def extract_text(pdf):

    # INITIALIZE PDF READER OBJECT
    reader = PdfReader(pdf)

    # INITIALIZE CONTENT VARIABLE
    content = ""

    # LOOP THROUGH THE PAGES, EXTRACT TEXT, AND APPEND TO CONTENT
    for page in reader.pages:
        text = page.extract_text()
        content += text
    
    return content

def summarize_resume(resume_content, api_key):

    # INITIALIZE GOOGLE GEMINI MODEL
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                temperature=0.5,
                                google_api_key=api_key)
    
    # INITIALIZE PROMPT TEMPLATE
    template = """
                Summarize this resume content:
                {resume_content}

                Answer directly.
                """
    prompt = PromptTemplate.from_template(template)

    # INITIALIZE LLM CHAIN
    chain = prompt | llm

    # GENERATE RESUME SUMMARY
    llm_response = chain.invoke({"resume_content": resume_content})
    result = llm_response.content

    return result

def score_resume(resume_summary, job_description, api_key):

    # INITIALIZE GOOGLE GEMINI MODEL
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                temperature=0.5,
                                google_api_key=api_key)
    
    # INITIALIZE PROMPT TEMPLATE
    template = """
                You are an AI that helps HR in screening applicant's resumes.

                Based on this resume summary:
                {resume_summary}

                Analyze if the summary fits in this job description:
                {job_description}

                And give it a score ranging from 1-100.

                Follow this format and answer directly:
                The score - Short explanation (1 paragraph)
                """
    prompt = PromptTemplate.from_template(template)

    # INITIALIZE LLM CHAIN
    chain = prompt | llm

    # GENERATE RESUME SUMMARY
    llm_response = chain.invoke({"resume_summary": resume_summary, "job_description": job_description})
    result = llm_response.content
    print(result)

    # EXTRACT SCORE AND DESCRIPTION
    score = int(result.split("-")[0].strip())
    description = result.split("-")[1]

    return score, description
