import os
import selenium.webdriver as wd
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.options import Options
import time
from vars import *


# DRIVER CONFIG
d = "chromedriver_v105.exe"
pdf_folder = os.path.join(os.getcwd(), "pdfs")


def is_annual_report(url):
    url = url.lower()
    non_ar = ["administrative guide", "corporate governance",
              "cg report", "admin guide"]
    if "annual report" in url or "ar" in url.split() \
            or all(j not in url for j in non_ar):
        return True
    return False


def download_all_pdfs():
    start_time = time.time()
    options = Options()
    # options for running in headless mode (Chrome is not opened physically)
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options for downloading PDF
    options.add_experimental_option('prefs', {
        "download.default_directory": pdf_folder,  # Change default dir for downloads
        "download.prompt_for_download": False,  # auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # avoid showing PDF directly in chrome
    })
    driver = wd.Chrome(d, options=options)

    urls = URL_LIST
    all_downloaded_pdfs_cnt = 0
    for url_idx, url in enumerate(urls):
        try:
            # company announcements page
            company_id = url.replace(COMP_ANNOUNCE_URL, "")\
                .replace(COMP_ANNOUNCE_URL2, "")
            driver.switch_to.window(driver.window_handles[-1])
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(url)
            soup = bs(driver.page_source, 'html.parser')
            tbl = soup.find(id="table-announcements")
            all_a = tbl.find('tbody').find_all('a')
            # all_reports = [i for i in all_a if PDF_PG_URL in str(i)]
            target_urls = [i['href'] for i in all_a if PDF_PG_URL in str(i)]
            ann_ids = [i.split("ann_id=")[-1] for i in target_urls]

            dl_cnt = 0
            for ann_id in ann_ids:
                if dl_cnt:
                    break
                # announcement details iframe
                # take latest (topmost) record
                driver.switch_to.window(driver.window_handles[-1])
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(f"{ATTACHMENT_URL}{ann_id}")  # take first row only i.e. the latest year of report

                soup_ad = bs(driver.page_source, 'html.parser')
                pdf_a = soup_ad.find(class_="attachment").find_all("a")
                pdf_urls = [i["href"] for i in pdf_a if is_annual_report(i.text)]

                # download pdf
                for pdf_url in pdf_urls:
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.get(f"{DISCLOSURE_URL}{pdf_url}")

                    # rename downloaded pdf to a relevant distinct name ({company_id}_{filename})
                    dl_name = ""
                    while dl_name.lower().endswith('.pdf') is False:
                        time.sleep(.25)
                        try:
                            dl_name = max([os.path.join(pdf_folder, f) for f in
                                           os.listdir(pdf_folder)], key=os.path.getctime)
                        except ValueError:
                            pass
                    file_name = os.path.split(dl_name)
                    new_file_name = os.path.join(file_name[0], f"{company_id}_{file_name[1]}")
                    try:
                        os.rename(dl_name, new_file_name)
                    except FileExistsError:
                        print(f"File name already exists. Please redownload here: "
                              f"{DISCLOSURE_URL}{pdf_urls[0]}")

                    dl_cnt += 1
                    driver.close()  # close pdf file tab

                else:
                    print(f"{dl_cnt} PDFs for company {company_id} has been downloaded")
                all_downloaded_pdfs_cnt += dl_cnt
                driver.switch_to.window(driver.window_handles[-1])
                driver.close()  # close announcement details iframe tab
            if dl_cnt == 0:
                print(f"No PDF downloaded for company {company_id}. Revisit here: "
                      f"{COMP_ANNOUNCE_URL}{company_id}{COMP_ANNOUNCE_URL2}")
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()  # close company announcements tab
        except Exception as e:
            print('Error: ', e)

    print()
    print(f"Downloading ENDED. Visited {len(urls)} company sites")
    print(f"Downloaded {all_downloaded_pdfs_cnt} PDFs")
    print(f"Time taken: {time.time() - start_time}")


def retrieve_company_ids():
    from selenium.webdriver.support.ui import Select
    options = Options()

    # options for running in headless mode (Chrome is not opened physically)
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = wd.Chrome(d, options=options)
    driver.get(ALL_COMPANY_LIST)

    # show all rows first before scraping
    select_view = Select(driver.find_element("id", "DataTables_Table_0_length")
                         .find_element("name", "DataTables_Table_0_length"))
    select_view.select_by_value("-1")
    time.sleep(.5)

    # start scraping all rows
    soup = bs(driver.page_source, 'html.parser')
    main_tbl = soup.find(id="DataTables_Table_0")
    all_a = main_tbl.find('tbody').find_all('a')  # all links from Company Name & Company Website col
    company_names_a = [i for i in all_a if LISTED_COMPANY_URL in str(i)]
    all_urls = [i['href'] for i in company_names_a]
    company_names = [i.text for i in company_names_a]
    company_ids = [i.replace(LISTED_COMPANY_URL, "") for i in all_urls]
    company_id_name_pair = list(zip(company_ids, company_names))
    return company_id_name_pair


if __name__ == '__main__':
    download_all_pdfs()
    # comp_id_name_pair = retrieve_company_ids()
    # print(len(comp_id_name_pair))
    # comp_csv = [",".join(i) for i in comp_id_name_pair]
    # with open("company_id_name_pair.csv", "w") as f:
    #     f.write("\n".join(comp_csv))
    # print("DONE")
