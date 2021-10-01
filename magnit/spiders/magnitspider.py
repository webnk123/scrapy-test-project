import scrapy
from scrapy_splash import SplashRequest
import time
from magnit.items import MagnitItem


class MagnitspiderSpider(scrapy.Spider):
    name = 'magnitspider'
    allowed_domains = ['magnitcosmetic.ru']
    slug = 'https://magnitcosmetic.ru'

    def start_requests(self):
        url = self.slug
        yield scrapy.Request(url=url, callback=self.get_catalog_link)

    def get_catalog_link(self,response):
        url = self.slug + response.xpath("//*[contains(text(), 'Косметика')]").css('a::attr(href)').get()
        yield scrapy.Request(url=url, callback=self.get_category_links)

# get 2 category links and pass them to scrapy-splash to render full page and generate product links
    def get_category_links(self,response):
        script = """
        function main(splash, args)
            splash.private_mode_enabled = false
            assert(splash:go(args.url))
            assert(splash:wait(5))
            a = tonumber(splash:select('.pageCount'):text()) 
            a = a - 1
            for i=1, a do
                btn = splash:select('.load_more_product_items')
                btn:mouse_click()
                assert(splash:wait(3))
            end
            return {
                html = splash:html(),
                har = splash:har()
                }
        end"""

        links = []

# scrapy crawl spider -a categories=val, val_val, val
# self.categories = [val, val val, val]
        categories = self.categories.split(',')
        for i in categories:
            i = i.replace("_"," ")
            link = self.slug + response.xpath("//*[contains(text(), '{}')]".format(i)).css('a::attr(href)').get() + '?perpage=96'
            time.sleep(1)
            yield SplashRequest(url=link, callback=self.scrape_product_links, endpoint='execute', args={'wait':0.5, 'lua_source':script, 'timeout': 3600}, dont_filter=True)

    def scrape_product_links(self,response):
        links = response.css(".red")
        print('done scraping product links ..... now scraping products')
        for i in links:
            link = self.slug + i.css(".product__link").css('a::attr(href)').get()
            price = i.css(".js-item_price-value::text").get()
            if price != None:
                is_in_stock = True
            else:
                is_in_stock = False
            yield scrapy.Request(url=link, callback=self.scrape_product, cb_kwargs=dict(price=price,is_in_stock=is_in_stock))

    def scrape_product(self,response, price, is_in_stock):
        print('+1 product')
        time.sleep(3)

        keys = response.css(".action-card__cell:nth-child(1)::text").getall()
        keys = [elem.strip() for elem in keys]
        values = response.css(".action-card__cell+ .action-card__cell::text").getall()
        values = [elem.strip() for elem in values]
        dictionary = dict(zip(keys, values))
        
        crumbs = response.css(".breadcrumbs__link::text").getall()
        crumbs = [elem.strip() for elem in crumbs]

        img_link = response.xpath("/html/body/div[1]/div[1]/div[2]/div[1]/div/div[2]/div/div[1]/img/@src").get()


        item = MagnitItem()
        description = response.css(".action-card__text:nth-child(1)::text").get().strip()
        description_dict = {"__description":description}
        metadata = description_dict.update(dictionary)

        print(price)
        item["timestamp"] = time.time()
        item["RPC"] = response.request.url.split("/")[-2]
        item["url"] = response.request.url
        item["title"] = response.css(".action-card__name::text").get().strip()
        item["marketing_tags"] = [] 
        item["brand"] = dictionary['Бренд:']
        item["section"] = crumbs
        item["price_data"] = {"current":price, "original":price, "sale_tag":""} 
        item["stock"] = {"in_stock": is_in_stock, "count": 0} 
        item["assets"] = {"main_image":[self.slug + img_link],"set_images":[''],"view360":[''],"video":['']}
        item["metadata"] = description_dict
        item["variants"] = 1

# check if product sale link is present else yield item
        sale_link = response.css(".event__product-name ::attr(href)").get()
        if sale_link != None:
            yield scrapy.Request(url=self.slug + sale_link, callback=self.scrape_sale, cb_kwargs=dict(item=item,price=price))
        else:
            yield item

    def scrape_sale(self,response, item,price):
        print("product is on sale!!!!")
        old_price = response.css(".action-card__price_old .action-card__price-rub::text").get().replace(",", ".")
        new_price = response.css(".action-card__price-rub::text").get().replace(",", ".")
        sale_tag = round(abs(new_price - old_price) / old * 100.0)
        if old_price != None:
            item["price_data"] = {"current":new_price,"original":old_price,"sale_tag":sale_tag}
        return item

"""
TODO  add this to splash script ^
        request:set_proxy{
        host = http://us-ny.proxymesh.com,
        port = 31280,
        username = username,
        password = secretpass,
    }
"""