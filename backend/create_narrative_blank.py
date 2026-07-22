import pandas as pd

columns = [
    "Title", "Premise", "Validation: Listens / Charts / Awards", 
    "Current Audio Rights Holder", "Episode Count", "Format Type", 
    "Sub-genre", "Length (hrs)", "Series / Anthology", "Show structure", 
    "Licensing Confidence", "Final Priority", "Shicong's Notes", 
    "Rights required", "Amber's notes", "Rightsholder contact", 
    "Contact point", "Email (creator)", "Outreach status"
]

df = pd.DataFrame(columns=columns)
df.to_excel("Narrative_Podcasts_Blank.xlsx", index=False)
print("Created Narrative_Podcasts_Blank.xlsx successfully.")
