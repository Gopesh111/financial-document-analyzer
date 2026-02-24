import os
from dotenv import load_dotenv
from crewai.tools import tool
from crewai_tools import SerperDevTool

# Load environment variables (API Keys)
load_dotenv()

# ==========================================
# 1. Web Search Tool
# ==========================================
# SerperDevTool is a native CrewAI tool, no decorator needed.
search_tool = SerperDevTool()

# ==========================================
# 2. Financial Document Reader Tool
# ==========================================
@tool("Read Financial Document")
def read_financial_document(file_path: str) -> str:
    """
    Mandatory tool for reading and extracting raw text from a financial PDF document.
    You must provide the exact 'file_path' to the PDF file.
    Use this tool FIRST to gather the financial data before attempting any analysis.
    """
    # Note: Requires 'pypdf' or 'PyPDF2'. Run: pip install pypdf
    try:
        from pypdf import PdfReader
        
        full_report = ""
        reader = PdfReader(file_path)
        
        for page in reader.pages:
            content = page.extract_text()
            if content:
                # Clean extra whitespaces to save LLM context window tokens
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")
                full_report += content + "\n"
                
        if not full_report.strip():
            return "Error: Document was read, but no text could be extracted. It might be a scanned image."
            
        return full_report

    except ImportError:
        return "System Error: 'pypdf' library is missing. Please notify the system administrator to install it."
    except Exception as e:
        return f"Error reading document at {file_path}. Ensure the file exists. Details: {str(e)}"

# ==========================================
# 3. Investment Analysis Processor Tool
# ==========================================
@tool("Process Investment Data")
def analyze_investment_tool(financial_text: str) -> str:
    """
    Processes raw financial text to isolate key investment metrics.
    Pass the raw text extracted from the PDF into this tool to clean and format it 
    specifically for investment and profitability analysis.
    """
    # Clean up the data format (removing excessive whitespace)
    processed_data = " ".join(financial_text.split())
    
    # In a fully scaled app, you'd integrate NLP/Regex here to pull out specific tables.
    # For now, we format it cleanly for the LLM to process deterministically.
    return f"--- INVESTMENT DATA PRE-PROCESSED ---\nExtracted Length: {len(processed_data)} characters.\nData ready for EPS, Gross Margin, and Cash Flow extraction:\n\n{processed_data}"

# ==========================================
# 4. Risk Assessment Processor Tool
# ==========================================
@tool("Process Risk Data")
def create_risk_assessment_tool(financial_text: str) -> str:
    """
    Evaluates financial data to isolate operational, market, and liquidity risks.
    Pass the raw text extracted from the PDF into this tool to format it specifically 
     for risk auditing and liability checks.
    """
    processed_data = " ".join(financial_text.split())
    
    return f"--- RISK DATA PRE-PROCESSED ---\nExtracted Length: {len(processed_data)} characters.\nData ready for macroeconomic headwind, operational risk, and debt extraction:\n\n{processed_data}"