import concurrent.futures
import json
from openai import OpenAI
import os
import time
import uuid

from constants import button_link_keywords, banner_text_keywords, banner_attributes_keywords
from pprint import pprint
from dotenv import load_dotenv
from operator import itemgetter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from website_list import url_list


load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def extract_company_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain_parts = domain.split('.')
    return domain_parts[1] if len(domain_parts) > 2 else domain_parts[0]


def get_elements_with_zindex(driver):
    elements = driver.find_elements(By.XPATH, '//*')
    elements_with_zindex = {}
    for element in elements:
        try:
            z_index = element.value_of_css_property('z-index')
            if z_index.isdigit():
                elements_with_zindex[element] = int(z_index)
        except Exception as e:
            print(f"Error processing element: {e}")
    return elements_with_zindex


def get_element_html_code(element):
    return element.get_attribute('outerHTML')


def get_element_text(element):
    return element.text


def find_cookie_banner_by_attributes(driver):
    for keyword in banner_attributes_keywords:
        elements = driver.find_elements(
            By.XPATH, f"//*[contains(@id, '{keyword}') or contains(@class, '{keyword}') or contains(@*[starts-with(name(), 'data-')], '{keyword}') or contains(@*[starts-with(name(), 'aria-')], '{keyword}')]")

        for element in elements:
            if element.is_displayed() and (element.size['width'] > 0 and element.size['height'] > 0):
                if is_cookie_banner(element):
                    return element
            else:
                child_element = find_child_element(element)
                return child_element
    return None


def find_cookie_banner(elements_with_zindex):
    sorted_elements = sorted(elements_with_zindex.items(),
                             key=lambda x: x[1], reverse=True)
    for element, a in sorted_elements:
        if is_cookie_banner(element):
            return element
    return None


def is_cookie_banner(element):
    # Check for keywords in element text
    text = element.text.lower()

    if any(keyword in text for keyword in banner_text_keywords):
        # Check for specific keywords in buttons or links
        buttons_or_links = element.find_elements(By.XPATH, ".//button | .//a")
        for btn_link in buttons_or_links:
            btn_link_text = btn_link.text.lower()

            if any(keyword in btn_link_text for keyword in button_link_keywords):
                return True
    return False


def find_child_element(element):
    try:
        shadow_root = element.shadow_root
        if shadow_root:
            child_element = shadow_root.find_element(By.XPATH, ".//div")
        else:
            child_element = element.find_element(By.XPATH, ".//div")
    except Exception as e:
        print(f"No shadow root found")
        try:
            child_element = element.find_element(By.XPATH, ".//div")
        except Exception as e:
            print(f"No child element found")
            child_element = None
    return child_element


def take_element_screenshot(element, screenshot_path):
    if element.is_displayed() and element.size['width'] > 0 and element.size['height'] > 0:
        element.screenshot(
            f"{screenshot_path}.png")
    else:
        child_element = find_child_element(element)
        if child_element:
            child_element.screenshot(f"{screenshot_path}.png")


def get_links_details_from_banner(element):
    # Find all links within the banner
    links = element.find_elements(By.TAG_NAME, 'a')
    link_details = [{
        "text": link.text,
        "url": link.get_attribute('href'),
        "font_size": link.value_of_css_property("font-size"),
        "font_weight": link.value_of_css_property("font-weight"),
        "color": link.value_of_css_property("color"),
        "background_color": link.value_of_css_property("background-color")
    } for link in links]

    return link_details


def get_buttons_details_from_banner(element):
    # Find all buttons within the banner
    buttons = element.find_elements(By.TAG_NAME, 'button')
    button_details = [{
        "text": button.text,
        "font_size": button.value_of_css_property("font-size"),
        "font_weight": button.value_of_css_property("font-weight"),
        "color": button.value_of_css_property("color"),
        "background_color": button.value_of_css_property("background-color")
    } for button in buttons]

    return button_details


def process_cookie_banner(driver, element, company_name):
    html_code = get_element_html_code(element)
    text = get_element_text(element)

    html_code_prompt = f"Determine if the following HTML code is a cookie consent banner and answer with 'True' or 'False' only: \n\n{html_code}"
    text_prompt = f"Determine if the following text is a cookie consent banner and answer with 'True' or 'False' only: \n\n{text}"

    is_cookie_banner = "True"

    # is_cookie_banner = get_gpt3_response(html_code_prompt)
    # if is_cookie_banner is None:
    #     is_cookie_banner = get_gpt3_response(text_prompt)

    if is_cookie_banner == "True":
        print("Cookie banner found.")
        screenshot_path = f"./results/{company_name}/main_banner.png"
        link_details = get_links_details_from_banner(element)
        button_details = get_buttons_details_from_banner(element)
        company_dir = f"./results/{company_name}"
        os.makedirs(company_dir, exist_ok=True)
        results = {
            "position": element.location,
            "size": element.size,
            "z_index": element.value_of_css_property('z-index'),
            "class": element.get_attribute('class'),
            "id": element.get_attribute('id'),
            "background_color": element.value_of_css_property('background-color'),
            "color": element.value_of_css_property('color'),
            "border": element.value_of_css_property('border'),
            "screen_shot_path": screenshot_path,
            "links": link_details,
            "number_of_links": len(link_details),
            "buttons": button_details,
            "number_of_buttons": len(button_details),
            "html_code": html_code,
            "text": text
        }

        with open(f"{company_dir}/data.json", "w") as f:
            f.write(json.dumps(results, indent=4))

        take_element_screenshot(element, screenshot_path)

    elif is_cookie_banner == "False":
        print("Cookie banner not found.")
    elif is_cookie_banner is None:
        print("Cookie banner could not be determined.")


def get_gpt3_response(prompt):
    print("Calling GPT-3 API...")
    try:
        # Call the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Print the response
        response = completion.choices[0].message.content
        print(f"Response: {response}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None


def check_website_folders(base_path, website_list):
    folder_exists = {}

    for website_url in website_list:
        # Extract company name from the URL
        company_name = extract_company_name(website_url)

        # Construct the path to the website's folder
        folder_path = os.path.join(base_path, company_name)

        # Check if the folder exists
        folder_exists[website_url] = os.path.isdir(folder_path)

    return folder_exists


def main(url):
    print(f"\n\nProcessing {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # chrome_options.add_argument(
    #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    chrome_options.add_argument("window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    time.sleep(10)  # Wait for the page to load

    company_name = extract_company_name(url)

    elements_with_zindex = get_elements_with_zindex(driver)
    cookie_banner = find_cookie_banner(elements_with_zindex)

    if cookie_banner:
        process_cookie_banner(driver, cookie_banner, company_name)
    else:
        # Find banners by attributes and take screenshots
        cookie_banner = find_cookie_banner_by_attributes(driver)
        if cookie_banner:
            process_cookie_banner(driver, cookie_banner, company_name)
        else:
            print("No cookie banner found.")
    driver.quit()


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(main, url_list)

    for url in url_list:
        company_name = extract_company_name(url)
        # check if company name folder exists in results
        # if not, run the main function for that url again
        if not os.path.exists(f"./results/{company_name}"):
            main(url)

    base_path = "./results"
    folder_exists = check_website_folders(base_path, url_list)

    # Counting True and False occurrences
    true_count = sum(value for value in folder_exists.values())
    false_count = len(folder_exists) - true_count

    # Printing results
    pprint(folder_exists)
    print(f"Websites with cookie banner: {true_count}")
    print(f"Websites without cookie banner: {false_count}")
