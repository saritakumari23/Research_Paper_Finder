import requests
import pandas as pd
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# PubMed API URLs
PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
DETAILS_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/fetch_papers", methods=["GET"])
def fetch_papers():
    query = request.args.get("query")
    
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    # Step 1: Search for papers on PubMed
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 10  # Limit results to 10
    }

    response = requests.get(PUBMED_API_URL, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch papers"}), 500
    
    data = response.json()
    paper_ids = data.get("esearchresult", {}).get("idlist", [])

    if not paper_ids:
        return jsonify({"message": "No papers found", "query": query})

    # Step 2: Fetch details for the retrieved paper IDs
    details_params = {
        "db": "pubmed",
        "id": ",".join(paper_ids),
        "retmode": "json"
    }

    details_response = requests.get(DETAILS_API_URL, params=details_params)
    details_data = details_response.json()

    papers = []
    for paper_id in paper_ids:
        paper_info = details_data.get("result", {}).get(paper_id, {})
        papers.append({
            "PubmedID": paper_id,
            "Title": paper_info.get("title", "N/A"),
            "Publication Date": paper_info.get("pubdate", "N/A"),
            "Link": f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"
        })

    return jsonify({"query": query, "papers": papers})

if __name__ == "__main__":
    app.run(debug=True)
