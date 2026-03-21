from GoogleNews import GoogleNews

def test_googlenews_pkg():
    gn = GoogleNews(lang='en', region='US')
    gn.search('Gold market news')
    # This only gets the last 24h by default, but we can set a period
    # BUT we want specific dates.
    # gn.set_time_range('03/22/2023', '03/29/2023')
    results = gn.result()
    if results:
        print(f"Title: {results[0]['title']}")
        print(f"Link: {results[0]['link']}")
    else:
        print("No results found")

if __name__ == "__main__":
    test_googlenews_pkg()
