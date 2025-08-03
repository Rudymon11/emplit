from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Academic Jobs API", description="API for London Academic Job Aggregation")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/academic_jobs')
client = AsyncIOMotorClient(MONGO_URL)
db = client.academic_jobs

# Pydantic models
class JobCreate(BaseModel):
    title: str
    university: str
    description: str
    url: str
    location: str = "London, UK"
    deadline: Optional[str] = None
    category: Optional[str] = "General"
    summary: Optional[str] = None

class Job(JobCreate):
    id: str
    date_added: datetime
    is_active: bool = True

class JobSource(BaseModel):
    id: str
    name: str
    url: str
    location: str
    scrape_pattern: dict
    is_active: bool = True

# Routes
@app.get("/")
async def root():
    return {"message": "Academic Jobs API for London", "status": "active"}

@app.get("/api/jobs", response_model=List[Job])
async def get_jobs(
    location: Optional[str] = Query("London", description="Filter by location"),
    category: Optional[str] = Query(None, description="Filter by category"),
    university: Optional[str] = Query(None, description="Filter by university"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    limit: int = Query(50, description="Number of jobs to return"),
    skip: int = Query(0, description="Number of jobs to skip")
):
    """Get jobs with optional filtering"""
    try:
        # Build query
        query = {"is_active": True}
        
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
            
        if university:
            query["university"] = {"$regex": university, "$options": "i"}
            
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"summary": {"$regex": search, "$options": "i"}}
            ]
        
        # Execute query
        cursor = db.jobs.find(query).sort("date_added", -1).skip(skip).limit(limit)
        jobs = []
        
        async for job in cursor:
            job["id"] = job.pop("_id")
            jobs.append(Job(**job))
        
        return jobs
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="Error fetching jobs")

@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get a specific job by ID"""
    try:
        job = await db.jobs.find_one({"_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job["id"] = job.pop("_id")
        return Job(**job)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching job")

@app.post("/api/jobs", response_model=Job)
async def create_job(job: JobCreate):
    """Create a new job posting"""
    try:
        job_dict = job.dict()
        job_dict["id"] = str(uuid.uuid4())
        job_dict["_id"] = job_dict["id"]
        job_dict["date_added"] = datetime.utcnow()
        job_dict["is_active"] = True
        
        await db.jobs.insert_one(job_dict)
        
        job_dict.pop("_id")
        return Job(**job_dict)
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail="Error creating job")

@app.get("/api/stats")
async def get_stats():
    """Get job statistics"""
    try:
        total_jobs = await db.jobs.count_documents({"is_active": True})
        london_jobs = await db.jobs.count_documents({"is_active": True, "location": {"$regex": "London", "$options": "i"}})
        
        # Get top categories
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_categories = []
        async for cat in db.jobs.aggregate(pipeline):
            top_categories.append({"category": cat["_id"], "count": cat["count"]})
        
        # Get top universities
        pipeline = [
            {"$match": {"is_active": True, "location": {"$regex": "London", "$options": "i"}}},
            {"$group": {"_id": "$university", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_universities = []
        async for uni in db.jobs.aggregate(pipeline):
            top_universities.append({"university": uni["_id"], "count": uni["count"]})
        
        return {
            "total_jobs": total_jobs,
            "london_jobs": london_jobs,
            "top_categories": top_categories,
            "top_universities": top_universities
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Error fetching statistics")

@app.get("/api/sources", response_model=List[JobSource])
async def get_sources():
    """Get all job sources"""
    try:
        cursor = db.sources.find({"is_active": True})
        sources = []
        
        async for source in cursor:
            source["id"] = source.pop("_id")
            sources.append(JobSource(**source))
        
        return sources
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail="Error fetching sources")

@app.post("/api/sources", response_model=JobSource)
async def create_source(source: dict):
    """Create a new job source"""
    try:
        source["id"] = str(uuid.uuid4())
        source["_id"] = source["id"]
        source["is_active"] = True
        
        await db.sources.insert_one(source)
        
        source.pop("_id")
        return JobSource(**source)
    except Exception as e:
        logger.error(f"Error creating source: {e}")
        raise HTTPException(status_code=500, detail="Error creating source")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)