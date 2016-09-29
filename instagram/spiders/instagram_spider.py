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
        
        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)
        csrf = re.search(r"csrftoken\=(.+?)\;", str(response.headers)).group(1)
        
        response.headers['referer'] = 'https://www.instagram.com/explore/tags/{}/'.format(tag)
        response.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        response.headers['origin'] = 'https://www.instagram.com'
        response.headers['authority'] = 'www.instagram.com'
        response.headers['content-type'] = 'application/x-www-form-urlencoded'
        response.headers['x-csrftoken'] = csrf
        response.headers['x-requested-with'], response.headers['x-instagram-ajax'], response.headers['accept'] = 'XMLHttpRequest', '1', '*/*'
        response.headers['accept-encoding'], response.headers['accept-language']= 'gzip, deflate, br','en-US,en;q=0.8'

        end_cursor = re.search(r"\"end\_cursor\"\: \"(.+?)\"", html).group(1)
        
        #data = {"q" :"ig_hashtag({})+%7B+media.after({}+10)+%7B%0A++count%2C%0A++nodes+%7B%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=tags%3A%3Ashow".format(tag, end_cursor)}
        data = "q=ig_hashtag({})+%7B+media.after({}+9)+%7B%0A++count%2C%0A++nodes+%7B%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=tags%3A%3Ashow".format(tag, end_cursor)
        url = 'https://www.instagram.com/query/'

        print(data)
        print(response.headers)
        yield Request(url, body=data, method="POST", callback=self.parseHashtag)
        #yield FormRequest(url, formdata=data, callback=self.parseHashtag)

    def parseHashtag(self, response):
        body = response.xpath("//body")
        html = str(body.extract())

        print(response.body)
        print("_______________________________________________________________")
        print(len(url_codes))
        print("_______________________________________________________________")
        quit()
        exit()
        
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






