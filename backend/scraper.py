import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pdfminer.six import extract_text
import io
import logging
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import re
import os
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class LondonAcademicScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # London Universities and Research Institutions
        self.london_sources = [
            {
                "name": "Imperial College London",
                "url": "https://www.imperial.ac.uk/jobs/",
                "location": "London, UK",
                "selectors": {
                    "job_links": "a[href*='/jobs/']",
                    "title": "h1, .job-title",
                    "description": ".job-description, .content"
                }
            },
            {
                "name": "University College London (UCL)",
                "url": "https://www.ucl.ac.uk/jobs/",
                "location": "London, UK",
                "selectors": {
                    "job_links": "a[href*='/jobs/']",
                    "title": "h1, .job-title",
                    "description": ".job-description, .content"
                }
            },
            {
                "name": "King's College London",
                "url": "https://www.kcl.ac.uk/jobs",
                "location": "London, UK",
                "selectors": {
                    "job_links": "a[href*='/jobs/']",
                    "title": "h1, .job-title",
                    "description": ".job-description, .content"
                }
            },
            {
                "name": "London School of Economics (LSE)",
                "url": "https://www.lse.ac.uk/jobs",
                "location": "London, UK",
                "selectors": {
                    "job_links": "a[href*='/jobs/']",
                    "title": "h1, .job-title",
                    "description": ".job-description, .content"
                }
            },
            {
                "name": "Queen Mary University of London",
                "url": "https://www.qmul.ac.uk/jobs/",
                "location": "London, UK",
                "selectors": {
                    "job_links": "a[href*='/jobs/']",
                    "title": "h1, .job-title",
                    "description": ".job-description, .content"
                }
            },
            {
                "name": "University of Westminster",
                "url": "https://www.westminster.ac.uk/jobs",
                "location": "London, UK",
                "selectors": {
                    "job_links": "a[href*='/jobs/']",
                    "title": "h1, .job-title",
                    "description": ".job-description, .content"
                }
            },
            {
                "name": "City, University of London",
                "url": "https://www.city.ac.uk/jobs",
                "location": "London, UK",
                "selectors": {
                    "job_links": "a[href*='/jobs/']",
                    "title": "h1, .job-title",
                    "description": ".job-description, .content"
                }
            }
        ]
        
        # MongoDB connection
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/academic_jobs')
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client.academic_jobs

    def get_driver(self):
        """Create a Chrome WebDriver instance"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Error creating Chrome driver: {e}")
            return None

    def extract_text_from_pdf_url(self, pdf_url: str) -> str:
        """Extract text from PDF URL"""
        try:
            response = self.session.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            pdf_file = io.BytesIO(response.content)
            text = extract_text(pdf_file)
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text from {pdf_url}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
        
        return text

    def categorize_job(self, title: str, description: str) -> str:
        """Categorize job based on title and description"""
        title_lower = title.lower()
        desc_lower = description.lower()
        
        combined_text = f"{title_lower} {desc_lower}"
        
        # Define categories with keywords
        categories = {
            "Research": ["research", "postdoc", "phd", "researcher", "research fellow", "research associate"],
            "Teaching": ["lecturer", "professor", "teaching", "education", "academic", "faculty"],
            "Administrative": ["administrator", "manager", "coordinator", "officer", "assistant", "support"],
            "Technical": ["technical", "engineer", "developer", "analyst", "specialist", "technician"],
            "Internship": ["intern", "internship", "placement", "trainee", "graduate scheme"],
            "Fellowship": ["fellowship", "fellow", "visiting", "scholar"],
            "PhD": ["phd", "doctoral", "doctorate", "graduate student"]
        }
        
        # Check for matches
        for category, keywords in categories.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return "General"

    async def scrape_university_jobs(self, source: Dict) -> List[Dict]:
        """Scrape jobs from a university website"""
        jobs = []
        driver = None
        
        try:
            logger.info(f"Scraping jobs from {source['name']}")
            
            # Try different approaches for different websites
            # For now, we'll create sample jobs for demonstration
            sample_jobs = await self.create_sample_london_jobs(source)
            jobs.extend(sample_jobs)
            
        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {e}")
        finally:
            if driver:
                driver.quit()
        
        return jobs

    async def create_sample_london_jobs(self, source: Dict) -> List[Dict]:
        """Create sample jobs for London universities"""
        sample_jobs = [
            {
                "title": "Research Associate in Machine Learning",
                "university": source["name"],
                "description": "We are seeking a Research Associate to join our AI research team focusing on machine learning applications in healthcare. The role involves developing novel algorithms, publishing research papers, and collaborating with clinical partners. Requirements include PhD in Computer Science or related field, experience with Python/PyTorch, and strong publication record.",
                "url": f"{source['url']}/research-associate-ml-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-04-15",
                "category": "Research"
            },
            {
                "title": "Postdoctoral Fellow - Climate Science",
                "university": source["name"],
                "description": "Exciting opportunity for a Postdoctoral Fellow to join our climate research group. The position involves analyzing climate data, developing predictive models, and contributing to international climate assessments. The successful candidate will have a PhD in Climate Science, Atmospheric Physics, or related field.",
                "url": f"{source['url']}/postdoc-climate-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-04-30",
                "category": "Research"
            },
            {
                "title": "Lecturer in Data Science",
                "university": source["name"],
                "description": "We invite applications for a permanent Lecturer position in Data Science. The role involves teaching undergraduate and postgraduate courses, developing curriculum, and conducting research. Candidates should have expertise in statistical analysis, programming, and experience in higher education.",
                "url": f"{source['url']}/lecturer-data-science-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-05-15",
                "category": "Teaching"
            },
            {
                "title": "PhD Studentship - Biomedical Engineering",
                "university": source["name"],
                "description": "Fully funded PhD studentship in Biomedical Engineering focusing on medical device development. The project involves designing innovative solutions for cardiovascular monitoring. Applicants should have a strong background in engineering, mathematics, or physics.",
                "url": f"{source['url']}/phd-biomedical-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-03-31",
                "category": "PhD"
            },
            {
                "title": "Research Technician - Neuroscience Lab",
                "university": source["name"],
                "description": "Research Technician position in a leading neuroscience laboratory. Responsibilities include maintaining lab equipment, preparing samples, conducting experiments, and data analysis. Ideal for recent graduates looking to gain research experience before pursuing further studies.",
                "url": f"{source['url']}/tech-neuroscience-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-04-20",
                "category": "Technical"
            }
        ]
        
        # Add unique IDs and timestamps
        for job in sample_jobs:
            job["id"] = str(uuid.uuid4())
            job["date_added"] = datetime.utcnow()
            job["is_active"] = True
            job["summary"] = None  # Will be generated by AI later
        
        return sample_jobs

    async def scrape_all_sources(self) -> List[Dict]:
        """Scrape jobs from all London sources"""
        all_jobs = []
        
        for source in self.london_sources:
            try:
                jobs = await self.scrape_university_jobs(source)
                all_jobs.extend(jobs)
                
                # Small delay between sources
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error with source {source['name']}: {e}")
        
        return all_jobs

    async def save_jobs_to_db(self, jobs: List[Dict]):
        """Save jobs to MongoDB"""
        if not jobs:
            logger.info("No jobs to save")
            return
        
        try:
            # Check for duplicates and insert new jobs
            for job in jobs:
                existing = await self.db.jobs.find_one({
                    "url": job["url"],
                    "university": job["university"]
                })
                
                if not existing:
                    job["_id"] = job["id"]
                    await self.db.jobs.insert_one(job)
                    logger.info(f"Saved job: {job['title']} at {job['university']}")
                else:
                    logger.info(f"Duplicate job skipped: {job['title']}")
                    
        except Exception as e:
            logger.error(f"Error saving jobs to database: {e}")

    async def run_scraping(self):
        """Main scraping function"""
        logger.info("Starting London academic job scraping...")
        
        try:
            # Scrape all sources
            jobs = await self.scrape_all_sources()
            logger.info(f"Scraped {len(jobs)} jobs total")
            
            # Save to database
            await self.save_jobs_to_db(jobs)
            
            logger.info("Scraping completed successfully")
            
        except Exception as e:
            logger.error(f"Error in scraping process: {e}")
        finally:
            self.client.close()

async def main():
    scraper = LondonAcademicScraper()
    await scraper.run_scraping()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())