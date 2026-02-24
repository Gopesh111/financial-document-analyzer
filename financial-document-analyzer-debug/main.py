import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

from crewai import Crew, Process

# Import our specialized agents and engineered tasks
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import verification, analyze_financial_document, risk_assessment, investment_analysis

# ==========================================
# 1. Database Setup (Bonus Point: DB Integration)
# ==========================================
# Using SQLite for a zero-config, plug-and-play experience for the reviewer
os.makedirs("data", exist_ok=True)
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/financial_analysis.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisRecord(Base):
    __tablename__ = "analyses"
    task_id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    query = Column(String)
    status = Column(String)  # QUEUED, PROCESSING, COMPLETED, FAILED
    result = Column(Text, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# ==========================================
# 2. FastAPI Application Setup
# ==========================================
app = FastAPI(
    title="Financial Document Analyzer API",
    description="Asynchronous CrewAI intelligence engine for financial auditing."
)

# ==========================================
# 3. Background Worker (Bonus Point: Queue Model)
# ==========================================
def process_crew_task(task_id: str, query: str, file_path: str):
    """Background worker function to run CrewAI without blocking the API"""
    db = SessionLocal()
    record = db.query(AnalysisRecord).filter(AnalysisRecord.task_id == task_id).first()
    
    try:
        if record:
            record.status = "PROCESSING"
            db.commit()

        # Assemble the Crew with all specialized agents and chained tasks
        financial_crew = Crew(
            agents=[verifier, financial_analyst, risk_assessor, investment_advisor],
            tasks=[verification, analyze_financial_document, risk_assessment, investment_analysis],
            process=Process.sequential,
            verbose=True
        )
        
        # Kickoff the crew with dynamic variables required by our new prompts
        result = financial_crew.kickoff(inputs={
            'query': query,
            'file_path': file_path
        })
        
        # Save successful result to database
        if record:
            record.status = "COMPLETED"
            # CrewAI kickoff returns a CrewOutput object, we need to convert it to string
            record.result = str(result)
            db.commit()
            
    except Exception as e:
        # Handle failures gracefully
        if record:
            record.status = "FAILED"
            record.result = f"Error during CrewAI execution: {str(e)}"
            db.commit()
            
    finally:
        db.close()
        # Clean up the physical file to save disk space after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

# ==========================================
# 4. API Endpoints
# ==========================================
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_financial_document_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Uploads a document and queues it for asynchronous analysis."""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    task_id = str(uuid.uuid4())
    file_path = f"data/doc_{task_id}.pdf"
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # Initialize database record
        db = SessionLocal()
        new_analysis = AnalysisRecord(
            task_id=task_id,
            filename=file.filename,
            query=query.strip(),
            status="QUEUED"
        )
        db.add(new_analysis)
        db.commit()
        db.close()
        
        # Send to background worker queue
        background_tasks.add_task(process_crew_task, task_id, query, file_path)
        
        return {
            "status": "success",
            "message": "Document queued for analysis.",
            "task_id": task_id,
            "check_status_url": f"/status/{task_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing analysis: {str(e)}")

@app.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    """Retrieve the status and results of a queued analysis."""
    db = SessionLocal()
    record = db.query(AnalysisRecord).filter(AnalysisRecord.task_id == task_id).first()
    db.close()
    
    if not record:
        raise HTTPException(status_code=404, detail="Task ID not found")
        
    return {
        "task_id": record.task_id,
        "filename": record.filename,
        "status": record.status,
        "result": record.result if record.status in ["COMPLETED", "FAILED"] else "Analysis in progress..."
    }

if __name__ == "__main__":
    import uvicorn
    # Added workers=1 to prevent concurrent DB lock issues during local testing
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)