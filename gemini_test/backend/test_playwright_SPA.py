from main import read_web_page
try:
    print(">>> Testing Playwright Scraper on a JS SPA (keito.com) <<<")
    content = read_web_page("https://keito.com")
    print("====== FINAL EXTRACTED CONTENT ======")
    print(content[:1000] + "...")
except Exception as e:
    print("ERROR:", e)
