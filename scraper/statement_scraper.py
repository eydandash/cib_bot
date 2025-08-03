from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from webdriver_manager.chrome import ChromeDriverManager
from chromedriver_py import binary_path

def scrape_arabic_statements(driver) -> list[str]:
    """
    Scrapes PDF links for Arabic financial statements from the CIB website.

    Returns:
        List of URLs (strings) pointing to PDF files.
    """

    ar_doc_url = "https://www.cibeg.com/ar/investor-relations/ir-library/financial-statements"
    driver.get(ar_doc_url)
    time.sleep(5)  # Allow page to load

    ar_pdf_links: list[str] = []
    ar_doc_links = driver.find_elements(By.TAG_NAME, "a")

    for elem in ar_doc_links:
        href = elem.get_attribute("href")
        if href and href.endswith(".pdf"):
            ar_pdf_links.append(href)

    print(f"Found {len(ar_pdf_links)} PDFs")
    for link in ar_pdf_links:
        print(link)

    return ar_pdf_links


def scrape_english_statements(driver) -> list[str]:
    """
    Scrapes PDF links for English financial statements from the CIB website using an existing driver.

    Args:
        driver: Selenium WebDriver instance.

    Returns:
        List of URLs (strings) pointing to PDF files.
    """
    eng_doc_url = "https://www.cibeg.com/en/investor-relations/ir-library/financial-statements"
    driver.get(eng_doc_url)
    time.sleep(5)  # Allow page to load

    eng_pdf_links: list[str] = []
    eng_doc_links = driver.find_elements(By.TAG_NAME, "a")

    for elem in eng_doc_links:
        href = elem.get_attribute("href")
        if href and href.endswith(".pdf"):
            eng_pdf_links.append(href)

    print(f"Found {len(eng_pdf_links)} PDFs")
    for link in eng_pdf_links:
        print(link)

    return eng_pdf_links

def download_pdfs_with_metadata(pdf_data: list[tuple], download_dir: str = "statements") -> None:
    """
    Downloads PDF files with custom filenames based on metadata.
    
    Args:
        pdf_data: List of tuples containing metadata and URL
                 Format: (year, language, quarter, cs_sa, url)
        download_dir: Directory to save the downloaded PDFs (default: "statements")
    """
    import os
    
    download_path = os.path.abspath(download_dir)
    os.makedirs(download_path, exist_ok=True)

    # Check for existing files to avoid re-downloading
    existing_files = set(os.listdir(download_path))
    
    # Remove duplicates from pdf_data based on URL
    seen_urls = set()
    unique_data = []
    for item in pdf_data:
        url = item[-1]  # URL is always the last element
        if url not in seen_urls:
            seen_urls.add(url)
            unique_data.append(item)
    
    print(f"Removed {len(pdf_data) - len(unique_data)} duplicate links")

    # Setup Chrome for downloading
    options = Options()
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True  # bypass PDF viewer
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    # Download loop
    skipped = 0
    for idx, data in enumerate(unique_data, start=1):
        try:
            # Extract metadata and URL - should always be 5 elements
            year, language, quarter, cs_sa, url = data
            
            # Generate custom filename
            custom_filename = f"{year}_{language}_{quarter.lower()}_{cs_sa}.pdf"
            
            if custom_filename in existing_files:
                print(f"[{idx}/{len(unique_data)}] Skipping existing file: {custom_filename}")
                skipped += 1
                continue
                
            print(f"[{idx}/{len(unique_data)}] Downloading: {custom_filename}")
            
            driver.get(url)
            time.sleep(7)  # Allow time for PDF to load + trigger download
            
            # Rename the downloaded file to our custom name
            url_parts = url.rstrip('/').split('/')
            original_filename = url_parts[-1] if url_parts[-1] else url_parts[-2]
            original_path = os.path.join(download_path, original_filename)
            custom_path = os.path.join(download_path, custom_filename)
            
            # Wait a bit more and check if file was downloaded
            time.sleep(2)
            if os.path.exists(original_path):
                os.rename(original_path, custom_path)
                print(f"    ✅ Renamed to: {custom_filename}")
            
        except Exception as e:
            print(f"⚠️ Error with item {idx}: {e}")

    driver.quit()
    print(f"✅ All downloads attempted. Skipped {skipped} existing files.")

def download_pdfs(pdf_links: list[str], download_dir: str = "statements") -> None:
    """
    Downloads PDF files from the provided links to a specified directory.
    
    Args:
        pdf_links: List of PDF URLs to download
        download_dir: Directory to save the downloaded PDFs (default: "statements")
    """
    import os
    
    download_path = os.path.abspath(download_dir)
    os.makedirs(download_path, exist_ok=True)

    # Check for existing files to avoid re-downloading
    existing_files = set(os.listdir(download_path))
    
    # Remove duplicates from pdf_links
    unique_links = list(set(pdf_links))
    print(f"Removed {len(pdf_links) - len(unique_links)} duplicate links")

    # Setup Chrome for downloading
    options = Options()
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True  # bypass PDF viewer
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    # Download loop
    skipped = 0
    for idx, url in enumerate(unique_links, start=1):
        try:
            # Extract filename from URL
            filename = url.split('/')[-1]
            if filename in existing_files:
                print(f"[{idx}/{len(unique_links)}] Skipping existing file: {filename}")
                skipped += 1
                continue
                
            print(f"[{idx}/{len(unique_links)}] Opening: {url}")
            driver.get(url)
            time.sleep(7)  # Allow time for PDF to load + trigger download
        except Exception as e:
            print(f"⚠️ Error with {url}: {e}")

    driver.quit()
    print(f"✅ All downloads attempted. Skipped {skipped} existing files.")