import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
import pandas as pd

def setup_driver() -> webdriver.Chrome:
    """
    Sets up and returns a configured Chrome WebDriver.
    """
    service = Service(executable_path='chromedriver.exe')
    return webdriver.Chrome(service=service)

def get_page_proposals(driver: webdriver.Chrome, current_page_url: str) -> list:
    '''Extracts the proposal ids from a single page of proposals.
    
    Args:
        driver: The Selenium WebDriver.
        current_page_url: The URL of the current page.
        
    Returns:
        A list of proposal ids.
    '''
    proposal_ids = []
    driver.get(current_page_url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find all 'div' elements with a class 'column' and an id that starts with 'proposal_'
    proposals = soup.find_all('div', class_='column', id=re.compile(r'^proposal_\d+$'))
    
    # Extract the id attributes
    for proposal in proposals:
        id = proposal['id'].split('_')[-1]
        proposal_ids.append(id)

    return proposal_ids

def get_all_proposal_ids(driver: webdriver.Chrome, base_url: str) -> list:
    '''Extracts all proposal ids from all pages of proposals.

    Args:
        driver: The Selenium WebDriver.
        base_url: The base URL of the proposals page.

    Returns:
        A list of proposal ids.
    '''
    proposal_ids = []
    current_page = 1
    while True:
        page_url = f'{base_url}?component_id=321&page={current_page}&participatory_process_slug=Citywidepb2023'
        proposal_ids.extend(get_page_proposals(driver, page_url))

        try:
            # Locate the Next button and click
            next_button = driver.find_element(by='css selector', value='li.pagination-next a[rel="next"]')
            next_button.click()
            current_page += 1  # Increment the page count
        except NoSuchElementException:
            # If no Next button is found, break the loop
            break

    return proposal_ids

def fetch_proposal_data(proposal_id: str, base_url: str) -> dict:
    '''Fetches data for a single proposal.

    Args: 
        proposal_id: The ID of the proposal.
        base_url: The base URL of the proposals page.

    Returns:
        A dictionary containing the proposal data.
    '''
    proposal_url = f'{base_url}/{proposal_id}'
    
    driver = setup_driver()
    driver.get(proposal_url)
    page_source = driver.page_source
    
    soup = BeautifulSoup(page_source, 'html.parser')

    # Parse the title
    title = soup.find('h2', class_='heading3').text.strip()

    # Parse the datetime
    datetime = soup.find('div', class_='author-data__extra').span.text.strip()

    # Extract data from each dt-dd pair
    data = {}
    for dt, dd in zip(soup.find_all('dt'), soup.find_all('dd')):
        key = dt.get_text().strip()
        values = [div.get_text().strip() for div in dd.find_all('div')]
        if len(values) > 1:
            data[key] = values
        elif values:
            data[key] = values[0]
        else:
            data[key] = ""

    # Parse tags
    tags = [
        li.a.text.strip().split('\n')[-1].strip() 
        for li in soup.select('ul.tags--list li')
    ]

    # Combine everything into a dictionary
    result = {
        "proposal_id": proposal_id,
        "title": title,
        "datetime": datetime,
        **data,
        "tags": tags
    }

    return result

def main():
    # Set the base URL of the proposals page
    base_url = 'https://www.participate.nyc.gov/processes/Citywidepb2023/f/321/proposals'

    # Set up the WebDriver
    driver = setup_driver()

    # Get all proposal IDs
    proposal_ids = get_all_proposal_ids(driver, base_url)

    # Fetch data for each proposal
    results = []
    failed_proposals = []

    for proposal_id in proposal_ids:
        try:
            print(f'Fetching proposal {base_url}/{proposal_id}')
            result = fetch_proposal_data(proposal_id)
            results.append(result)
        except Exception as e:
            print(f"Error fetching proposal {base_url}/{proposal_id}: {e}")
            failed_proposals.append(proposal_id)
            time.sleep(1)

    # Save results to an Excel file
    df = pd.DataFrame(results)
    df.to_excel('../data/nyc_pb_proposals.xlsx', index=False)

    # Save failed proposals to a text file
    with open('../data/failed_proposals.txt', 'w') as f:
        for proposal_id in failed_proposals:
            f.write(f'{proposal_id}\n')
