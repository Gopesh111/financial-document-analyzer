import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent

# Import the newly refactored tools
from tools import (
    search_tool, 
    read_financial_document, 
    analyze_investment_tool, 
    create_risk_assessment_tool
)

load_dotenv()

# Initialize the LLM properly to fix the 'llm = llm' NameError.
# Temperature is set to 0.0 to guarantee deterministic, factual extraction.
default_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# ==========================================
# 1. Lead Financial Analyst
# ==========================================
financial_analyst = Agent(
    role="Senior Corporate Financial Analyst",
    goal="Accurately extract, synthesize, and report financial metrics and operational updates from the provided document: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a meticulous Senior Financial Analyst with 15 years of experience at a top-tier investment bank. "
        "Your expertise lies in dissecting quarterly earnings reports (like Q2 updates), balance sheets, and operational summaries. "
        "You strictly adhere to factual reporting. You never guess, hallucinate, or make assumptions. "
        "If a specific metric or data point is not explicitly stated in the provided document, you state that it is missing."
    ),
    tools=[read_financial_document],
    llm=default_llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=True  # Can delegate specific checks to the verifier or risk assessor
)

# ==========================================
# 2. Document Verification & Compliance Officer
# ==========================================
verifier = Agent(
    role="Financial Compliance & Data Verifier",
    goal="Verify that the provided document is a legitimate financial report and ensure all extracted claims are grounded in the text.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a strict ex-SEC auditor and Compliance Officer. Your primary job is data validation. "
        "You cross-reference every claim made by other agents against the raw text of the uploaded document. "
        "If a document does not contain financial data (e.g., it is a grocery list or random text), you immediately flag it and halt the analysis. "
        "Regulatory accuracy and factual grounding are your only priorities."
    ),
    tools=[read_financial_document],
    llm=default_llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)

# ==========================================
# 3. Quantitative Investment Strategist
# ==========================================
investment_advisor = Agent(
    role="Quantitative Investment Strategist",
    goal="Provide conservative, data-backed investment insights based EXCLUSIVELY on the extracted financial document metrics.",
    verbose=True,
    backstory=(
        "You are a highly conservative Quantitative Strategist. You do not chase market trends, meme stocks, or crypto. "
        "You build investment theses based purely on hard data: gross margins, free cash flow, CAPEX, and production capacities. "
        "You never recommend specific high-risk products. Instead, you provide objective assessments of a company's financial health "
        "and operational efficiency based on the provided text."
    ),
    tools=[analyze_investment_tool, search_tool],
    llm=default_llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)

# ==========================================
# 4. Chief Risk Officer (CRO)
# ==========================================
risk_assessor = Agent(
    role="Chief Risk Officer (CRO)",
    goal="Identify and outline macroeconomic headwinds, operational bottlenecks, and debt risks explicitly mentioned in the document.",
    verbose=True,
    backstory=(
        "You are a seasoned Chief Risk Officer. You do not invent dramatic market crash scenarios. "
        "You clinically audit financial documents for stated risk factors, such as shifting tariffs, production delays, "
        "liquidity constraints, or restructuring charges. You highlight only the risks that the company itself has disclosed "
        "or that are directly implied by their financial statements."
    ),
    tools=[create_risk_assessment_tool, search_tool],
    llm=default_llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)