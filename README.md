# dataops-company-info-gatherer

## Description

This is a simple tool to gather information about companies from their websites. It uses the `requests`, `beautifulsoup4`, and `selenium` libraries to scrape the data.

The tool can be used to gather the following information:
- Company name with latest news
- Company stock price changes
- Currency exchange rates evolution

## Contents
- [Project structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)

## Project structure
```
root/
│   src/
│   │   ..... # main scripts and modules
│   |
│   utils/
│   │   webdriver/
│   │   │
│   │
│   .env
│   .env.example
│   .gitignore
│   README.md
│   requirements.txt
```

## Installation
1. Clone the repository

2. Install the required libraries
```bash
pip install -r requirements.txt
```

3. Install the `chromedriver` for `selenium` to work. You can download it from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).

4. Copy the `chromedriver` to the `utils/webdriver` directory.

5. This tool uses `.env` files to store the environment variables. Create a copy of the `.env.example` file and rename it to `.env`. Fill in the required values.

## Usage

```bash
cd to_your_project_directory
python src/api_v2.py
```

```bash
cd to_your_project_directory
python src/webscrapping_beautifulsoup.py
```