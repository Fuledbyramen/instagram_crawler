import scrapy
import re
from scrapy import Request, FormRequest
from sqlite3 import dbapi2 as sqlite
from time import time

connection = sqlite.connect('scrapy_insta_data.db')
cursor = connection.cursor()

user_counter = 0

class InstagramUser(scrapy.Item):
    #origin = scrapy.Field()
    user = scrapy.Field() 
    post_count = scrapy.Field()
    follower_count = scrapy.Field()
    follows_count = scrapy.Field()
    code = scrapy.Field()

class InstagramHashtag(scrapy.Item):
    tag = scrapy.Field()
    posts = scrapy.Field()
    entry_time = scrapy.Field()
    time_to_top = scrapy.Field()
    code = scrapy.Field()
    date = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()
    comment_count = scrapy.Field()
    ownerID = scrapy.Field()
    isVideo = scrapy.Field()
    imageID = scrapy.Field()

def boolean(string):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        print("Error in boolean function. Neither true nor false.")

def regex_with_default(regex, string, group_number, default_return=0):
    try:
        result = int(re.search(regex, string).group(group_number))
    except ValueError:
        result = re.search(regex, string).group(group_number)
    except AttributeError:
        result = default_return
    return result

def extractPostsFromPage(html, tag="FromUser", top_post = False):
    #all image url codes on the page
    if not top_post:
        url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)
    #used for extracting the top post information specifically if set to true
    #sets the code to be code of top post, a list of one code
    else:
        try:
            url_codes = [re.search(r"top_posts(?:.+?)code\"\: \"(.+?)\"", html).group(1)]
        except AttributeError:
            url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)

    #matches the code to the regex to ensure all regexes are to exact image
    for code in url_codes:
        date = int(re.search(r"{}(?:.+?)date\"\: ([0-9]+)".format(code), html).group(1))
        width = int(re.search(r"{}(?:.+?)width\"\: ([0-9]+)".format(code), html).group(1))
        height = int(re.search(r"{}(?:.+?)height\"\: ([0-9]+)".format(code), html).group(1))
        comment_count = int(re.search(r"{}(?:.+?)comments(?:.+?)([0-9]+)".format(code), html).group(1))
        caption = re.search(r"{}(?:.+?)caption\"\: \"(.+?)\"\, \"likes".format(code), html).group(1)
        owner = int(re.search(r"{}(?:.+?)owner(?:.+?)([0-9]+)".format(code), html).group(1))
        isvideo = re.search(r"{}(?:.+?)is_video\"\: ([a-z]+)".format(code), html).group(1)
        imageid = int(re.search(r"{}(?:.+?)is_video(?:.+?)id\"\: \"([0-9]+)".format(code), html).group(1))

        #check if image is already logged

        cursor.execute('SELECT code FROM insta_posts WHERE code = ?', (code,))
        preExisting = [a[0] for a in cursor.fetchall()]
        if top_post:
            return code, date, width, height, comment_count, owner, isvideo, imageid
        else:
            if not top_post:
                #posts are sorted by tags or user id's
                cursor.execute('INSERT INTO insta_posts (tag, code, date, width, height, comment_count, caption, ownerID, isVideo, imageID) VALUES (?,?,?,?,?,?,?,?,?,?)', (tag, code, date, width, height, comment_count, caption, owner, isvideo, imageid))

    connection.commit()
    print("____________________________________________________________________")
    print("____________________________________________________________________")

    print("______________________________COMMITED______________________________")
    print("____________________________________________________________________")
    print("____________________________________________________________________")


class InstagramSpider(scrapy.Spider):
    name = 'instagram_spider'

    cursor.execute("CREATE TABLE IF NOT EXISTS insta_posts(tag TEXT, code TEXT, date REAL, width REAL, height REAL, comment_count REAL, caption TEXT, ownerID REAL, isVideo TEXT, imageID REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS insta_users(user TEXT,  code REAL, post_count REAL, follower_count REAL, follows_count REAL, privacy TEXT, verification TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS insta_hashtags(tag TEXT, posts REAL, entry_time REAL, time_to_top REAL, code TEXT, date REAL, width REAL, height REAL, comment_count REAL, ownerID REAL, isVideo TEXT, imageID REAL)")


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
        #Takes a hashtag and extends the amount of photos on the page
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
        #Parses Hashtag Page
        body = response.xpath("//body")
        html = str(body.extract())
        
        response_url = str(response.url)
        tag = re.search(r"ig\_hashtag\(([a-z]+)", response_url).group(1)
        extractPostsFromPage(html, tag)

        #all image url codes on the page
        url_codes = re.findall(r"\"code\"\: \"(.+?)\"", html)

        #extract all hashtags used in captions on hashtag page
        #hashtags taken here may simply be jokes and have one or two photos in them so will not be parsed like a prolific hashtag
        #They will be added to a hashtag database and when the big hashtags are found, they will be added manually for now
        branchHashtags = re.findall(r"\#([A-Za-z]+)", html)
        #Each will be briefly searched to get stats on it for growth each time they are found
        #generate the urls from the branches
        for branch in branchHashtags:
            print(" HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHH")
            print("A HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHH")
            print("AH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHH")
            print("AHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHH")
            print("AHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHH")
            print("AHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHH H HHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHH HHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHH HHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHHH HHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHHHH HHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHHHHH HHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHHHHHH HHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHHHHHHH HHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHHHHHHHH HH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            print("AHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            url = "https://www.instagram.com/explore/tags/%s/".format(branch)
            yield Request(url, callback=self.parseBranchHashtag)

        #constructs url from url code
        for code in url_codes:
            url = "https://www.instagram.com/p/%s/" % (code)
            yield Request(url, callback=self.parseImage)



    def parseBranchHashtag(self, response):
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

        body = response.xpath("//body")
        html = str(body.extract())
        #the tag from the response url
        response_url = str(response.url)
        tag = re.search(r"explore\/tags\/(.+?)\/", response_url).group(1)
        #time of last post to see how frequency of posts
        last_post = re.search(r"date\"\: ([0-9]+)", html).group(1)
        #gets the total amount of posts to a hashtag
        post_count = re.search(r"\{\"TagPage\"\: \[\{\"tag\"\: \{\"media\"\: \{\"count\"\: ([0-9]+)", html).group(1)
        #TOP POSTS
        #current date time - when top post was posted to see how long it takes
        #return code, date, width, height, comment_count, owner, isvideo, imageid
        top_post_data = extractPostsFromPage(html, top_post=True)
        #amount of time it took to get to the top post
        top_post_duration = currentTime - int(top_post_data[1])
        #the tag name, amount of posts, time logged, time_to_top post, all stats of top post
        cursor.execute('INSERT INTO insta_hashtags (tag, posts, entry_time, time_to_top, code, date, width, height, comment_count, ownerID, isVideo, imageID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (tag, int(post_count), int(time()), top_post_duration, top_post_data[0], top_post_data[1], top_post_data[2], top_post_data[3], top_post_data[4], top_post_data[5], top_post_data[6], top_post_data[7]))
        connection.commit()

        yield InstagramHashtag(tag, int(post_count), int(time()), top_post_duration, top_post_data[0], top_post_data[1], top_post_data[2], top_post_data[3], top_post_data[4], top_post_data[5], top_post_data[6], top_post_data[7])

    def parseImage(self, response):
        body = response.xpath("//body")
        html = str(body.extract())

        users = []
        #all non duplicate usernames from image page aka commenters and the poster
        users_in_html = list(set(re.findall(r"\"username\"\: \"(.+?)\"", html)))
        for user in users_in_html:
            url = "https://www.instagram.com/%s/" % user
            yield Request(url, callback=self.parseUser)


    def parseUser(self, response):
        global user_counter
        body = response.xpath("//body")
        html = str(body.extract())

        #commit every five users
        if user_counter % 5 == 0:
            connection.commit()
        user_counter += 1
        #extract things specific to a user
        privacy = str(re.search(r"is\_private\"\: ([a-z]+)", html).group(1))
        user = str(re.search(r"\"username\"\: \"(.+?)\"", html).group(1))
        #private users require a different regex
        if privacy == "true":
            code = int(re.search(r"id\"\: \"([0-9]+)", html).group(1))
        else:
            code = int(re.search(r"owner\"(?:.+?)([0-9]+)", html).group(1))
        post_count = int(re.search(r"\"media\"\: \{\"count\"\: ([0-9]+)", html).group(1))
        follower_count = int(re.search(r"followed_by\"\: \{\"count\"\: ([0-9]+)", html).group(1))
        follows_count = int(re.search(r"\"follows\"\: \{\"count\"\: ([0-9]+)", html).group(1)) 
        verification = str(re.search(r"is_verified\"\: ([a-z]+)", html).group(1))
        #commit to the user database
        #regardless of next page, each user is logged unless previously logged
        #check if the user is already logged
        cursor.execute('SELECT user FROM insta_users WHERE code = ?', (code,))
        preExisting = [a[0] for a in cursor.fetchall()]
        if not preExisting:
            cursor.execute('INSERT INTO insta_users (user, code, post_count, follower_count, follows_count, privacy, verification) VALUES (?,?,?,?,?,?,?)',
                (user, code, post_count, follower_count, follows_count, privacy, verification))
        #then, if the user has more than 12 posts, aka a next page, load all those posts and log them with one network request
        #as long as they also are not private
        has_next_page = boolean(str(re.search(r"has_next_page\"\: ([a-z]+)",html).group(1)))
        if has_next_page and not boolean(privacy) and not preExisting:
            end_cursor = str(re.search(r"end_cursor\"\: \"([0-9]+)", html).group(1))
            #all their posts except the most recent 24, why 24?
            #No clue, instagram just prefers it

            if post_count > 124:
                img_num = str(100)
            else:
                img_num = str(post_count - 24)

            first = "https://www.instagram.com/query/?q=ig_user("
            second = ")%20{%20media.after("
            third = "%2C%20"
            fourth = ")%20{%0A%20%20count%2C%0A%20%20nodes%20{%0A%20%20%20%20caption%2C%0A%20%20%20%20code%2C%0A%20%20%20%20comments%20{%0A%20%20%20%20%20%20count%0A%20%20%20%20}%2C%0A%20%20%20%20comments_disabled%2C%0A%20%20%20%20date%2C%0A%20%20%20%20dimensions%20{%0A%20%20%20%20%20%20height%2C%0A%20%20%20%20%20%20width%0A%20%20%20%20}%2C%0A%20%20%20%20display_src%2C%0A%20%20%20%20id%2C%0A%20%20%20%20is_video%2C%0A%20%20%20%20likes%20{%0A%20%20%20%20%20%20count%0A%20%20%20%20}%2C%0A%20%20%20%20owner%20{%0A%20%20%20%20%20%20id%0A%20%20%20%20}%2C%0A%20%20%20%20thumbnail_src%2C%0A%20%20%20%20video_views%0A%20%20}%2C%0A%20%20page_info%0A}%0A%20}&ref=users%3A%3Ashow"
            #construct post url from all above
            data = first + str(code) + second + end_cursor + third + img_num + fourth        
            yield Request(data, callback=self.parseExtendedUser)

        yield InstagramUser(user=user,post_count=post_count,
            follower_count=follower_count,follows_count=follows_count,
            code=code)


    def parseExtendedUser(self, response):
        #calls the extraction of posts on the extended page
        #needs to be extra function to get the new request I guess
        body = response.xpath("//body")
        html = str(body.extract())

        extractPostsFromPage(html)


