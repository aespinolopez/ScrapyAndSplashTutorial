import requests
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class VideoPipeline:

    def process_item(self, item, spider):
        if 'content' in item:
            url = item['content']
            video = requests.get(url, stream=True)
            chapter = url.split('_')[-1]
            with open('video/{}'.format(chapter), 'wb') as f:
                for chunk in video.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return item
