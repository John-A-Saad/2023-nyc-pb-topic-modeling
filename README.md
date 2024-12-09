# 2023 NYC PB Topic Modeling

This repository contains code and resources for topic modeling on the 2023 New York City (NYC) Participatory Budgeting (PB) data. The goal is to analyze and extract meaningful topics from the PB proposals submitted by NYC residents.

## Contents

- `data/`: Contains the datasets used for topic modeling.
- `scrape/`: Contains script to scrape the 2023 NYC PB data.
- `topic_modeling/`: Jupyter notebooks with data prep and topic modeling steps.
- `viz/`: visualizations from the topic modeling.

## Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/John-A-Saad/2023-nyc-pb-topic-modeling.git
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the script to scrape the 2023 NYC PB data:
    ```bash
    python scrape/extract_nyc_pb_data.py
    ```
4. Run Jupyter notebook `topic_modeling/topic_modeling.ipynb` to explore the data and train models.