import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleJobInitializer:
    def __init__(self):
        # MongoDB connection
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/academic_jobs')
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client.academic_jobs

        # 50+ UK Universities
        self.universities = [
            "Imperial College London", "University College London (UCL)", "King's College London",
            "London School of Economics (LSE)", "Queen Mary University of London", "City, University of London",
            "University of Westminster", "Goldsmiths, University of London", "Birkbeck, University of London",
            "Royal Holloway, University of London", "SOAS University of London", "London Metropolitan University",
            "University of East London", "London South Bank University", "Greenwich University",
            "Middlesex University", "Kingston University", "Brunel University London",
            "University of Oxford", "University of Cambridge", "University of Manchester",
            "University of Edinburgh", "University of Birmingham", "University of Bristol",
            "University of Leeds", "University of Sheffield", "University of Nottingham",
            "University of Liverpool", "University of Southampton", "University of Glasgow",
            "University of Warwick", "Newcastle University", "Cardiff University",
            "University of York", "University of Bath", "University of Exeter",
            "University of Surrey", "University of Reading", "Loughborough University",
            "University of Sussex", "University of Kent", "University of Leicester",
            "Queen's University Belfast", "Heriot-Watt University", "University of Strathclyde",
            "University of Aberdeen", "University of Dundee", "Swansea University",
            "Durham University", "University of St Andrews", "Lancaster University"
        ]

    async def create_professorial_jobs(self):
        """Create diverse professorial jobs across all universities"""
        
        job_templates = [
            {
                "title": "Professor of Machine Learning and AI",
                "description": "We are seeking an exceptional Professor to lead our Machine Learning and Artificial Intelligence research group. The successful candidate will have a distinguished record of research in machine learning, deep learning, or related AI fields, with significant publications in top-tier venues. The role involves leading a research team, securing major funding, teaching at undergraduate and postgraduate levels, and establishing international collaborations. We offer a competitive salary, comprehensive benefits, sabbatical opportunities, and excellent research facilities including state-of-the-art computing resources. Strong candidates will have expertise in neural networks, computer vision, natural language processing, or robotics applications.",
                "category": "Teaching"
            },
            {
                "title": "Associate Professor in Climate Science",
                "description": "Applications are invited for an Associate Professor position in Climate Science within our Environmental Science Department. The ideal candidate will have expertise in climate modeling, atmospheric physics, or oceanography, with a strong publication record and experience in grant acquisition. Responsibilities include conducting cutting-edge research, supervising PhD students, teaching undergraduate and graduate courses, and contributing to departmental administration. The position offers excellent startup funding, access to high-performance computing facilities, and opportunities for field research. Research areas of particular interest include climate change impacts, carbon cycle dynamics, and extreme weather events.",
                "category": "Teaching"
            },
            {
                "title": "Assistant Professor in Data Science",
                "description": "Join our expanding Data Science program as an Assistant Professor. We seek candidates with expertise in statistical modeling, big data analytics, machine learning applications, or computational statistics. The ideal candidate will have a strong methodological background, experience with real-world data applications, and a commitment to interdisciplinary collaboration. Duties include research, teaching statistical methods and data science courses, supervising graduate students, and contributing to our growing data science initiative. Excellent computational resources and collaborative opportunities available with industry partners and research institutes.",
                "category": "Teaching"
            },
            {
                "title": "Professor of Economics and Public Policy",
                "description": "Distinguished Professor position available in Economics with focus on Public Policy. We are looking for a world-class economist with expertise in policy analysis, development economics, or behavioral economics. The candidate should have an outstanding research record, experience in policy advisory roles, and strong leadership capabilities. Responsibilities include leading research initiatives, securing external funding, supervising doctoral students, and engaging with policymakers. The position offers a prestigious chair, reduced teaching load, substantial research support, and opportunities for international collaboration with government agencies and international organizations.",
                "category": "Teaching"
            },
            {
                "title": "Associate Professor in Biomedical Engineering",
                "description": "We seek a dynamic Associate Professor in Biomedical Engineering to join our interdisciplinary research community. The successful candidate should have expertise in medical device development, biomaterials, tissue engineering, or biomedical imaging. A PhD in Biomedical Engineering or related field is required, along with postdoctoral experience and a strong research portfolio. The role includes establishing an independent research program, teaching courses at all levels, mentoring students, and collaborating across departments. Startup package includes laboratory space, equipment funding, and graduate student support for innovative research projects.",
                "category": "Teaching"
            },
            {
                "title": "Assistant Professor in Cognitive Psychology",
                "description": "The Department of Psychology invites applications for an Assistant Professor position in Cognitive Psychology. We are particularly interested in candidates working in areas such as memory, attention, perception, or cognitive neuroscience. The successful applicant will have a PhD in Psychology or related field, strong research skills, and potential for external funding. Responsibilities include conducting research, teaching undergraduate and graduate courses, supervising students, and service to the department. State-of-the-art laboratories, neuroimaging facilities, and collaborative research environment provided with opportunities for interdisciplinary research.",
                "category": "Teaching"
            }
        ]

        all_jobs = []
        job_count = 0

        # Create jobs for each university
        for university in self.universities:
            if job_count >= 150:  # Create plenty of jobs
                break
                
            # Create 2-3 jobs per university
            for i, template in enumerate(job_templates[:3]):
                if job_count >= 150:
                    break
                    
                location = "London, UK" if "London" in university else "UK"
                
                job = {
                    "id": str(uuid.uuid4()),
                    "title": template["title"],
                    "university": university,
                    "description": template["description"],
                    "url": f"https://{university.lower().replace(' ', '').replace(',', '')}.ac.uk/jobs/{uuid.uuid4().hex[:8]}",
                    "location": location,
                    "deadline": "2024-06-30",
                    "category": template["category"],
                    "date_added": datetime.utcnow(),
                    "is_active": True,
                    "summary": None
                }
                
                all_jobs.append(job)
                job_count += 1

        return all_jobs

    async def save_jobs_to_db(self, jobs):
        """Save jobs to MongoDB"""
        if not jobs:
            logger.info("No jobs to save")
            return

        try:
            # Clear existing jobs first
            await self.db.jobs.delete_many({})
            logger.info("Cleared existing jobs")

            # Insert new jobs
            for job in jobs:
                job["_id"] = job["id"]
                await self.db.jobs.insert_one(job)
                
            logger.info(f"Saved {len(jobs)} jobs to database")
                    
        except Exception as e:
            logger.error(f"Error saving jobs to database: {e}")

    async def initialize_data(self):
        """Initialize the database with professorial jobs"""
        logger.info("Creating professorial jobs for UK universities...")
        
        try:
            jobs = await self.create_professorial_jobs()
            logger.info(f"Created {len(jobs)} jobs")
            
            await self.save_jobs_to_db(jobs)
            logger.info("Database initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
        finally:
            self.client.close()
        
        return True

async def main():
    initializer = SimpleJobInitializer()
    await initializer.initialize_data()

if __name__ == "__main__":
    asyncio.run(main())