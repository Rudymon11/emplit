import requests
import sys
from datetime import datetime
import json

class AcademicJobsAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_get_jobs_basic(self):
        """Test basic jobs endpoint"""
        return self.run_test("Get Jobs (Basic)", "GET", "api/jobs", 200)

    def test_get_jobs_with_pagination(self):
        """Test jobs with pagination"""
        params = {"page": 1, "limit": 5}
        return self.run_test("Get Jobs (Pagination)", "GET", "api/jobs", 200, params=params)

    def test_get_jobs_with_search(self):
        """Test jobs with search"""
        params = {"search": "Professor"}
        return self.run_test("Get Jobs (Search Professor)", "GET", "api/jobs", 200, params=params)

    def test_get_jobs_search_machine_learning(self):
        """Test search for Machine Learning"""
        params = {"search": "Machine Learning"}
        return self.run_test("Get Jobs (Search Machine Learning)", "GET", "api/jobs", 200, params=params)

    def test_get_jobs_search_data_science(self):
        """Test search for Data Science"""
        params = {"search": "Data Science"}
        return self.run_test("Get Jobs (Search Data Science)", "GET", "api/jobs", 200, params=params)

    def test_get_jobs_with_category_filter(self):
        """Test jobs with category filter"""
        params = {"category": "Teaching"}
        return self.run_test("Get Jobs (Category: Teaching)", "GET", "api/jobs", 200, params=params)

    def test_get_jobs_with_university_filter(self):
        """Test jobs with university filter"""
        params = {"university": "University"}
        return self.run_test("Get Jobs (University Filter)", "GET", "api/jobs", 200, params=params)

    def test_get_stats(self):
        """Test stats endpoint"""
        return self.run_test("Get Stats", "GET", "api/stats", 200)

    def test_get_sources(self):
        """Test sources endpoint"""
        return self.run_test("Get Sources", "GET", "api/sources", 200)

    def test_create_job(self):
        """Test creating a new job"""
        job_data = {
            "title": "Test Professor Position",
            "university": "Test University",
            "description": "This is a test job posting for a professor position in computer science.",
            "url": "https://example.com/job/123",
            "location": "London, UK",
            "deadline": "2024-12-31T23:59:59Z",
            "category": "Teaching",
            "summary": "Test summary for professor position"
        }
        return self.run_test("Create Job", "POST", "api/jobs", 200, data=job_data)

    def test_pagination_multiple_pages(self):
        """Test multiple pages of pagination"""
        success = True
        for page in range(1, 4):  # Test first 3 pages
            page_success, response = self.run_test(f"Get Jobs (Page {page})", "GET", "api/jobs", 200, params={"page": page, "limit": 10})
            if not page_success:
                success = False
            elif isinstance(response, dict) and 'pagination' in response:
                pagination = response['pagination']
                print(f"   Page {page}: {len(response.get('jobs', []))} jobs, Total: {pagination.get('total_count', 0)}")
        return success

def main():
    print("🚀 Starting Academic Jobs API Tests")
    print("=" * 50)
    
    # Setup
    tester = AcademicJobsAPITester("http://localhost:8001")
    
    # Run all tests
    tests = [
        tester.test_root_endpoint,
        tester.test_get_stats,
        tester.test_get_jobs_basic,
        tester.test_get_jobs_with_pagination,
        tester.test_get_jobs_with_search,
        tester.test_get_jobs_search_machine_learning,
        tester.test_get_jobs_search_data_science,
        tester.test_get_jobs_with_category_filter,
        tester.test_get_jobs_with_university_filter,
        tester.test_get_sources,
        tester.test_create_job,
        tester.test_pagination_multiple_pages
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())