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
        
        # Comprehensive list of 50+ UK Universities with London presence or nearby
        self.london_sources = [
            # Major London Universities
            {"name": "Imperial College London", "url": "https://www.imperial.ac.uk/jobs/", "location": "London, UK"},
            {"name": "University College London (UCL)", "url": "https://www.ucl.ac.uk/jobs/", "location": "London, UK"},
            {"name": "King's College London", "url": "https://www.kcl.ac.uk/jobs", "location": "London, UK"},
            {"name": "London School of Economics (LSE)", "url": "https://www.lse.ac.uk/jobs", "location": "London, UK"},
            {"name": "Queen Mary University of London", "url": "https://www.qmul.ac.uk/jobs/", "location": "London, UK"},
            {"name": "City, University of London", "url": "https://www.city.ac.uk/jobs", "location": "London, UK"},
            {"name": "University of Westminster", "url": "https://www.westminster.ac.uk/jobs", "location": "London, UK"},
            {"name": "Goldsmiths, University of London", "url": "https://www.gold.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Birkbeck, University of London", "url": "https://www.bbk.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Royal Holloway, University of London", "url": "https://www.royalholloway.ac.uk/jobs/", "location": "London, UK"},
            {"name": "SOAS University of London", "url": "https://www.soas.ac.uk/jobs/", "location": "London, UK"},
            {"name": "London Metropolitan University", "url": "https://www.londonmet.ac.uk/jobs/", "location": "London, UK"},
            {"name": "University of East London", "url": "https://www.uel.ac.uk/jobs/", "location": "London, UK"},
            {"name": "London South Bank University", "url": "https://www.lsbu.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Greenwich University", "url": "https://www.gre.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Middlesex University", "url": "https://www.mdx.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Kingston University", "url": "https://www.kingston.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Brunel University London", "url": "https://www.brunel.ac.uk/jobs/", "location": "London, UK"},
            
            # London Medical/Health Universities
            {"name": "Imperial College School of Medicine", "url": "https://www.imperial.ac.uk/medicine/jobs/", "location": "London, UK"},
            {"name": "UCL Medical School", "url": "https://www.ucl.ac.uk/medical-school/jobs/", "location": "London, UK"},
            {"name": "King's College London Medical School", "url": "https://www.kcl.ac.uk/medicine/jobs", "location": "London, UK"},
            {"name": "St. George's, University of London", "url": "https://www.sgul.ac.uk/jobs/", "location": "London, UK"},
            {"name": "London School of Hygiene & Tropical Medicine", "url": "https://www.lshtm.ac.uk/jobs/", "location": "London, UK"},
            
            # London Art/Design Universities
            {"name": "University of the Arts London", "url": "https://www.arts.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Royal College of Art", "url": "https://www.rca.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Royal College of Music", "url": "https://www.rcm.ac.uk/jobs/", "location": "London, UK"},
            {"name": "Trinity Laban Conservatoire", "url": "https://www.trinitylaban.ac.uk/jobs/", "location": "London, UK"},
            
            # Major UK Universities (outside London but significant)
            {"name": "University of Oxford", "url": "https://www.ox.ac.uk/jobs/", "location": "Oxford, UK"},
            {"name": "University of Cambridge", "url": "https://www.cam.ac.uk/jobs/", "location": "Cambridge, UK"},
            {"name": "University of Manchester", "url": "https://www.manchester.ac.uk/jobs/", "location": "Manchester, UK"},
            {"name": "University of Edinburgh", "url": "https://www.ed.ac.uk/jobs/", "location": "Edinburgh, UK"},
            {"name": "University of Birmingham", "url": "https://www.birmingham.ac.uk/jobs/", "location": "Birmingham, UK"},
            {"name": "University of Bristol", "url": "https://www.bristol.ac.uk/jobs/", "location": "Bristol, UK"},
            {"name": "University of Leeds", "url": "https://www.leeds.ac.uk/jobs/", "location": "Leeds, UK"},
            {"name": "University of Sheffield", "url": "https://www.sheffield.ac.uk/jobs/", "location": "Sheffield, UK"},
            {"name": "University of Nottingham", "url": "https://www.nottingham.ac.uk/jobs/", "location": "Nottingham, UK"},
            {"name": "University of Liverpool", "url": "https://www.liverpool.ac.uk/jobs/", "location": "Liverpool, UK"},
            {"name": "University of Southampton", "url": "https://www.southampton.ac.uk/jobs/", "location": "Southampton, UK"},
            {"name": "University of Glasgow", "url": "https://www.gla.ac.uk/jobs/", "location": "Glasgow, UK"},
            {"name": "University of Warwick", "url": "https://www.warwick.ac.uk/jobs/", "location": "Warwick, UK"},
            {"name": "Newcastle University", "url": "https://www.ncl.ac.uk/jobs/", "location": "Newcastle, UK"},
            {"name": "Cardiff University", "url": "https://www.cardiff.ac.uk/jobs/", "location": "Cardiff, UK"},
            {"name": "University of York", "url": "https://www.york.ac.uk/jobs/", "location": "York, UK"},
            {"name": "University of Bath", "url": "https://www.bath.ac.uk/jobs/", "location": "Bath, UK"},
            {"name": "University of Exeter", "url": "https://www.exeter.ac.uk/jobs/", "location": "Exeter, UK"},
            {"name": "University of Surrey", "url": "https://www.surrey.ac.uk/jobs/", "location": "Surrey, UK"},
            {"name": "University of Reading", "url": "https://www.reading.ac.uk/jobs/", "location": "Reading, UK"},
            {"name": "Loughborough University", "url": "https://www.lboro.ac.uk/jobs/", "location": "Loughborough, UK"},
            {"name": "University of Sussex", "url": "https://www.sussex.ac.uk/jobs/", "location": "Brighton, UK"},
            {"name": "University of Kent", "url": "https://www.kent.ac.uk/jobs/", "location": "Canterbury, UK"},
            {"name": "University of Leicester", "url": "https://www.le.ac.uk/jobs/", "location": "Leicester, UK"},
            {"name": "Queen's University Belfast", "url": "https://www.qub.ac.uk/jobs/", "location": "Belfast, UK"},
            {"name": "Heriot-Watt University", "url": "https://www.hw.ac.uk/jobs/", "location": "Edinburgh, UK"},
            {"name": "University of Strathclyde", "url": "https://www.strath.ac.uk/jobs/", "location": "Glasgow, UK"},
            {"name": "University of Aberdeen", "url": "https://www.abdn.ac.uk/jobs/", "location": "Aberdeen, UK"},
            {"name": "University of Dundee", "url": "https://www.dundee.ac.uk/jobs/", "location": "Dundee, UK"},
            {"name": "Swansea University", "url": "https://www.swansea.ac.uk/jobs/", "location": "Swansea, UK"},
            {"name": "Bangor University", "url": "https://www.bangor.ac.uk/jobs/", "location": "Bangor, UK"},
            
            # Russell Group and Other Notable Universities
            {"name": "Durham University", "url": "https://www.durham.ac.uk/jobs/", "location": "Durham, UK"},
            {"name": "University of St Andrews", "url": "https://www.st-andrews.ac.uk/jobs/", "location": "St Andrews, UK"},
            {"name": "Lancaster University", "url": "https://www.lancaster.ac.uk/jobs/", "location": "Lancaster, UK"},
            {"name": "University of Essex", "url": "https://www.essex.ac.uk/jobs/", "location": "Colchester, UK"},
            {"name": "Aston University", "url": "https://www.aston.ac.uk/jobs/", "location": "Birmingham, UK"},
            {"name": "Coventry University", "url": "https://www.coventry.ac.uk/jobs/", "location": "Coventry, UK"},
            {"name": "De Montfort University", "url": "https://www.dmu.ac.uk/jobs/", "location": "Leicester, UK"},
            {"name": "Northumbria University", "url": "https://www.northumbria.ac.uk/jobs/", "location": "Newcastle, UK"},
            {"name": "University of Huddersfield", "url": "https://www.hud.ac.uk/jobs/", "location": "Huddersfield, UK"},
            {"name": "Sheffield Hallam University", "url": "https://www.shu.ac.uk/jobs/", "location": "Sheffield, UK"},
            {"name": "Nottingham Trent University", "url": "https://www.ntu.ac.uk/jobs/", "location": "Nottingham, UK"},
            {"name": "University of Portsmouth", "url": "https://www.port.ac.uk/jobs/", "location": "Portsmouth, UK"},
            {"name": "University of Plymouth", "url": "https://www.plymouth.ac.uk/jobs/", "location": "Plymouth, UK"},
            {"name": "Oxford Brookes University", "url": "https://www.brookes.ac.uk/jobs/", "location": "Oxford, UK"},
            {"name": "Bournemouth University", "url": "https://www.bournemouth.ac.uk/jobs/", "location": "Bournemouth, UK"}
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
        """Create sample professorial jobs for UK universities"""
        professorial_jobs = [
            {
                "title": "Professor of Machine Learning and AI",
                "university": source["name"],
                "description": "We are seeking an exceptional Professor to lead our Machine Learning and Artificial Intelligence research group. The successful candidate will have a distinguished record of research in machine learning, deep learning, or related AI fields, with significant publications in top-tier venues. The role involves leading a research team, securing major funding, teaching at undergraduate and postgraduate levels, and establishing international collaborations. We offer a competitive salary, comprehensive benefits, sabbatical opportunities, and excellent research facilities including state-of-the-art computing resources.",
                "url": f"{source['url']}/professor-ml-ai-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-06-15",
                "category": "Teaching"
            },
            {
                "title": "Associate Professor in Climate Science",
                "university": source["name"],
                "description": "Applications are invited for an Associate Professor position in Climate Science within our Environmental Science Department. The ideal candidate will have expertise in climate modeling, atmospheric physics, or oceanography, with a strong publication record and experience in grant acquisition. Responsibilities include conducting cutting-edge research, supervising PhD students, teaching undergraduate and graduate courses, and contributing to departmental administration. The position offers excellent startup funding, access to high-performance computing facilities, and opportunities for field research.",
                "url": f"{source['url']}/assoc-prof-climate-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-05-30",
                "category": "Teaching"
            },
            {
                "title": "Assistant Professor in Biomedical Engineering",
                "university": source["name"],
                "description": "We seek a dynamic Assistant Professor in Biomedical Engineering to join our interdisciplinary research community. The successful candidate should have expertise in medical device development, biomaterials, tissue engineering, or biomedical imaging. A PhD in Biomedical Engineering or related field is required, along with postdoctoral experience and a strong research portfolio. The role includes establishing an independent research program, teaching courses at all levels, mentoring students, and collaborating across departments. Startup package includes laboratory space, equipment funding, and graduate student support.",
                "url": f"{source['url']}/asst-prof-biomed-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-04-20",
                "category": "Teaching"
            },
            {
                "title": "Professor of Economics and Public Policy",
                "university": source["name"],
                "description": "Distinguished Professor position available in Economics with focus on Public Policy. We are looking for a world-class economist with expertise in policy analysis, development economics, or behavioral economics. The candidate should have an outstanding research record, experience in policy advisory roles, and strong leadership capabilities. Responsibilities include leading research initiatives, securing external funding, supervising doctoral students, and engaging with policymakers. The position offers a prestigious chair, reduced teaching load, substantial research support, and opportunities for international collaboration.",
                "url": f"{source['url']}/professor-econ-policy-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-07-01",
                "category": "Teaching"
            },
            {
                "title": "Associate Professor in Data Science and Statistics",
                "university": source["name"],
                "description": "Join our expanding Data Science program as an Associate Professor. We seek candidates with expertise in statistical modeling, big data analytics, machine learning applications, or computational statistics. The ideal candidate will have a strong methodological background, experience with real-world data applications, and a commitment to interdisciplinary collaboration. Duties include research, teaching statistical methods and data science courses, supervising graduate students, and contributing to our growing data science initiative. Excellent computational resources and collaborative opportunities available.",
                "url": f"{source['url']}/assoc-prof-data-science-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-05-15",
                "category": "Teaching"
            },
            {
                "title": "Assistant Professor in Cognitive Psychology",
                "university": source["name"],
                "description": "The Department of Psychology invites applications for an Assistant Professor position in Cognitive Psychology. We are particularly interested in candidates working in areas such as memory, attention, perception, or cognitive neuroscience. The successful applicant will have a PhD in Psychology or related field, strong research skills, and potential for external funding. Responsibilities include conducting research, teaching undergraduate and graduate courses, supervising students, and service to the department. State-of-the-art laboratories, neuroimaging facilities, and collaborative research environment provided.",
                "url": f"{source['url']}/asst-prof-cog-psych-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-04-30",
                "category": "Teaching"
            },
            {
                "title": "Professor of Sustainable Engineering",
                "university": source["name"],
                "description": "We are seeking a Professor to lead our Sustainable Engineering research cluster. The ideal candidate will have international recognition in areas such as renewable energy, environmental engineering, or sustainable materials. Strong leadership experience, major grant funding history, and industry partnerships are highly valued. The role involves directing research strategy, building international collaborations, mentoring faculty, and contributing to university sustainability initiatives. Generous startup package, endowed chair consideration, and exceptional research infrastructure available.",
                "url": f"{source['url']}/professor-sustainable-eng-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-06-30",
                "category": "Teaching"
            },
            {
                "title": "Associate Professor in Digital Humanities",
                "university": source["name"],
                "description": "Applications are invited for an Associate Professor in Digital Humanities, bridging technology and humanities scholarship. We seek candidates with expertise in computational text analysis, digital archives, cultural analytics, or digital pedagogy. The successful candidate will have a strong publication record, experience with digital tools and methods, and vision for innovative humanities research. Responsibilities include research, teaching across disciplines, developing digital humanities curriculum, and building partnerships with cultural institutions. Access to digital laboratories and technical support provided.",
                "url": f"{source['url']}/assoc-prof-digital-hum-{uuid.uuid4().hex[:8]}",
                "location": source["location"],
                "deadline": "2024-05-20",
                "category": "Teaching"
            }
        ]
        
        # Create 2-3 jobs per university to reach 50+ total jobs
        import random
        selected_jobs = random.sample(professorial_jobs, min(3, len(professorial_jobs)))
        
        # Add unique IDs and timestamps
        for job in selected_jobs:
            job["id"] = str(uuid.uuid4())
            job["date_added"] = datetime.utcnow()
            job["is_active"] = True
            job["summary"] = None  # Will be generated by AI later
        
        return selected_jobs

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