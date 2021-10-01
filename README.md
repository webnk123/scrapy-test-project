test project written with scrapy and scrapy splash


INSTALL:

pip install requirements.txt

docker pull scrapinghub/splash

docker run -it -p 8050:8050 scrapinghub/splash --max-timeout 3600

USAGE:
pass categories to scrape , swap spaces for underscores

scrapy crawl magnitspider -a categories=Бритье_и_эпиляция,Средства_гигиены
