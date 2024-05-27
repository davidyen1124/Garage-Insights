# Garage Insights

## Overview

Garage Insights is a program designed to analyze the activation patterns of a garage door using historical data from Home Assistant. The program fetches data, processes it, generates informative plots, and uploads these visualizations to Google Drive for easy access and sharing.

## Features

- **Data Retrieval**: Fetches historical data from Home Assistant based on specified time periods.
- **Data Processing**: Normalizes and processes the data to extract meaningful insights.
- **Visualization**: Creates detailed plots showing garage door activation patterns over a 24-hour period.
- **Cloud Integration**: Uploads the generated plots to Google Drive, making them accessible from anywhere.
- **Automation**: Can be scheduled to run periodically using cron jobs for continuous monitoring and analysis.

## Technologies

- **Python**: Core programming language used for data processing and automation.
- **Pandas**: Library for data manipulation and analysis.
- **Matplotlib**: Library for creating static, animated, and interactive visualizations.
- **Requests**: Library for making HTTP requests to access Home Assistant data.
- **Google API Client**: Libraries for interacting with Google Drive API to upload files.
- **Dotenv**: Library to manage environment variables for configuration settings.

## Benefits

- **Insightful Analysis**: Provides valuable insights into the usage patterns of your garage door.
- **Automated Reporting**: Eliminates the need for manual data collection and reporting by automating the entire process.
- **Accessibility**: Stores visual reports in Google Drive, allowing easy sharing and access from any device.
- **Customizable**: Easily adaptable to other use cases by modifying the data processing and visualization logic.

## Setup

To get started, copy the `.env.example` file to `.env` and fill in your specific configuration details:

```bash
cp .env.example .env
```

Edit the .env file and replace the placeholder values with your actual configuration values.
