from dotenv import load_dotenv
import os
import hashlib
import requests
import csv
import questionary
from urllib.parse import urlencode


class GitHubRepoFinder:
    def __init__(self):
        load_dotenv()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        self.default_config = {
            "star_count": os.getenv("DEFAULT_STAR_COUNT", 50),
            "fork_count": os.getenv("DEFAULT_FORK_COUNT", 50),
            "last_commit": os.getenv("DEFAULT_LAST_COMMIT", "2023-01-01"),
            "language": os.getenv("DEFAULT_LANGUAGE", ""),
            "max_pages": os.getenv("DEFAULT_MAX_PAGES", 5)
        }
        self.existing_urls = set()

    def run(self):
        while True:
            action = questionary.select(
                "What do you want to do?",
                choices=[
                    "Find new repositories",
                    "Exit"
                ]
            ).ask()

            if action == "Find new repositories":
                self.find_new_repositories_interactive()
            elif action == "Exit":
                break
            else:
                print("Invalid option. Please try again.")

    def find_new_repositories_interactive(self):
        self.existing_urls = set()  # reset the set of existing URLs
        search_query = questionary.text(
            "Please enter the packages you wish to search for (for example, 'openai' or 'openai,numpy'): "
        ).ask()

        if not search_query:
            print("Invalid input. Please try again.")
            return

        parameters = self.get_search_parameters()
        parameters['q'] = f"{search_query} in:file"
        search_results = self.github_code_search(parameters)
        self.save_search_results(search_results, search_query)

        save_txt = questionary.confirm(
            "Do you want to save the URLs as lists.txt (This will replace existing lists.txt file)?"
        ).ask()

        if save_txt:
            self.save_as_txt()

    def get_search_parameters(self):
        parameters = {
            'star_count': self.get_user_input("Star count", self.default_config["star_count"]),
            'fork_count': self.get_user_input("Fork count", self.default_config["fork_count"]),
            'last_commit': self.get_user_input("Last commit (YYYY-MM-DD)", self.default_config["last_commit"]),
            'language': self.get_user_input("Language", self.default_config["language"]),
            'max_pages': int(self.get_user_input("Maximum number of pages to fetch", self.default_config["max_pages"])),
        }
        return parameters

    def get_user_input(self, prompt, default):
        return questionary.text(
            f"{prompt} (default is {default}): ",
            default=default
        ).ask()

    def github_code_search(self, parameters):
        base_url = "https://api.github.com/search/code"
        search_results = []
        for page in range(1, parameters['max_pages'] + 1):
            params = {
                "q": parameters['q'],
                "sort": "indexed",
                "order": "desc",
                "per_page": 100,
                "page": page
            }
            response = requests.get(base_url, headers=self.headers, params=params)
            if response.status_code == 200:
                search_results.extend(response.json().get('items', []))
            else:
                break
        return search_results

    def save_search_results(self, search_results, search_query):
        file_name = hashlib.sha3_224(search_query.encode('utf-8')).hexdigest() + ".csv"
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["URL"])
            for item in search_results:
                repository_url = item.get('repository', {}).get('html_url', "")
                if repository_url not in self.existing_urls:
                    self.existing_urls.add(repository_url)
                    writer.writerow([repository_url])
        print(f"Saved {len(self.existing_urls)} unique URLs to {file_name}")

    def save_as_txt(self):
        with open('lists.txt', 'w') as file:
            for url in self.existing_urls:
                file.write(url + '\n')


if __name__ == "__main__":
    finder = GitHubRepoFinder()
    finder.run()
