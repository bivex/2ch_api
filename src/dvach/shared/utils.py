from bs4 import BeautifulSoup

def strip_html(html_content: str) -> str:
    if not html_content:
        return ""
    # 2ch uses <br> for newlines, replace them before stripping
    soup = BeautifulSoup(html_content, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    return soup.get_text()
