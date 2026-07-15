# Json to XML File Converter
## I make it when Hianime got shut down and had a json file and the internet wasn't helping me do it so I decided to do it myself
## Languages: [Python]
## ​Tools: [VS Code]
## Features
* **Automated Conversion**: Converts your JSON watchlists into clean XML.
* **API Integration**: Connects with Jikan API to fetch and store necessary metadata (e.g., MAL IDs).
* **Smart Caching**: Local caching ensures subsequent runs are fast and efficient.

## Prerequisites
* **Python 3.x**
* **Requests library**: Install it using:
  ```bash
  pip install requests
  ##How to use
  Place your watching.json, completed.json, and plan-to-watch.json files in the project folder.
  Run the script:
  python merge.py
## Your converted XML file will be generated in the same directory.
