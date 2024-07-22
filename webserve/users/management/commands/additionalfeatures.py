import json
import os
import re
from django.core.management.base import BaseCommand
from urllib.parse import urlparse
class Command(BaseCommand):
    help = 'Process a JSONL file to generate extra features from URLs and save to a new JSONL file.'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str, help='Path to the input JSONL file')
        parser.add_argument('output_file', type=str, help='Path to the output JSONL file')
        parser.add_argument('--keywords', action="store_true", help="Generate features about specific keywords e.g article, blog")
        parser.add_argument('--non_domain', action="store_true", help="Include features about segment after url domain")
    
    def handle(self, *args, **options):
        input_file = options['input_file']
        output_file = options['output_file']
        keywords = ["blog", "article"]  # Replace with actual keywords

        data = self.get_data(input_file)
        processed_data = self.generate_features(data, keywords, options=options)
        self.save_data(processed_data, output_file)

        self.stdout.write(self.style.SUCCESS(f"Processed data saved to {output_file}"))

    def get_data(self, path):
        data = []
        with open(path, 'r') as file:
            for line in file:
                data.append(json.loads(line))
        return data

    def generate_features(self, data, keywords, options):
        if options["keywords"]:
            for item in data:
                url = item.get("url", "")
                for keyword in keywords:
                    item[f"num_of_word_{keyword}"] = len(re.findall(keyword, url))
        
        if options["non_domain"]:
            for item in data:
                url = item.get("url", "")
                parsed_url = urlparse(url)
                # Length of URL that is not part of the domain
                url_path = parsed_url.path + parsed_url.query + parsed_url.fragment
                item["length_non_domain"] = len(url_path)

        return data

    def save_data(self, data, path):
        with open(path, 'w') as file:
            for item in data:
                file.write(json.dumps(item) + "\n")
