# cno-scraper

## Overview
`cno-scraper` is a web scraping tool designed to scrape positive EV (Expected Value) betting data from the Crazy Ninja Odds website. The tool periodically scrapes the website, analyzes the data, and sends email alerts if there are any changes in the top 3 rows of the data.

## Features
- Periodically scrapes positive EV betting data from Crazy Ninja Odds.
- Analyzes the data and sends email alerts if there are changes in the top 3 rows.
- Configurable via environment variables for secure handling of sensitive information.
- Skips sending alerts between midnight and 8 AM.

## Requirements
- Python 3.x
- `selenium` library
- `beautifulsoup4` library
- `pandas` library
- `python-dotenv` library
- A valid SMTP server for sending email alerts

## Enviroment Variables

- SMTP_SERVER=smtp.gmail.com
- SMTP_PORT=587
- SMTP_USER=your_email@gmail.com
- SMTP_PASSWORD=your_email_password
- FROM_EMAIL=your_email@gmail.com
- TO_EMAIL=recipient_email@gmail.com