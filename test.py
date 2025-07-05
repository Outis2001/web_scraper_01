import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import multiprocessing as mp

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HighPerformanceScraper:
    def __init__(self, max_concurrent=10, use_selenium_fallback=True):
        self.max_concurrent = max_concurrent
        self.use_selenium_fallback = use_selenium_fallback
        self.session = None
        self.selenium_drivers = []

    async def create_session(self):
        """Create aiohttp session with optimized settings"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )

    def setup_selenium_driver(self):
        """Setup Selenium driver for fallback"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")

        service = Service(executable_path="./chromedriver-win64/chromedriver.exe")
        return webdriver.Chrome(service=service, options=chrome_options)

    async def scrape_with_aiohttp(self, url, session_id):
        """Fast scraping using aiohttp (for simple HTML parsing)"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.parse_html_fast(html, url)
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"aiohttp error for {url}: {str(e)}")
            return None

    def parse_html_fast(self, html, url):
        """Fast HTML parsing with BeautifulSoup"""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Fast extraction using CSS selectors
            data = {
                'Company_Name': self.extract_text(soup, '#listing-profile-heading'),
                'Address': self.extract_text(soup, '.col-md-10'),
                'Email': self.extract_text(soup, '.col-md-11'),
                'Contact_Number': self.extract_contact(soup),
                'Domain_Name': self.extract_domain(soup),
                'Listed_Under': self.extract_services(soup, 0),
                'Products_Services': self.extract_services(soup, 1),
                'URL': url,
                'Method': 'aiohttp'
            }
            return data
        except Exception as e:
            logger.error(f"HTML parsing error for {url}: {str(e)}")
            return None

    def extract_text(self, soup, selector):
        """Extract text using CSS selector"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None

    def extract_contact(self, soup):
        """Extract contact numbers"""
        elements = soup.select('.col-md-4')
        if len(elements) > 2:
            return elements[2].get_text(strip=True).split(',')
        return None

    def extract_domain(self, soup):
        """Extract domain name"""
        elements = soup.select('.col-md-8')
        if len(elements) > 2:
            return elements[2].get_text(strip=True)
        return None

    def extract_services(self, soup, index):
        """Extract services/products"""
        elements = soup.select('.company-service')
        if len(elements) > index:
            text = elements[index].get_text(strip=True)
            return text.split('\n')[1:] if '\n' in text else [text]
        return None

    def scrape_with_selenium(self, url):
        """Fallback Selenium scraping for complex pages"""
        driver = self.setup_selenium_driver()
        try:
            driver.get(url)
            time.sleep(2)  # Wait for page load

            # Your original Selenium extraction logic here
            data = {
                'Company_Name': self.selenium_extract(driver, 'id', 'listing-profile-heading'),
                'Address': self.selenium_extract(driver, 'class', 'col-md-10'),
                'Email': self.selenium_extract(driver, 'class', 'col-md-11'),
                'Contact_Number': self.selenium_extract_contact(driver),
                'Domain_Name': self.selenium_extract_domain(driver),
                'Listed_Under': self.selenium_extract_services(driver, 0),
                'Products_Services': self.selenium_extract_services(driver, 1),
                'URL': url,
                'Method': 'selenium'
            }
            return data
        except Exception as e:
            logger.error(f"Selenium error for {url}: {str(e)}")
            return None
        finally:
            driver.quit()

    def selenium_extract(self, driver, by_type, value):
        """Extract text using Selenium"""
        try:
            if by_type == 'id':
                elements = driver.find_elements('id', value)
            else:
                elements = driver.find_elements('class name', value)
            return elements[0].text if elements else None
        except:
            return None

    def selenium_extract_contact(self, driver):
        """Extract contact with Selenium"""
        try:
            elements = driver.find_elements('class name', 'col-md-4')
            if len(elements) > 2:
                return elements[2].text.split(',')
        except:
            pass
        return None

    def selenium_extract_domain(self, driver):
        """Extract domain with Selenium"""
        try:
            elements = driver.find_elements('class name', 'col-md-8')
            if len(elements) > 2:
                return elements[2].text
        except:
            pass
        return None

    def selenium_extract_services(self, driver, index):
        """Extract services with Selenium"""
        try:
            elements = driver.find_elements('class name', 'company-service')
            if len(elements) > index:
                return elements[index].text.split('\n')[1:]
        except:
            pass
        return None

    async def scrape_batch_async(self, urls):
        """Scrape a batch of URLs asynchronously"""
        if not self.session:
            await self.create_session()

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def scrape_with_semaphore(url, session_id):
            async with semaphore:
                return await self.scrape_with_aiohttp(url, session_id)

        # Create tasks for all URLs
        tasks = [scrape_with_semaphore(url, i) for i, url in enumerate(urls)]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        successful_results = []
        failed_urls = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task failed for URL {i}: {result}")
                failed_urls.append(urls[i])
            elif result is not None:
                successful_results.append(result)
            else:
                failed_urls.append(urls[i])

        return successful_results, failed_urls

    def scrape_failed_with_selenium(self, failed_urls):
        """Use Selenium for URLs that failed with aiohttp"""
        if not self.use_selenium_fallback or not failed_urls:
            return []

        logger.info(f"Using Selenium fallback for {len(failed_urls)} failed URLs")

        # Use ThreadPoolExecutor for parallel Selenium execution
        with ThreadPoolExecutor(max_workers=min(4, mp.cpu_count())) as executor:
            results = list(executor.map(self.scrape_with_selenium, failed_urls))

        return [r for r in results if r is not None]

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()


async def main():
    # Initialize high-performance scraper
    scraper = HighPerformanceScraper(max_concurrent=20, use_selenium_fallback=True)

    # Load URLs
    csv_name = "All_links"
    try:
        link_df = pd.read_csv(f"../Datasets/scraper_02/links/{csv_name}.csv")
        logger.info(f"Loaded {len(link_df)} links from CSV")
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        return

    lower_limit = 48000
    batch_size = 500  # Larger batches for async processing
    url_list = link_df['business_link'].tolist()[lower_limit:]

    all_results = []
    start_time = time.time()

    try:
        # Process in batches
        for i in range(0, len(url_list), batch_size):
            batch_urls = url_list[i:i + batch_size]
            current_index = lower_limit + i

            logger.info(
                f"Processing batch {i // batch_size + 1}: URLs {current_index} to {current_index + len(batch_urls)}")
            batch_start = time.time()

            # Async scraping (fast)
            successful_results, failed_urls = await scraper.scrape_batch_async(batch_urls)

            # Selenium fallback for failed URLs
            selenium_results = scraper.scrape_failed_with_selenium(failed_urls)

            # Combine results
            batch_results = successful_results + selenium_results

            if batch_results:
                batch_df = pd.DataFrame(batch_results)
                all_results.append(batch_df)

                # Save batch results
                filename = f"../Datasets/scraper_02/details/{csv_name}_batch_{i // batch_size + 1}_async.csv"
                batch_df.to_csv(filename, index=False)

                batch_time = time.time() - batch_start
                logger.info(
                    f"Batch completed in {batch_time:.2f}s. Success: {len(successful_results)}, Fallback: {len(selenium_results)}")

            # Small delay between batches
            await asyncio.sleep(2)

    finally:
        await scraper.close_session()

    # Combine all results
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        final_filename = f"../Datasets/scraper_02/details/{csv_name}_final_async.csv"
        final_df.to_csv(final_filename, index=False)

        total_time = time.time() - start_time
        logger.info(f"Scraping completed in {total_time:.2f}s. Total records: {len(final_df)}")


if __name__ == "__main__":
    asyncio.run(main())