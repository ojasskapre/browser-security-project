# 18636 - Browser Security Project

#### By Ojas Kapre - [Github](https://github.com/ojasskapre), [LinkedIn](https://www.linkedin.com/in/ojaskapre/)

## Project Description

The "Browser Security Project" focuses on investigating and ensuring the compliance of website cookie banners with privacy regulations like GDPR and CCPA. With the increasing importance of digital privacy, this project combines theoretical research with practical tools to assess and enhance cookie banner compliance. A key outcome of this project is the development of a Python-based tool that detects and analyzes cookie banners across various websites, leveraging Selenium and OpenAI's GPT-3.5-turbo API for enhanced accuracy.

## Features

- **Cookie Detection Module**: Automatically detects cookie banners on websites using advanced CSS property analysis and machine learning models.
- **Compliance Evaluation**: Assesses the detected cookie banners against GDPR and CCPA guidelines, ensuring they meet regulatory requirements.
- **Custom GPT Models**: Utilizes custom GPT models to evaluate cookie consent interfaces based on clarity, transparency, accessibility, and other user-centered design principles.
- **Multilingual Support**: Capable of detecting and analyzing cookie banners in multiple languages, ensuring global compliance.
- **Data Saving**: Saves metadata and screenshots of detected cookie banners for further analysis.

## What's Done

- **Literature Review**: Conducted a comprehensive review of four pivotal research papers on cookie consent interfaces and compliance challenges.
- **Cookie Detection Module**: Developed and implemented a robust cookie detection module using Python and Selenium.
- **Machine Learning Integration**: Enhanced the accuracy of the detection module with the integration of OpenAI's GPT-3.5-turbo for analyzing HTML code.
- **Compliance Evaluation Module**: Created custom GPT models to evaluate cookie banners against 12 key principles derived from research.
- **Multilingual Detection**: Successfully tested and validated the tool's capability to detect cookie banners in various languages.
- **Results Documentation**: Captured and documented the results, demonstrating the tool's effectiveness across different websites.

## Setup

1. Clone the repository `git clone https://github.com/ojasskapre/browser-security-project`
2. Create a python virtual environment `python3 -m venv venv`
3. Activate the virtual environment `source venv/bin/activate`
4. Install all the dependencies `pip install -r requirements.txt`
5. Running the script `python app.py`
