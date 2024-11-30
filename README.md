# Web Tracker Analysis Tool

Analyze web trackers on URLs retrieved from search results using Selenium and the [WhoTracks.Me](https://whotracks.me/) dataset. This tool identifies and categorizes trackers to provide insights into the tracking ecosystem of websites and generates detailed reports.

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Dependencies](#dependencies)
- [Setup Instructions](#setup-instructions)
  - [System Requirements](#system-requirements)
  - [Python Environment](#python-environment)
  - [WhoTracks.Me Dataset](#whotracksme-dataset)
- [Usage](#usage)
- [Output Details](#output-details)
- [Technologies and Libraries](#technologies-and-libraries)
- [Known Issues](#known-issues)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Introduction

This project analyzes web trackers using Selenium for web scraping and the WhoTracks.Me Python API for tracker information.

The project performs the following tasks:
1. Scrapes search results and their linked pages using Selenium.
2. Identifies third-party trackers on these pages.
3. Categorizes trackers (e.g., "Advertising", "Site Analytics") using WhoTracks.Me data.

---

## Features

### Automated Search Query Analysis
- **Google Search Scraping**:
  - Utilizes [Selenium](https://www.selenium.dev/) to automate scraping search results for specified queries.
  - Differentiates between normal search results and AI overview results.

### Tracker Identification
- **Domain Extraction**:
  - Extracts third-party domains from browser performance logs using Selenium's performance logging capabilities.
  - Matches tracker domains to categories using the [WhoTracks.Me dataset](https://github.com/cliqz-oss/whotracks.me).

### Categorization and Reporting
- **Tracker Categorization**:
  - Categorizes trackers into predefined types, including:
    - Advertising
    - Site Analytics
    - Consent Management
    - Essential
    - Hosting
    - Customer Interaction
    - Audio/Video Player
    - Extensions
    - Adult Advertising
    - Social Media
    - Miscellaneous
    - Uncategorized
- **Summary and Reporting**:
  - Generates two CSV reports:
    - **Tracker Summary CSV**:
      - Includes total trackers and counts by category for each URL, split between Normal and AI Overview links.
    - **Tracker Names CSV**:
      - Lists tracker domain names found for each query, along with their associated URL and link type (Normal/AI Overview).

---

## Dependencies

- Python 3.11 or later
- [Selenium](https://www.selenium.dev/)
- [WhoTracks.Me Python API](https://github.com/ghostery/whotracks.me)
- ChromeDriver
- AWS CLI (for downloading data)

---

## Setup Instructions

### System Requirements

#### Homebrew (for macOS users):
1. If Homebrew is not installed, run:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install ChromeDriver using Homebrew:
   ```
   brew install chromedriver
   ```

#### AWS CLI:
1. Install AWS CLI by following the official guide for your operating system:
   - [Linux](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html)
   - [MacOS](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html)
   - [Windows](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html)

2. Alternatively, for macOS, install AWS CLI using Homebrew:
   ```
   brew install awscli
   ```

3. Verify installation:
   ```
   aws --version
   ```

---

### Python Environment

1. Create a virtual environment:
   ```
   python3.11 -m venv venv
   ```

2. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```
   pip install selenium git+https://github.com/ghostery/whotracks.me.git
   ```

---

### WhoTracks.Me Dataset

1. Use AWS CLI to download the latest data into the required folder structure:
   ```
   aws s3 sync --no-sign-request s3://data.whotracks.me/<latest-month> ./whotracksme/data/assets
   ```

2. Alternatively, manually download the data from the [WhoTracks.Me Explorer](https://www.ghostery.com/whotracksme/explorer) and place it in the `whotracksme/data/assets` directory.

3. Verify the dataset structure:

---

## Usage

1. Ensure ChromeDriver is installed and available in your PATH.
2. Run the script:
```
python main.py
```
3. The script will:
- Scrape Google search results.
- Extract third-party trackers from performance logs.
- Categorize trackers and generate detailed CSV reports.

---

## Output Details

### Tracker Summary CSV (`tracker_summary_detailed.csv`)
| Column            | Description                                                 |
|--------------------|-------------------------------------------------------------|
| Query             | The search query associated with the URLs.                  |
| URL               | The analyzed URL.                                           |
| Type              | Either "Normal" or "AI Overview".                           |
| Position          | Position of the URL in the search results.                  |
| Total Trackers    | Total number of trackers found on the URL.                  |
| Category Columns  | Tracker counts for each predefined category (e.g., Advertising, Site Analytics). |

### Tracker Names CSV (`tracker_names.csv`)
| Column    | Description                                  |
|-----------|----------------------------------------------|
| Query     | The search query associated with the URL.   |
| URL       | The URL where the tracker was found.        |
| Tracker   | The name of the tracker domain.             |
| Type      | Either "Normal" or "AI Overview".           |

---

## Technologies and Libraries

- **Selenium**:
- Used for browser automation to scrape Google search results and analyze network requests.
- For more information, visit [Selenium's official website](https://www.selenium.dev/).

- **WhoTracks.Me**:
- A dataset that provides detailed information on trackers, including categorization.
- For more information, visit [WhoTracks.Me](https://whotracks.me/) or explore the dataset on [GitHub](https://github.com/cliqz-oss/whotracks.me).

- **Python Standard Libraries**:
- `csv`: For generating structured CSV reports.
- `json`: For parsing network logs from Selenium.
- `time`: To manage delays for resource loading.
- `collections`: Used for managing and counting tracker categories with `defaultdict`.

---

## Known Issues

- **No AI Overview Links**:
Queries without AI Overview links are skipped, and their names are logged separately.

- **Tracker Categories**:
If a tracker category is not in `CATEGORY_MAPPING`, it will not be included in the detailed summary.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgments

- **Selenium** for making browser automation straightforward.
- **WhoTracks.Me** for their invaluable dataset on web trackers.
- The Python community for providing robust tools and libraries to build this project.
