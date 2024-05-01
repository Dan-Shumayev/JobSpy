import csv
from jobspy import scrape_jobs

jobs = scrape_jobs(
    # site_name=["indeed", "linkedin", "zip_recruiter"],
    site_name=["glassdoor"],
    search_term="software developer",
    location="israel",
    results_wanted=50,
    # linkedin_fetch_description = True,
    junior_experience_level = True,
    hours_old=72, # (only Linkedin/Indeed is hour specific, others round up to days old)
    country_indeed='israel'  # only needed for indeed / glassdoor
)
jobs = jobs.drop(columns=['company_revenue'])

print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_xlsx