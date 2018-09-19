import os, requests

def get_goodreads(isbn):
    response = requests.get("https://www.goodreads.com/book/review_counts.json", {"key": os.getenv("GoodReadsKey"), "isbns": isbn})
    return(response)

def main():
    # Do nothing
    return "Do nothing"

if __name__ == "__main__":
    main()
