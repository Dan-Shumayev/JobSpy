import os
import csv
import pandas as pd
import re
from googleapiclient.discovery import build

COMPANY_TO_RATING_CACHE = {}

def find_google_rating_with_api(company_name, api_key="AIzaSyBMSfnUyUGaMhv4u-RvJArQev3x6j4Z4-Q"):
    if company_name in COMPANY_TO_RATING_CACHE:
        return COMPANY_TO_RATING_CACHE[company_name]
    
    # Initialize the Custom Search API client
    service = build("customsearch", "v1", developerKey=api_key)

    # Construct the search query
    query = f"{company_name} site:glassdoor.com"

    # Make the search request
    result = service.cse().list(
        q=query,
        cx="013036536707430787589:_pqjad5hr1a"  # Custom Search Engine ID for Glassdoor
    ).execute()

    # Extract and return the rating
    items = result.get("items", [])
    for item in items:
        snippet = item.get("snippet", "")
        # Search for the rating pattern in the snippet
        rating_pattern = re.compile(r"(\d+\.\d+) out of")
        match = rating_pattern.search(snippet)
        if match:
            COMPANY_TO_RATING_CACHE[company_name] = float(match.group(1))
            return float(match.group(1))

    return 0.0

# Load both CSV files
jobs1 = pd.read_csv("jobs.csv")
jobs2 = pd.read_csv("jobs2.csv")

# Concatenate the two DataFrames
combined_jobs = pd.concat([jobs1, jobs2])

# Drop duplicates based on job title and company name
combined_jobs = combined_jobs.drop_duplicates(subset=['title', 'company'])

# Reset index
combined_jobs.reset_index(drop=True, inplace=True)

# Save the combined DataFrame to a new CSV file
combined_jobs.to_csv("combined_jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

print(f"Combined {len(combined_jobs)} unique jobs")

# Load the combined jobs CSV
combined_jobs = pd.read_csv("combined_jobs.csv").tail(72)

# # Filter jobs based on Glassdoor rating
combined_jobs['glassdoor_rating'] = combined_jobs['company'].apply(find_google_rating_with_api)
combined_jobs = combined_jobs[combined_jobs['glassdoor_rating'] >= 4.0]

# # Drop the temporary glassdoor_rating column
combined_jobs = combined_jobs.drop(columns=['glassdoor_rating'])

# # Reset index
combined_jobs.reset_index(drop=True, inplace=True)

# # Save the filtered DataFrame to a new CSV file
combined_jobs.to_csv("filtered_jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)

# Load the filtered jobs CSV
combined_jobs = pd.read_csv("filtered_jobs.csv")

# Group the jobs by company
grouped_jobs = combined_jobs.groupby('company')

# Create a directory to store the files
output_directory = "company_jobs4"
os.makedirs(output_directory, exist_ok=True)

# Iterate over each company and create a separate CSV file for its jobs
for company_name, group_data in grouped_jobs:
    # Replace '|' with '-' in company name for file name
    company_file_name = company_name.replace('|', '-')

    # Extract job URLs for this company
    company_jobs_urls = group_data['job_url'].tolist()
    
    # Write job URLs to a CSV file
    output_file = os.path.join(output_directory, f"{company_file_name}.csv")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['job_url'])
        writer.writerows([[job_url] for job_url in company_jobs_urls])

    print(f"Created CSV file for {company_file_name} jobs: {output_file}")