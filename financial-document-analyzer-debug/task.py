from crewai import Task

# Import all our specialized agents
from agents import financial_analyst, verifier, investment_advisor, risk_assessor

# Import our refactored tools
from tools import (
    search_tool, 
    read_financial_document, 
    analyze_investment_tool, 
    create_risk_assessment_tool
)

# ==========================================
# 1. Document Verification Task
# ==========================================
verification = Task(
    description=(
        "Verify the contents of the uploaded file located at path: {file_path}. "
        "Read the document using the provided tool and determine if it is a legitimate financial report, "
        "earnings update, or corporate filing. If it is NOT a financial document, immediately halt "
        "and report the error. If it is, extract the core subject matter, the company name, and the reporting period."
    ),
    expected_output="A brief statement confirming the document's validity, the company name, and the exact reporting period.",
    agent=verifier,
    tools=[read_financial_document]
)

# ==========================================
# 2. Financial Extraction & Analysis Task
# ==========================================
analyze_financial_document = Task(
    description=(
        "Based on the verified document at {file_path}, analyze the financial data to answer the user's specific query: '{query}'. "
        "Extract key performance indicators (KPIs) such as total revenues, profit margins, delivery/production numbers, "
        "and cash flow. Focus ONLY on the hard data explicitly stated in the document. Do not invent or estimate metrics."
    ),
    expected_output="A detailed, factual, markdown-formatted breakdown of the company's financial performance relevant to the user's query.",
    agent=financial_analyst,
    tools=[read_financial_document],
    context=[verification]  # This ensures the analyst waits for the verifier to finish
)

# ==========================================
# 3. Risk Assessment Task
# ==========================================
risk_assessment = Task(
    description=(
        "Analyze the financial data from {file_path} for stated operational and market risks. "
        "Identify macroeconomic headwinds, production bottlenecks, supply chain issues, shifting tariffs, "
        "or debt liabilities explicitly mentioned by the company in the text. Do not invent catastrophic scenarios."
    ),
    expected_output="A structured, bulleted list of factual risk factors and headwinds disclosed in the document.",
    agent=risk_assessor,
    tools=[read_financial_document, create_risk_assessment_tool, search_tool],
    context=[analyze_financial_document] # Builds on the financial extraction
)

# ==========================================
# 4. Investment Synthesis Task
# ==========================================
investment_analysis = Task(
    description=(
        "Synthesize the financial performance and risk assessments to provide a conservative, data-driven investment outlook. "
        "Address the user's exact query: '{query}'. Base your conclusions entirely on the extracted metrics and stated risks. "
        "Do NOT recommend speculative trades, meme stocks, or invent financial models."
    ),
    expected_output=(
        "A professional, SEC-compliant investment summary in markdown format. Must include:\n"
        "- A clear, direct response to the user's query.\n"
        "- A summary of operational strengths based on the data.\n"
        "- A recap of identified factual risks.\n"
        "- A conservative, data-backed conclusion."
    ),
    agent=investment_advisor,
    tools=[analyze_investment_tool, search_tool],
    context=[analyze_financial_document, risk_assessment] # Requires both prior tasks to synthesize
)