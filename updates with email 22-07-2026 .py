# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 05:29:35 2026

@author: usera
"""

# -*- coding: utf-8 -*-
"""
YellowPages Canada Dentist Scraper + Website Email Finder
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import random
import re
from urllib.parse import urljoin


base_url = "https://www.yellowpages.ca"
search_query = "Dentist"
location = "Vancouver+BC"
total_pages = 2


headers = {
    'User-Agent': 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/91.0.4472.124 Safari/537.36'
}


data_list = []


# ---------------- EMAIL FINDER FUNCTION ---------------- #

def find_email_from_website(website):

    if website == "N/A" or website == "":
        return "Email not found"


    try:

        print(f"      Opening website: {website}")


        response = requests.get(
            website,
            headers=headers,
            timeout=15
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # Method 1 - mailto links

        links = soup.find_all(
            "a",
            href=True
        )


        for link in links:

            href = link["href"]

            if href.startswith("mailto:"):

                email = (
                    href
                    .replace("mailto:", "")
                    .split("?")[0]
                    .strip()
                )

                if email:
                    return email



        # Method 2 - Regex search

        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


        emails = re.findall(
            pattern,
            response.text
        )


        for email in emails:

            email = email.strip()

            if email:

                return email



        # Method 3 - Search visible text

        page_text = soup.get_text(
            " "
        )


        emails = re.findall(
            pattern,
            page_text
        )


        if emails:

            return emails[0]


    except Exception as e:

        print(
            "      Email error:",
            e
        )


    return "Email not found"



# ---------------- SCRAPER ---------------- #


for page_number in range(1, total_pages + 1):


    url = (
        f"{base_url}/search/si/"
        f"{page_number}/{search_query}/{location}"
    )


    print(
        "\nOpening:",
        url
    )


    try:

        response = requests.get(
            url,
            headers=headers
        )

        response.raise_for_status()


    except Exception as e:

        print(
            "Page error:",
            e
        )

        continue



    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    cards = soup.find_all(
        'div',
        class_='listing__content__wrapper'
    )


    print(
        f"Found {len(cards)} businesses"
    )


    for index, card in enumerate(cards, start=1):


        print(
            "\nBusiness:",
            index
        )


        name_element = card.find(
            'a',
            class_='listing__name--link'
        )


        name = (
            name_element.text.strip()
            if name_element
            else "N/A"
        )


        print(
            "Name:",
            name
        )



        link_div = card.find(
            'div',
            class_='listing__content__wrap--flexed'
        )


        if not link_div:

            continue



        detail_link = link_div.get(
            "data-merchanturl"
        )


        time.sleep(
            random.uniform(1,2)
        )



        try:

            detail_response = requests.get(
                base_url + detail_link,
                headers=headers
            )


            detail_response.raise_for_status()


        except Exception as e:

            print(
                "Detail error:",
                e
            )

            continue



        detail_soup = BeautifulSoup(
            detail_response.text,
            "html.parser"
        )



        street_address = "N/A"
        locality = "N/A"
        region = "N/A"
        postal_code = "N/A"
        phone_number = "N/A"
        website_link = "N/A"
        email = "Email not found"



        # Address

        address = detail_soup.find(
            "div",
            class_="merchant__address"
        )


        if address:

            try:

                street_address = address.find(
                    "span",
                    itemprop="streetAddress"
                ).text.strip()


                locality = address.find(
                    "span",
                    itemprop="addressLocality"
                ).text.strip()


                region = address.find(
                    "span",
                    itemprop="addressRegion"
                ).text.strip()


                postal_code = address.find(
                    "span",
                    itemprop="postalCode"
                ).text.strip()


            except:

                pass




        # Phone

        phone = detail_soup.find(
            "span",
            class_="mlr__sub-text"
        )


        if phone:

            phone_number = phone.text.strip()



        # Website

        website_element = detail_soup.find(
            'li',
            class_='mlr__item--website'
        )


        if website_element:

            a = website_element.find(
                "a"
            )

            if a:

                website_link = a.get(
                    "href"
                )


                if website_link.startswith("/"):

                    website_link = urljoin(
                        base_url,
                        website_link
                    )



        # ---------------- EMAIL SEARCH ---------------- #

        if website_link != "N/A":

            email = find_email_from_website(
                website_link
            )


        print(
            "Website:",
            website_link
        )

        print(
            "Email:",
            email
        )



        data_list.append({

            "Name": name,
            "Street Address": street_address,
            "City": locality,
            "Province": region,
            "Postal Code": postal_code,
            "Phone Number": phone_number,
            "Website Link": website_link,
            "Email": email

        })




# SAVE FILE

df = pd.DataFrame(
    data_list
)


df.to_excel(
    "Dentist_Vancouver_with_Email.xlsx",
    index=False
)


print(
    "\nFinished! Excel saved."
)