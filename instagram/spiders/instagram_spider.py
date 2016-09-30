import scrapy
import re
from scrapy import Request, FormRequest


class InstagramUser(scrapy.Item):
    #origin = scrapy.Field()
    user = scrapy.Field() 
    post_count = scrapy.Field()
    follower_count = scrapy.Field()
    follows_count = scrapy.Field()
    code = scrapy.Field()

def regex_with_default(regex, string, group_number, default_return=0):
    try:
        result = int(re.search(regex, string).group(group_number))
    except ValueError:
        result = re.search(regex, string).group(group_number)
    except AttributeError:
        result = default_return
    return result

class InstagramSpider(scrapy.Spider):
    name = 'instagram_spider'
    
    '''
    hashtags = ['love', 'instagood', 'me', 'tbt', 'cute', 'follow', 'followme', 
    'photooftheday', 'happy', 'tagforlikes', 'beautiful', 'self', 'girl', 'picoftheday', 
    'like', 'smile', 'friends', 'fun', 'like', 'fashion', 'summer', 'instadaily', 'igers', 
    'instalike', 'food', 'swag', 'amazing', 'tflers', 'follow', 'bestoftheday', 'likeforlike', 
    'instamood', 'style', 'wcw', 'family', 'f', 'nofilter', 'lol', 'life', 'pretty', 'repost', 
    'hair', 'my', 'sun', 'webstagram', 'iphoneonly', 'art', 'tweegram', 'cool', 'followback', 
    'instafollow', 'instasize', 'bored', 'instacool', 'funny', 'mcm', 'instago', 'instasize', 
    'vscocam', 'girls', 'all', 'party', 'music', 'eyes', 'nature', 'beauty', 'night', 'fitness', 
    'beach', 'look', 'nice', 'sky', 'christmas', 'baby', 'selfie', 'like4like']
    '''
    hashtags = ['love']
    
    allowed_domains = ['https://www.instagram.com', 'www.instagram.com']
    start_urls = []
    for hashtag in hashtags:
        start_urls.append("https://www.instagram.com/explore/tags/%s/" % (hashtag))

    def parse(self, response):
        body = response.xpath("//body")
        html = str(body.extract())
        
        img_num = 48
        base_url = "https://www.instagram.com/query/"
        beginning_param = "?q=ig_hashtag("
        middle_param = ")%20%7B%20media.after("
        end_param = "%2C%20{})%20%7B%0A%20%20count%2C%0A%20%20nodes%20%7B%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20comments_disabled%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20%7B%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20%7D%2C%0A%20%20%20%20display_src%2C%0A%20%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20owner%20%7B%0A%20%20%20%20%20%20id%0A%20%20%20%20%7D%2C%0A%20%20%20%20thumbnail_src%2C%0A%20%20%20%20video_views%0A%20%20%7D%2C%0A%20%20page_info%0A%7D%0A%20%7D&ref=tags%3A%3Ashow".format(img_num)

        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)

        end_cursor = re.search(r"\"end\_cursor\"\: \"(.+?)\"", html).group(1)
        
        data = base_url + beginning_param + tag + middle_param + end_cursor + end_param
        #data = "https://www.instagram.com/query/?q=ig_hashtag({})%20%7B%20media.after({}%2C%2048)%20%7B%0A%20%20count%2C%0A%20%20nodes%20%7B%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20comments_disabled%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20%7B%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20%7D%2C%0A%20%20%20%20display_src%2C%0A%20%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20%7B%0A%20%20%20%20%20%20count%0A%20%20%20%20%7D%2C%0A%20%20%20%20owner%20%7B%0A%20%20%20%20%20%20id%0A%20%20%20%20%7D%2C%0A%20%20%20%20thumbnail_src%2C%0A%20%20%20%20video_views%0A%20%20%7D%2C%0A%20%20page_info%0A%7D%0A%20%7D&ref=tags%3A%3Ashow".format(tag, end_cursor)
        yield Request(data, callback=self.parseHashtag)

    def parseHashtag(self, response):
        body = response.xpath("//body")
        html = str(body.extract())
        
        url_codes = re.findall("\"code\"\: \"(.+?)\"", html)
        urls = []

        for code in url_codes:
            urls.append("https://www.instagram.com/p/%s/" % (code))
        for url in urls:
            print(url)
            yield Request(url, callback=self.parseImage)


    def parseImage(self, response):
        body = response.xpath("//body")
        html = str(body.extract())

        users = []

        users_in_html = re.findall(r"\"username\"\: \"(.+?)\"", html)
        users_in_html = list(set(users_in_html))
        for user in users_in_html:
            url = "https://www.instagram.com/%s/" % user
            yield Request(url, callback=self.parseUser)


    def parseUser(self, response):
        body = response.xpath("//body")
        html = str(body.extract())

        user = str(regex_with_default(r"\"username\"\: \"(.+?)\"", html, 1))
        post_count = int(regex_with_default(r"\"media\"\: \{\"count\"\: ([0-9]+)", html, 1))
        follower_count = int(regex_with_default(r"(?:\"followed_by\"\: \{\"count\"\: )([0-9]+)", html, 1))
        follows_count = int(regex_with_default(r"\"follows\"\: \{\"count\"\: ([0-9]+)", html, 1))
        code = int(regex_with_default(r"\"id\"\: \"([0-9]+)", html, 1))

        yield InstagramUser(user=user,post_count=post_count,
            follower_count=follower_count,follows_count=follows_count,
            code=code)






