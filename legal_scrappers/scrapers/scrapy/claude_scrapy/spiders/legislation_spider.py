import scrapy
from scrapy.http import Request, FormRequest

class LegislationSpider(scrapy.Spider):
    name = 'legislation'
    start_urls = ['https://legislation-securite.tn/latest-laws/']
    
    def __init__(self, *args, **kwargs):
        super(LegislationSpider, self).__init__(*args, **kwargs)
        self.current_page = 1

    def parse(self, response):
        # Extract law entries from the grid
        law_entries = response.css('.jet-listing-grid__item')
        
        for entry in law_entries:
            # Corrected date extraction
            date_cells = entry.css('.jet-table__body-cell .jet-table__cell-text::text')
            if len(date_cells) >= 1:
                date = date_cells[0].get().strip()
                
                # Corrected title and link extraction
                title = entry.css('.jet-table__cell-link .jet-table__cell-text::text').get().strip()
                link = entry.css('.jet-table__cell-link::attr(href)').get()

                # Follow the link to get the full content
                if link:
                    yield Request(
                        url=link, 
                        callback=self.parse_law_detail, 
                        meta={
                            'date': date, 
                            'title': title
                        }
                    )

        # Check for next page
        next_button = response.css('.jet-filters-pagination__item.prev-next.next .jet-filters-pagination__link')
        if next_button:
            # Increment page counter
            self.current_page += 1
            
            # Prepare AJAX request for next page
            yield FormRequest.from_response(
                response,
                formdata={
                    'action': 'jet_engine_ajax',
                    'handler': 'get_listing',
                    'page': str(self.current_page),
                    'query_id': 'laws'
                },
                callback=self.parse
            )

    def parse_law_detail(self, response):
        # Extract the law content from the specified div
        content_div = response.css('.elementor-column.elementor-element-fbd68d1 .elementor-widget-text-editor .elementor-widget-container').get()
        
        yield {
            'date': response.meta['date'],
            'title': response.meta['title'],
            'link': response.url,
            'content': content_div
        }