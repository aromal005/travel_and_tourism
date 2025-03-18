import requests

API_KEY = "0b02678dbe914e5d82a572f6c6b2e23f"

destination = "Munnar"  # Replace this with your selected destination

url = f"https://newsapi.org/v2/everything?q={destination} travel&language=en&apiKey={API_KEY}"

response = requests.get(url)
data = response.json()

if data["status"] == "ok" and "articles" in data:
    articles = data["articles"][:2]  # Get only the first two news articles
    if articles:
        for idx, article in enumerate(articles, 1):
            print(f"{idx}. {article['title']}\n   {article['url']}\n")
    else:
        print("No relevant travel news found for this destination.")
else:
    print("Error fetching travel news:", data.get("message", "Unknown error"))
