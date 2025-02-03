import scrapy
import os
import urllib.parse

class FinanceGovSpider(scrapy.Spider):
    name = "finance_gov_spider"
    allowed_domains = ["finances.gov.tn"]
    start_urls = ["http://www.finances.gov.tn/fr/loi_finance?page=0"]
    
    def parse(self, response):
        # Extract PDF links and titles from the page
        for item in response.css("li"):  
            pdf_link = item.css("div.linkLien a::attr(href)").get()
            title = item.css("div.ttr::text").get()
            
            if pdf_link:
                pdf_url = response.urljoin(pdf_link)
                yield scrapy.Request(pdf_url, callback=self.save_pdf, meta={'title': title})
        
        # Find next page link and follow it
        next_page = response.css("li.pager__item.pager__item--next a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)
    
    def save_pdf(self, response):
        # Extract and decode the filename from the URL
        pdf_filename = response.url.split("/")[-1]  # Get last part of the URL
        pdf_filename = urllib.parse.unquote(pdf_filename)  # Decode URL encoding
        
        pdf_path = os.path.join("downloaded_pdfs", pdf_filename)
        pdf_title = response.meta.get('title', 'Unknown Title')
        
        # Ensure the download directory exists
        os.makedirs("downloaded_pdfs", exist_ok=True)

        # Save the PDF file
        with open(pdf_path, "wb") as f:
            f.write(response.body)
        
        yield {
            "pdf_url": response.url,
            "pdf_filename": pdf_filename,
            "pdf_title": pdf_title.strip() if pdf_title else "Unknown Title",
        }
