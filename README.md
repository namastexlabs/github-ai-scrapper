# GitHub Scraper

GitHub Scraper is a Python script designed to extract information about GitHub repositories and store it in a CSV file as well as a Notion database. This tool is great for tracking changes in repositories over time, keeping an eye on popular repositories, or for general data analysis purposes.

## Features

- Fetches repository data from GitHub using the GitHub API
- Stores the repository data in a CSV file and a Notion database
- Updates the CSV file and the Notion database at a specified frequency
- Interactive command-line interface to manage the script

## Usage

1. **Install the required libraries**: Before running the script, you need to install all the required libraries by running the following command:

    ```
    pip install -r requirements.txt
    ```

2. **Set up your environment variables**: The script requires access to the GitHub API and the Notion API, so you need to provide your API tokens. Create a `.env` file in the same directory as your script and add your GitHub and Notion API tokens like this:

    ```
    GITHUB_TOKEN=your_github_token
    NOTION_TOKEN=your_notion_token
    ```

    You can also specify the frequency at which the script should scrape the repositories by adding the `SCRAPE_FREQUENCY` variable to your `.env` file. The value should be a number followed by either "h" for hours or "d" for days. If not specified, the default value is "1d" (once a day).

    ```
    SCRAPE_FREQUENCY=12h
    ```

3. **Add your repositories**: Create a `list.txt` file in the same directory as your script and list the URLs of the repositories you want to track, one per line.

4. **Run the script**: You can run the script by executing the following command in your terminal:

    ```
    python github_scraper.py
    ```

    The script will ask you to select a Notion database or create a new one, and then it will start scraping the repositories.

5. **Use the interactive command-line interface**: Once the script is running, you can choose to find new repositories or run the GitHub Scraper. When you're done, you can choose to exit the program.

Please remember to replace `your_github_token` and `your_notion_token` with your actual GitHub and Notion API tokens respectively. Do not share your `.env` file as it contains sensitive data.

Please note that the GitHub API has a rate limit. If you hit this limit, you will have to wait until the limit resets before you can make more requests.
