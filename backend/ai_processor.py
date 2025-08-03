import os
import httpx
import logging
from typing import Optional, Dict
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class AIJobProcessor:
    def __init__(self):
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
        # MongoDB connection
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/academic_jobs')
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client.academic_jobs
        
        if not self.openrouter_api_key or self.openrouter_api_key == "your_openrouter_key_here":
            logger.warning("OpenRouter API key not set. AI features will be disabled.")
            self.api_enabled = False
        else:
            self.api_enabled = True

    async def summarize_job_description(self, title: str, description: str, university: str) -> Optional[str]:
        """Generate a concise summary of the job description using AI"""
        if not self.api_enabled:
            return self.generate_basic_summary(title, description)
        
        try:
            prompt = f"""
            Please create a concise, professional summary (2-3 sentences) of this academic job posting:

            Job Title: {title}
            University: {university}
            
            Description: {description[:1500]}...
            
            Focus on:
            - Key responsibilities and requirements
            - Required qualifications
            - What makes this opportunity attractive
            
            Keep it under 150 words and professional.
            """
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3-haiku",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 200,
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    summary = result["choices"][0]["message"]["content"].strip()
                    return summary
                else:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return self.generate_basic_summary(title, description)
                    
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return self.generate_basic_summary(title, description)

    def generate_basic_summary(self, title: str, description: str) -> str:
        """Generate a basic summary without AI"""
        # Extract first few sentences or key points
        sentences = description.split('. ')
        
        if len(sentences) >= 2:
            summary = '. '.join(sentences[:2]) + '.'
        else:
            summary = description[:200] + "..." if len(description) > 200 else description
        
        return summary

    async def categorize_job_with_ai(self, title: str, description: str) -> str:
        """Categorize job using AI analysis"""
        if not self.api_enabled:
            return self.basic_categorization(title, description)
        
        try:
            prompt = f"""
            Categorize this academic job posting into ONE of these categories:
            - Research
            - Teaching  
            - Administrative
            - Technical
            - Internship
            - Fellowship
            - PhD
            
            Job Title: {title}
            Description: {description[:800]}...
            
            Respond with just the category name.
            """
            
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3-haiku",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 10,
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    category = result["choices"][0]["message"]["content"].strip()
                    
                    # Validate category
                    valid_categories = ["Research", "Teaching", "Administrative", "Technical", "Internship", "Fellowship", "PhD"]
                    if category in valid_categories:
                        return category
                    else:
                        return self.basic_categorization(title, description)
                else:
                    return self.basic_categorization(title, description)
                    
        except Exception as e:
            logger.error(f"Error categorizing with AI: {e}")
            return self.basic_categorization(title, description)

    def basic_categorization(self, title: str, description: str) -> str:
        """Basic rule-based categorization"""
        title_lower = title.lower()
        desc_lower = description.lower()
        combined = f"{title_lower} {desc_lower}"
        
        if any(word in combined for word in ["research", "postdoc", "research associate", "research fellow"]):
            return "Research"
        elif any(word in combined for word in ["lecturer", "professor", "teaching", "faculty"]):
            return "Teaching"
        elif any(word in combined for word in ["phd", "doctoral", "doctorate"]):
            return "PhD"
        elif any(word in combined for word in ["fellowship", "fellow"]):
            return "Fellowship"
        elif any(word in combined for word in ["intern", "internship", "trainee"]):
            return "Internship"
        elif any(word in combined for word in ["technical", "engineer", "analyst", "developer"]):
            return "Technical"
        elif any(word in combined for word in ["administrator", "manager", "coordinator", "officer"]):
            return "Administrative"
        else:
            return "General"

    async def process_unprocessed_jobs(self):
        """Process jobs that don't have AI-generated summaries"""
        try:
            # Find jobs without summaries
            cursor = self.db.jobs.find({
                "is_active": True,
                "$or": [
                    {"summary": None},
                    {"summary": {"$exists": False}}
                ]
            }).limit(10)  # Process in batches
            
            processed_count = 0
            
            async for job in cursor:
                try:
                    # Generate summary
                    summary = await self.summarize_job_description(
                        job["title"],
                        job["description"],
                        job["university"]
                    )
                    
                    # Update category if needed
                    if not job.get("category") or job.get("category") == "General":
                        category = await self.categorize_job_with_ai(
                            job["title"],
                            job["description"]
                        )
                    else:
                        category = job["category"]
                    
                    # Update job in database
                    await self.db.jobs.update_one(
                        {"_id": job["_id"]},
                        {
                            "$set": {
                                "summary": summary,
                                "category": category
                            }
                        }
                    )
                    
                    processed_count += 1
                    logger.info(f"Processed job: {job['title']} at {job['university']}")
                    
                    # Small delay to respect API limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing job {job.get('title', 'Unknown')}: {e}")
            
            logger.info(f"AI processing completed. Processed {processed_count} jobs.")
            
        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
        finally:
            self.client.close()

async def main():
    processor = AIJobProcessor()
    await processor.process_unprocessed_jobs()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())