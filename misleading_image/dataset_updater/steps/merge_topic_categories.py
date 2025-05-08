"""
Corrects the topic categories by mapping minor categories to major categories.
"""

# topic_mapper.py
from collections import defaultdict
from misleading_image.dataset_updater.step import Step
from misleading_image.dataset_updater.steps.add_topical_categories import add_topical_categories_step

# ────────────────────────────────────────────────────────────────────────────────
# 1. Build the mapping  (sub-topic  ➜  major topic)
# ────────────────────────────────────────────────────────────────────────────────
major_topics = {
    "Political Misinformation": [
        "Election Fraud/Integrity", "Policy Misrepresentation",
        "Political Figures"
    ],
    "Health and Medical Misinformation": [
        "Vaccines and Immunization", "Pandemics/Epidemics",
        "Medical Treatments/Cures"
    ],
    "Climate and Environmental Misinformation": [
        "Climate Change Denial", "Renewable Energy and Fossil Fuels",
        "Natural Disasters"
    ],
    "Economic Misinformation": [
        "Market Instability", "Inflation and Currency Manipulation",
        "Cryptocurrency Scams"
    ],
    "Social and Cultural Misinformation": [
        "Protests and Social Movements", "Religious Conflicts",
        "Gender and Identity"
    ],
    "War, Conflict, and Geopolitics": [
        "Conflict Zones", "International Relations",
        "Refugees and Migration"
    ],
    "Science and Technology Misinformation": [
        "Emerging Technologies", "Space Exploration",
        "Data and Cybersecurity"
    ],
    "Media and Communication Misinformation": [
        "Fake News Sites/Articles", "Out-of-Context Quotes",
        "Manipulated Media"
    ],
    "Criminal Activities and Scams": [
        "Human Trafficking Misinformation", "Scam Alerts",
        "Child Safety/Abductions"
    ],
    "Crisis and Emergency Situations": [
        "Natural Disasters", "Civil Unrest", "Public Safety Threats"
    ],
    "Historical Revisionism": [
        "Historical Figures/Events", "Monuments and Artifacts",
        "War Crimes and Atrocities"
    ],
    "Corporate and Brand Misinformation": [
        "Product Safety/Quality", "Boycotts/Defamation Campaigns",
        "Corporate Social Responsibility"
    ],
    "Conspiracy Theories": [
        "Global Cabal/New World Order", "Adrenochrome/Child Trafficking Theories",
        "5G/Technological Threats"
    ],
    "Misattributed or Fabricated Visuals": [
        "Photos Misused in New Contexts", "Deepfakes/AI-Generated Images",
        "Doctored Videos"
    ],
}

# Flatten into sub_topic ➜ major mapping (lower-cased keys for robustness)
sub_to_major = {
    sub.lower(): major for major, subs in major_topics.items() for sub in subs
}

# Also add identity mapping for the majors themselves
for major in major_topics.keys():
    sub_to_major[major.lower()] = major


def to_major(topic):
    """
    Converts to a sub topic or returns the same if it's a major topic.
    Errors if the topic is not found in the mapping.
    """

    topic = topic.lower()
    if topic in sub_to_major:
        return sub_to_major[topic]
    else:
        raise ValueError(f"Topic '{topic}' not found in the mapping.")
    


def merge_topic_categories(checkpoint):
    """
    Merges the topic categories in the dataset by mapping sub-topics to major topics.
    """
    if any(step.name == "Merge Topic Categories" for step in checkpoint.executed_steps):
        print("Existing step already executed")
        return

    existing_dataset = checkpoint.dataset
    merged_dataset = []

    for tweet in existing_dataset:
        if 'topical_categories' not in tweet:
            continue

        # Merge the topical categories
        merged_categories = set()
        for category in tweet['topical_categories']:
            try:
                merged_categories.add(to_major(category))
            except ValueError as e:
                print(e)

        tweet['topical_categories'] = list(merged_categories)
        merged_dataset.append(tweet)

    checkpoint.dataset = merged_dataset

merge_topic_categories_step = Step(
    name="Merge Topic Categories",
    action=merge_topic_categories,
    preconditions=[add_topical_categories_step],  # Ensure topical categories are added first
)