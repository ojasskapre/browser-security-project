import json
import os
import time
import uuid

from constants import button_link_keywords, banner_text_keywords, banner_attributes_keywords
from operator import itemgetter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from website_list import web_url, url_list


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
            print(element.is_displayed(), element.size,
                  element.get_attribute('id'))
            print(element.text)
            if element.is_displayed() and (element.size['width'] > 0 and element.size['height'] > 0):
                if is_cookie_banner(element):
                    print(element.get_attribute('id'))
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


def take_element_screenshot(driver, element, screenshot_path):
    z_index = element.value_of_css_property('z-index')

    if element.is_displayed() and element.size['width'] > 0 and element.size['height'] > 0:
        class_name = element.get_attribute('class')
        element_id = element.get_attribute('id')
        print(
            f"Element: {element}, Z-Index: {z_index}, Class: {class_name}, ID: {element_id}")
        element.screenshot(
            f"{screenshot_path}.png")
    else:
        print(
            f"Element not visible or has zero size: {element}, Z-Index: {z_index}")

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
    company_dir = f"./results/{company_name}"
    os.makedirs(company_dir, exist_ok=True)
    html_code = get_element_html_code(element)
    text = get_element_text(element)
    screenshot_path = f"./results/{company_name}/main_banner.png"

    link_details = get_links_details_from_banner(element)

    button_details = get_buttons_details_from_banner(element)

    results = {
        "html_code": html_code,
        "text": text,
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
    }

    with open(f"{company_dir}/data.json", "w") as f:
        f.write(json.dumps(results, indent=4))

    take_element_screenshot(driver, element, screenshot_path)


# def take_screenshots_of_top_elements(driver, elements_with_zindex, company_name, n=10):
#     sorted_elements = sorted(elements_with_zindex.items(),
#                              key=itemgetter(1), reverse=True)
#     for elem, z_index in sorted_elements[:n]:
#         if elem.is_displayed() and elem.size['width'] > 0 and elem.size['height'] > 0:
#             class_name = elem.get_attribute('class')
#             element_id = elem.get_attribute('id')
#             print(
#                 f"Element: {elem}, Z-Index: {z_index}, Class: {class_name}, ID: {element_id}")
#             elem.screenshot(f"{company_name}_{uuid.uuid4()}.png")
#         else:
#             print(
#                 f"Element not visible or has zero size: {elem}, Z-Index: {z_index}")


def main(url):
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

    # find_cookie_banner_by_attributes(driver)
    # keyword = "consent"
    # elements = driver.find_elements(
    #     By.XPATH, f"//*[contains(@id, '{keyword}') or contains(@class, '{keyword}') or contains(@*[starts-with(name(), 'data-')], '{keyword}') or contains(@*[starts-with(name(), 'aria-')], '{keyword}')]")

    # for e in elements:
    #     # ce = e.find_element(By.XPATH, ".//div")
    #     # print(e.shadow_root)
    #     print(e.get_attribute('id'))
    #     print(e.get_attribute('class'))
    #     print(e.size)
    #     print(e.is_displayed())
    #     print(e.text)

    company_name = extract_company_name(url)

    elements_with_zindex = get_elements_with_zindex(driver)
    cookie_banner = find_cookie_banner(elements_with_zindex)

    if cookie_banner:
        print("Cookie banner found.")
        process_cookie_banner(driver, cookie_banner, company_name)
    else:
        print("No cookie banner found using z-index.")
        # Find banners by attributes and take screenshots
        cookie_banner = find_cookie_banner_by_attributes(driver)
        if cookie_banner:
            print("Cookie banner found.")
            process_cookie_banner(driver, cookie_banner, company_name)
        else:
            print("No cookie banner found.")
    driver.quit()


if __name__ == "__main__":
    # main(web_url)
    for url in url_list:
        print(f"\nProcessing {url}")
        main(url)
