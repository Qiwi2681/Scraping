import sys
import home_scraper
import subreddit_scraper
import post_scraper

if __name__ == "__main__":
    HOMEPAGE_SCROLLS = 2 # 40-180 subreddits
    SUBPAGE_SCROLLS = 2 # 20-40 posts per sub
    # 400 - 7200 urls per scrape

    #home page
    homepage = home_scraper.HomePageCrawler(HOMEPAGE_SCROLLS, threads=2)
    subreddits = homepage.scrape()

    #subreddits
    subpage = subreddit_scraper.SubRedditCrawler(SUBPAGE_SCROLLS, threads=4)
    posts = subpage.scrape(subreddits)

    #post scraper
    scraper = post_scraper.PostScraper(threads=4)
    scraper.scrape(posts)
