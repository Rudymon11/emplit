import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import LondonAcademicScraper
from ai_processor import AIJobProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_sample_data():
    """Initialize the database with sample London academic jobs"""
    logger.info("Initializing London academic jobs database...")
    
    try:
        # Run scraper to create sample data
        scraper = LondonAcademicScraper()
        await scraper.run_scraping()
        
        # Process jobs with AI
        logger.info("Processing jobs with AI...")
        processor = AIJobProcessor()
        await processor.process_unprocessed_jobs()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(initialize_sample_data())
    sys.exit(0 if success else 1)