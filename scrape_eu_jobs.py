import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import random
import undetected_chromedriver as uc

driver = uc.Chrome()
driver.get(url)
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Updated sites with working selectors
JOB_SITES = [
    {
        "name": "RemoteOK",
        "url": "https://remoteok.com/remote-python-jobs",
        "container": "tr.job",
        "title": "h2",
        "company": "h3",
        "tags": "td.tags"
    },
    {
        "name": "WeWorkRemotely",
        "url": "https://weworkremotely.com/categories/remote-programming-jobs",
        "container": "article",
        "title": "h2",
        "company": "h3",
        "location": "div.location"
    },
    {
        "name": "EU-Startups",
        "url": "https://www.eu-startups.com/jobs/",
        "container": "div.job-card",
        "title": "h3.job-title",
        "company": "div.company-name",
        "location": "div.job-location"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
    "DNT": "1"
}

def scrape_site(site):
    try:
        # Respectful delay
        time.sleep(random.uniform(1.5, 3.0))
        
        print(f"🌐 Scraping {site['name']}...")
        
        # Use session to maintain cookies
        session = requests.Session()
        response = session.get(site["url"], headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        
        # Special handling for WeWorkRemotely
        if site["name"] == "WeWorkRemotely":
            for section in soup.select('section.jobs'):
                category = section.select_one('h2').text.strip()
                if "programming" in category.lower():
                    for job in section.select(site["container"]):
                        title = job.select_one(site["title"]).text.strip()
                        company = job.select_one(site["company"]).text.strip()
                        location = "Remote"
                        jobs.append({
                            "Title": title,
                            "Company": company,
                            "Location": location,
                            "Source": site["name"]
                        })
        else:
            for job in soup.select(site["container"]):
                title = job.select_one(site["title"]).text.strip()
                company = job.select_one(site["company"]).text.strip()
                location = job.select_one(site["location"]).text.strip() if "location" in site else "Remote"
                
                jobs.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Source": site["name"]
                })
        
        print(f"✅ Found {len(jobs)} jobs on {site['name']}")
        return jobs
        
    except Exception as e:
        print(f"⚠️ Error scraping {site['name']}: {str(e)}")
        return []

def save_to_csv(jobs):
    if not jobs:
        print("❌ No jobs to save")
        return
        
    filename = f"eu_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
        writer.writeheader()
        writer.writerows(jobs)
    print(f"💾 Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    all_jobs = []
    
    for site in JOB_SITES:
        all_jobs.extend(scrape_site(site))
    
    if all_jobs:
        save_to_csv(all_jobs)
    else:
        print("❌ No jobs found overall")
    
    print("✨ Job scraping complete!")