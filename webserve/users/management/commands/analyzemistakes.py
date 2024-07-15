import json
import matplotlib.pyplot as plt
import numpy as np
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Analyze and plot feature distribution from JSONL files"

    def add_arguments(self, parser):
        parser.add_argument("jsonl_file_fp", type=str, help="Path to the JSONL file containing top 20 near misses for false positives")
        parser.add_argument("jsonl_file_fn", type=str, help="Path to the JSONL file containing top 20 near misses for false negatives")

    def handle(self, *args, **options):
        jsonl_file_fp = options["jsonl_file_fp"]
        jsonl_file_fn = options["jsonl_file_fn"]

        # Read the JSONL files
        data_fp = self.read_jsonl(jsonl_file_fp)
        data_fn = self.read_jsonl(jsonl_file_fn)

        # Extract features
        features_fp = self.extract_features(data_fp)
        features_fn = self.extract_features(data_fn)

        # Plot feature distributions
        self.plot_feature_distributions(features_fp, "Feature Distribution - False Positives", "feature_distribution_fp.png")
        self.plot_feature_distributions(features_fn, "Feature Distribution - False Negatives", "feature_distribution_fn.png")

        # Plot feature clustering
        self.plot_feature_clustering(features_fp, features_fn, "Feature Clustering - False Positives vs False Negatives", "feature_clustering.png")

    def read_jsonl(self, filepath):
        data = []
        with open(filepath, 'r') as file:
            for line in file:
                data.append(json.loads(line))
        return data

    def extract_features(self, data):
        feature_names = data[0].keys() - {"predicted_probability", "url"}
        features = {name: [] for name in feature_names}
        
        for record in data:
            for feature in feature_names:
                features[feature].append(record[feature])
        
        return features

    def plot_feature_distributions(self, features, title, output_file):
        num_features = len(features)
        num_cols = 3
        num_rows = (num_features + num_cols - 1) // num_cols

        fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
        fig.suptitle(title)

        for idx, (feature, values) in enumerate(features.items()):
            row, col = divmod(idx, num_cols)
            ax = axes[row, col] if num_features > num_cols else axes[col]
            ax.hist(values, bins=20, edgecolor='k', alpha=0.7)
            ax.set_title(feature)
            ax.set_xlabel("Value")
            ax.set_ylabel("Frequency")

        for idx in range(len(features), num_rows * num_cols):
            fig.delaxes(axes.flatten()[idx])

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(output_file)
        plt.close()

        self.stdout.write(f"Feature distribution plot saved as {output_file}")

    def plot_feature_clustering(self, features_fp, features_fn, title, output_file):
        feature_names = list(features_fp.keys())
        num_features = len(feature_names)

        fig, axes = plt.subplots(num_features, num_features, figsize=(20, 20))
        fig.suptitle(title)

        for i in range(num_features):
            for j in range(num_features):
                ax = axes[i, j]
                if i == j:
                    ax.hist(features_fp[feature_names[i]], bins=20, color='blue', alpha=0.5, label='False Positives')
                    ax.hist(features_fn[feature_names[i]], bins=20, color='red', alpha=0.5, label='False Negatives')
                    ax.set_title(feature_names[i])
                else:
                    ax.scatter(features_fp[feature_names[i]], features_fp[feature_names[j]], color='blue', alpha=0.5, label='False Positives')
                    ax.scatter(features_fn[feature_names[i]], features_fn[feature_names[j]], color='red', alpha=0.5, label='False Negatives')

                if i == num_features - 1 and j == 0:
                    ax.legend(loc='upper left')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(output_file)
        plt.close()

        self.stdout.write(f"Feature clustering plot saved as {output_file}")
