import requests
import json
import pandas as pd
import csv
from datetime import datetime, date, timedelta
from urllib.parse import urlparse
import time
from notion_client import Client
from notion_client.errors import APIResponseError
from dotenv import load_dotenv
import os
from colorama import Fore, Style
from dateutil.parser import parse

def parse_duration(duration_str):
    if duration_str.endswith('h'):
        return timedelta(hours=int(duration_str[:-1]))
    elif duration_str.endswith('d'):
        return timedelta(days=int(duration_str[:-1]))
    else:
        raise ValueError(f"Invalid duration string: {duration_str}")

class GitHubScraper:
    def __init__(self):
        load_dotenv()
        github_token = os.getenv("GITHUB_TOKEN")
        notion_token = os.getenv("NOTION_TOKEN")

        self.github_headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        self.notion = Client(auth=notion_token)
        self.database_id = None
        self.csv_data = pd.DataFrame()

    def create_csv_file(self, filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Description", "Language", "URL", "Stars", "Forks", "Last Updated", "Last Scraped"])

    def add_to_csv_file(self, filename, repo_data):
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([repo_data['name'], repo_data['description'], repo_data['language'], repo_data['html_url'], repo_data['stargazers_count'], repo_data['forks_count'], repo_data['pushed_at'], datetime.now().isoformat()])

    def update_csv_file(self, filename, repo_data):
        lines = list()
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                lines.append(row)
                for field in row:
                    if field == repo_data['html_url']:
                        lines.remove(row)
                        lines.append([repo_data['name'], repo_data['description'], repo_data['language'], repo_data['html_url'], repo_data['stargazers_count'], repo_data['forks_count'], repo_data['pushed_at'], datetime.now().isoformat()])
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(lines)

    def get_last_scraped_date_csv(self, repo):
        if self.csv_data.empty:
            return None
        repo_row = self.csv_data.loc[self.csv_data['Name'] == repo]
        if not repo_row.empty:
            last_scraped_str = repo_row['Last Scraped'].values[0]
            return datetime.fromisoformat(last_scraped_str)
        return None

    def select_database(self):
        databases = self.notion.search(filter={"property": "object", "value": "database"}).get("results")

        print("Please select a database:")
        for i, database in enumerate(databases):
            print(f"{i+1}. {database['title'][0]['plain_text']}")

        print("0. Create a new database")

        database_choice = int(input("Enter the number of the database or 0 to create a new one: "))

        if database_choice == 0:
            database_name = input("Enter the name of the new database: ")
            self.database_id = self.create_database(database_name)["id"]
            self.update_database_schema(self.database_id)
        else:
            self.database_id = databases[database_choice - 1]["id"]

            print("The current database schema will be updated. This process will not delete existing properties.")
            user_confirmation = input("Do you want to proceed? (yes/no): ").strip().lower()

            if user_confirmation == "yes":
                self.update_database_schema(self.database_id)
            else:
                print("Database schema update aborted.")


    def load_repositories(self, filename):
        try:
            with open(filename, 'r') as f:
                urls = [line.strip() for line in f]
        except FileNotFoundError:
            print(f"Error: '{filename}' file not found. Please create a '{filename}' file with a list of repositories.")
            exit()
        
        self.repositories = [urlparse(url).path.lstrip('/') for url in urls]

    def get_repository_data(self, repo):
        print(f"Fetching data for repository: {repo}")

        try:
            repo_response = requests.get(f'https://api.github.com/repos/{repo}', headers=self.github_headers)
            repo_data = repo_response.json()

            if repo_response.status_code == 200:
                return repo_data
            else:
                print(f"Error: {repo_data['message']}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def add_to_database(self, database_id, repo_data):
        new_page = {
            "Name": {"title": [{"text": {"content": repo_data['Name']}}]},
            "Description": {"rich_text": [{"text": {"content": repo_data['Description']}}]},
            "Language": {"select": {"name": repo_data['Language']}},
            "URL": {"url": repo_data['URL']},
            "Stars": {"number": repo_data['Stars']},
            "Forks": {"number": repo_data['Forks']},
            "Last Updated": {"date": {"start": repo_data['Last Updated']}},
            "Last Scraped": {"date": {"start": datetime.now().isoformat()}},  # new field
        }
        try:
            self.notion.pages.create(parent={"database_id": database_id}, properties=new_page)
            print(Fore.GREEN + f"Added {repo_data['Name']} to the Notion database." + Style.RESET_ALL)
        except APIResponseError as e:
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)

    def update_in_database(self, database_id, repo_data, page_id):
        updated_page = {
            "Name": {"title": [{"text": {"content": repo_data['Name']}}]},
            "Description": {"rich_text": [{"text": {"content": repo_data['Description']}}]},
            "Language": {"select": {"name": repo_data['Language']}},
            "URL": {"url": repo_data['URL']},
            "Stars": {"number": repo_data['Stars']},
            "Forks": {"number": repo_data['Forks']},
            "Last Updated": {"date": {"start": repo_data['Last Updated']}},
            "Last Scraped": {"date": {"start": datetime.now().isoformat()}},
        }
        try:
            self.notion.pages.update(page_id=page_id, properties=updated_page)
        except APIResponseError as e:
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)


    def update_database_schema(self, database_id):
        self.notion.databases.update(
            database_id,
            properties={
                "Name": {"title": {}},
                "Description": {"rich_text": {}},
                "Language": {"select": {"options": []}},
                "URL": {"url": {}},
                "Stars": {"number": {}},
                "Forks": {"number": {}},
                "Last Updated": {"date": {}},
                "Last Scraped": {"date": {}},  # new field
            },
        )
    

    def get_last_scraped_date(self, repo):
        database_query_filter = {
            "property": "Name",
            "title": {
                "equals": repo
            }
        }

        query_results = self.notion.databases.query(
            self.database_id,
            filter=database_query_filter
        )

        if query_results['results']:
            last_scraped_str = query_results['results'][0]['properties']['Last Scraped']['date']['start']
            return datetime.fromisoformat(last_scraped_str)

        return None  # return None if the repository was not found in the Notion database

    def get_page_id_by_url(self, url):
        database_query_filter = {
            "property": "URL",
            "url": {
                "equals": url
            }
        }

        query_results = self.notion.databases.query(
            self.database_id,
            filter=database_query_filter
        )

        if query_results['results']:
            return query_results['results'][0]['id']

        return None  # return None if the repository with the specified URL was not found in the Notion database


    def load_csv_file(self, filename):
        if os.path.isfile(filename):
            self.csv_data = pd.read_csv(filename)
        else:
            self.csv_data = pd.DataFrame()


    def run(self):
        if self.database_id is None:
            self.select_database()

        SCRAPE_FREQUENCY = os.getenv("SCRAPE_FREQUENCY", "1d")  # default to 1 day if not specified in .env file
        scrape_frequency_seconds = parse_duration(SCRAPE_FREQUENCY).total_seconds()

        self.create_csv_file('repo_data.csv')  # create a new CSV file

        for repo in self.repositories:
            repo_data = self.get_repository_data(repo)
            if repo_data is not None:
                last_scraped_date = self.get_last_scraped_date_csv(repo_data['name'])
                if last_scraped_date is not None:
                    time_since_last_scraped = (datetime.utcnow() - last_scraped_date).total_seconds()
                    if time_since_last_scraped < scrape_frequency_seconds:
                        print(Fore.YELLOW + f"Skipping {repo} as it was scraped less than {SCRAPE_FREQUENCY} ago." + Style.RESET_ALL)
                        continue

                self.add_to_csv_file('repo_data.csv', repo_data)  # add the new data to the CSV file
                print(Fore.GREEN + f"Successfully added {repo} to the CSV file." + Style.RESET_ALL)

        # Load the data from the CSV file
        self.load_csv_file('repo_data.csv')

        # Iterate over the loaded data and add or update the pages in the Notion database
        for index, row in self.csv_data.iterrows():
            page_id = self.get_page_id_by_url(row['URL'])
            if page_id is None:
                self.add_to_database(self.database_id, row.to_dict())
                print(Fore.GREEN + f"Successfully added {row['Name']} to the Notion database." + Style.RESET_ALL)
            else:
                self.update_in_database(self.database_id, row.to_dict(), page_id)
                print(Fore.GREEN + f"Successfully updated {row['Name']} in the Notion database." + Style.RESET_ALL)

# Initialize the scraper
scraper = GitHubScraper()

# Load the list of repositories
scraper.load_repositories('list.txt')

# Run the script with the chosen database
scraper.run()