## 1. Enhanced CLI Interactions
On executing `python main.py`, the user is presented with an interactive command-line interface. Users navigate the options using the keyboard arrows. The interface offers the following commands:

### **Find new repositories**
By employing GitHub's code search API, this function enables users to discover repositories containing specified packages in their code. When initiating this command, users are first asked to input the packages they wish to search for (for example, "openai" or "openai,numpy"). 

Next, users will be prompted to enter dynamic search filters: `star_count`, `fork_count`, `last_commit`, `language`, and `max_pages`. If the user does not provide input, the tool defaults to the configurations from the .env file. The search results are then parsed to identify unique repositories and extract relevant information. 

Each "Find new repositories" session generates a uniquely named file that stores the search results. To guarantee a consistent and suitably-sized filename, the search parameters are hashed using a secure hashing algorithm (SHA-3).

### **Scrape repository list**
This function provides users with the flexibility to select one or more list files from the 'lists' folder for scraping repository data. These list files are generated from previous search sessions. Unlike previous versions, this command focuses solely on scraping data, without automatically updating the Notion database.

When the "Scrape repository list" command is initiated, the tool fetches data from the GitHub repositories specified in the selected list files. The fetched data includes the repository's name, description, language, URL, stars, forks, last updated date, and the date it was last scraped. All this data is stored in a CSV file, ready for transfer to the Notion database.

### **Update Notion Database**
This function is now distinct from the "Scrape repository list" command. It provides users with full control over updating their Notion database with the latest scraped repository data. 

If a user selects an existing Notion database, the tool operates as previously described. If a user opts to create a new database, they're prompted to input its name. They then have the option to update the schema. It's important to note that this process requires enhancements to fully support new database creation.

The "Update Notion Database" command allows users to manually update their Notion database with the contents from `repo_data.csv`. The tool checks whether a repository already exists in the database. If it does, the existing row is updated. If not, a new row is created.

### **Exit**

## 2. Efficient GitHub API Usage
Throughout the search and scrape process, the tool vigilantly monitors the remaining API rate limit to prevent exceeding it. Moreover, the tool offers regular updates on the current API quota status, providing users with real-time visibility of API usage.

## 3. Advanced Debugging and Logging
A `--debug` command-line option is available. When used, detailed logs of the tool's operations are displayed in the CLI, useful for understanding the tool's functions and troubleshooting any issues.

## 4. Repository Scrape Frequency
The tool adheres to a scraping frequency specified in the .env file (default is daily). If a repository has been scraped within this frequency, it's skipped in the current session. The date of the last scrape is recorded in the CSV file and in the Notion database.
