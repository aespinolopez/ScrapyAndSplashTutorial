import json
import scrapy
from scrapy_splash import SplashRequest


LUA_SCRIPT = """
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(2))
  elems = splash:select_all('iframe')
  assert(elems)
  video_url = elems[2].node.attributes.src
  assert(video_url, 'invalid url: ' .. video_url)
  splash:go(video_url)
  assert(splash:wait(2))
  elem = splash:select('#message:first-child')
  assert(elem, 'div message not found')
  elem:mouse_click()
  splash:wait(3)
  video = splash:select('video')
  assert(video, 'video not found')
  return {
   content = video.firstChild.node.attributes.src
  }
end
"""


class AnimeSpider(scrapy.Spider):
    name = "animeflv"
    start_urls = [
        'https://animeflv.net/anime/4130/hunter-x-hunter-2011',
    ]
    custom_settings = {
        'SPLASH_URL': 'http://localhost:8050',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    }

    def parse(self, response):
        chapters = response.xpath('//ul[@class="ListEpisodes"]/li/a/@href').extract()
        for chapter in chapters:
            chapter_url = response.urljoin(chapter)
            request = SplashRequest(
                url=chapter_url,
                callback=self.get_video_url,
                endpoint="execute",
                args={"lua_source": LUA_SCRIPT}
            )
            yield request

    def get_video_url(self, response):
        json_response = json.loads(response.body.decode('utf-8'))
        yield json_response
