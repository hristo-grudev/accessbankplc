import scrapy

from scrapy.loader import ItemLoader

from ..items import AccessbankplcItem
from itemloaders.processors import TakeFirst


class AccessbankplcSpider(scrapy.Spider):
	name = 'accessbankplc'
	start_urls = ['https://www.accessbankplc.com/pages/Media/Press-Releases.aspx']

	def parse(self, response):
		post_links = response.xpath('//table[@class="table media-table mb100"]/tbody/tr')
		for post in post_links:
			url = post.xpath('.//div[@class="blog-side-detail"]//a/@href').get()
			date = post.xpath('.//div[@class="newspress-table-tt"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//ul[@class="pagination"]//a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h3/text()').get()
		description = response.xpath('//div[@class="media-press-contents"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=AccessbankplcItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
