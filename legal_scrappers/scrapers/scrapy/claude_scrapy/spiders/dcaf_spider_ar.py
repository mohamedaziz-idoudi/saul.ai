import scrapy
import re

class DcafSpiderArSpider(scrapy.Spider):
    name = "dcaf_spider_ar"
    allowed_domains = ["legislation-securite.tn"]
    start_urls = [
        "https://legislation-securite.tn/ar/latest-laws/أمر-رئاسي-عدد-691-لسنة-2022-مؤرخ-في-17-أوت-2022-يتعلق/"
    ]

    def parse(self, response):
        # Define the container with your CSS selector
        container_selector = (
            "body > div.elementor.elementor-49971.elementor-712.elementor-location-single.post-29678.latest-laws.type-latest-laws.status-publish.hentry.status-categories-188.text-type-categories-3321.institution-categories-342 > section > div > div.elementor-column.elementor-col-50.elementor-top-column.elementor-element.elementor-element-b973b8c > div > section > div > div.elementor-column.elementor-col-50.elementor-inner-column.elementor-element.elementor-element-fbd68d1 > div > div.elementor-element.elementor-element-a9246bd.elementor-widget.elementor-widget-jet-listing-dynamic-field > div > div > div > div"
        )
        container = response.css(container_selector)

        texts = []
        if container:
            # Collect all text from target tags (including all descendant nodes like <strong>)
            # The "//text()" will get text from within nested tags as well.
            text_nodes = container.xpath(
                ".//*[self::p or self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]//text()"
            ).getall()

            for text in text_nodes:
                # Replace non-breaking spaces with regular space
                cleaned = text.replace('\xa0', ' ').strip()
                # Remove any &nbsp; if still present (in case it's not automatically decoded)
                cleaned = cleaned.replace('&nbsp;', ' ')
                # Skip if the cleaned text is empty or only whitespace
                if cleaned and not re.match(r'^\s*$', cleaned):
                    texts.append(cleaned)

        # Yield the results (you could also join the texts into a single string if preferred)
        yield {
            "url": response.url,
            "content": texts,
        }