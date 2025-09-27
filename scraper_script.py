import os
import requests
import time
import argparse
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
BASE_URL = "https://www.annualreports.com"
def scrape_reports(industry_url, limit=50, out_dir="data/pdfs"):
    os.makedirs(out_dir, exist_ok=True)
    response = requests.get(industry_url)
    soup = BeautifulSoup(response.text, "html.parser")
    company_links = [BASE_URL + a["href"] for a in soup.select(".report-item a")][:limit]
    pdf_paths = []
    for link in company_links:
        try:
            r = requests.get(link)
            s = BeautifulSoup(r.text, "html.parser")
            pdf_tag = s.select_one("a[href$='.pdf']")
            if not pdf_tag:
                continue
            pdf_url = pdf_tag["href"]
            filename = os.path.join(out_dir, os.path.basename(pdf_url))
            if not os.path.exists(filename):
                pdf = requests.get(pdf_url)
                with open(filename, "wb") as f:
                    f.write(pdf.content)
                time.sleep(1)
            pdf_paths.append(filename)
        except:
            pass
    return pdf_paths
def extract_text(pdf_path, out_dir="data/texts"):
    os.makedirs(out_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    out_path = os.path.join(out_dir, os.path.basename(pdf_path).replace(".pdf", ".txt"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    pdfs = scrape_reports(args.url, args.limit)
    for p in pdfs:
        extract_text(p)
    print(f"Downloaded and extracted {len(pdfs)} reports.")
