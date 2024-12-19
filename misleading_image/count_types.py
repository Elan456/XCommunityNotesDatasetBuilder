"""
Given a json file with llm classifications, count the number of each type of classification.
"""

import json
import argparse 


def count_types(json_file):
    with open(json_file) as f:
        data = json.load(f)
    counts = {}
    for item in data:
        if not 'llm_image_classification' in item:
            print(f"Warning: item {item['id']} does not have a 'llm_image_classification' field")
            continue
        if item['llm_image_classification'] in counts:
            counts[item['llm_image_classification']] += 1
        else:
            counts[item['llm_image_classification']] = 1
    return counts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count the number of each type of classification in a json file')
    parser.add_argument('json_file', type=str, help='The json file to count classifications in')
    args = parser.parse_args()
    counts = count_types(args.json_file)
    print(counts)