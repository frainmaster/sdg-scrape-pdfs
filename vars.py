# URL CONFIG
URL_LIST = [i.strip() for i in open('urls3.txt', 'r').readlines()]
BASE_URL = "https://www.bursamalaysia.com"
COMP_ANNOUNCE_URL = "https://www.bursamalaysia.com/market_information/announcements/company_announcement?company="
COMP_ANNOUNCE_URL2 = "&cat=AR,ARCO"
PDF_PG_URL = "/market_information/announcements/company_announcement/announcement_details?ann_id="
DISCLOSURE_URL = "https://disclosure.bursamalaysia.com"
ATTACHMENT_URL = f"{DISCLOSURE_URL}/FileAccess/viewHtml?e="
ALL_COMPANY_LIST = f"{BASE_URL}/trade/trading_resources/listing_directory/main_market"
LISTED_COMPANY_URL = "/trade/trading_resources/listing_directory/company-profile?stock_code="

# life changer https://stackoverflow.com/questions/43149534/selenium-webdriver-how-to-download-a-pdf-file-with-python
