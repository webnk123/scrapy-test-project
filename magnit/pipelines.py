# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter
"""
class MagnitPipeline:

    def open_spider(self, spider):
        self.file = open('data.json', 'w', encoding='utf8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, 'NULL')
        a = json.dump(dict(item), self.file, ensure_ascii=False)
        return item


from itemadapter import ItemAdapter
import json  # Json package of python module.
  """
  
class MagnitPipeline:
    def process_item(self, item, spider):  # default method
        # calling dumps to create json data.
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # converting item to dict above, since dumps only intakes dict.
        self.file.write(line)                    # writing content in output file.
        return item
  
    def open_spider(self, spider):
        self.file = open('result.json', 'w', encoding='utf8')
  
    def close_spider(self, spider):
        self.file.close()