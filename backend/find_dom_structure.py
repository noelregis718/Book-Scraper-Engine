from bs4 import BeautifulSoup
import pandas as pd

with open("full_dom.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

target = soup.find(string=lambda t: t and "Sunshine Nails" in t)
if target:
    print("Found in tag:", target.parent.name)
    print("Parent class:", target.parent.get("class"))
    print("Grandparent class:", target.parent.parent.get("class"))
    print("Great Grandparent class:", target.parent.parent.parent.get("class"))
else:
    print("Not found")
