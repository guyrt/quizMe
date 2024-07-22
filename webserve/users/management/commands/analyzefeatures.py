import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.parse import urlparse
from collections import Counter
import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Analyze feature distributions among classes and optionally save the truncated dataset to JSONL. Usage: python manage.py analyze_features <PATH TO FEATURES IN JSONL> [--single-file] [--with-kde] [--kde-only] [--truncate-outliers <N_STD>] [--save-truncated <PATH TO SAVE TRUNCATED JSONL>]"

    def add_arguments(self, parser):
        parser.add_argument("data_path", type=str, help="Path to the feature data in JSONL format")
        parser.add_argument("--single-file", action="store_true", help="Save all histograms in a single file")
        parser.add_argument("--with-kde", action="store_true", help="Include PDF (KDE curve) in the histograms")
        parser.add_argument("--kde-only", action="store_true", help="Plot only the PDF (KDE curve) without histograms")
        parser.add_argument("--truncate-outliers", type=float, help="Number of standard deviations from the mean to truncate outliers")
        parser.add_argument("--save-truncated", type=str, help="Path where the truncated dataset should be saved in JSONL format")
        parser.add_argument("--count", action="store_true", help="count num of occurences of a specific url")
        parser.add_argument("--count-remove", action="store_true", help="after count remove")
    def handle(self, *args, **options):
        X, y, urls = self.get_data(path=options["data_path"])

        # Convert to numpy arrays for easier indexing
        X = np.array(X)
        y = np.array(y)
        urls = np.array(urls)

        if options["count"]:
            url_frag= "https://www.google.com/maps/"
            counter=0
            for url in urls:
                if url_frag in url:
                    counter+=1
            print(f"{url_frag} appeared {counter} times")
   
            if options["count_remove"]:
                indices_to_remove = [i for i, url in enumerate(urls) if url_frag in url][:850]
                X = np.delete(X, indices_to_remove, axis=0)
                y = np.delete(y, indices_to_remove, axis=0)
                urls = np.delete(urls, indices_to_remove, axis=0)

            url_frag= "https://www.linkedin.com/"
            counter=0
            for url in urls:
                if url_frag in url:
                    counter+=1
            print(f"{url_frag} appeared {counter} times")
            
            if options["count_remove"]:
                indices_to_remove = [i for i, url in enumerate(urls) if url_frag in url][:427]
                X = np.delete(X, indices_to_remove, axis=0)
                y = np.delete(y, indices_to_remove, axis=0)
                urls = np.delete(urls, indices_to_remove, axis=0)

            # Save the remaining data to a JSONL file
           
            X = [dict(zip(["num_dashes","num_slashes", "num_p_tags", "num_article_tags", "num_iframe_tags","num_embed_tags","num_blockquote_tags","num_of_word_blog","num_of_word_article", "length_non_domain"], x)) for x in X.tolist()]
            y = y.tolist()
            urls = urls.tolist()
            output_data = [{'url': url, **x, 'label': y_val} for url, x, y_val in zip(urls, X, y)]
            output_file_path = 'less_links_wo_outliers_data2.jsonl'

            with open(output_file_path, 'w') as f:
                for entry in output_data:
                    f.write(json.dumps(entry))
                    f.write('\n')
            
            # Extract domains and count them
            domains = [urlparse(url).netloc for url in urls]
            domain_counts = Counter(domains).most_common(10)

            # Create histogram
            domains, counts = zip(*domain_counts)
            plt.figure(figsize=(10, 5))
            plt.bar(domains, counts)
            plt.xlabel('Domain')
            plt.ylabel('Count')
            plt.title('Top 10 Most Frequent Domains')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Save histogram to a file
            histogram_file_path = 'domain_histogram.png'
            plt.savefig(histogram_file_path)
            exit(1)

    
    # Truncate outliers if specified
        if options["truncate_outliers"]:
            X, y, urls = self.truncate_outliers(X, y, urls, options["truncate_outliers"])
        
        # Save truncated dataset if specified
        if options["save_truncated"]:
            self.save_truncated_data(X, y, urls, options["save_truncated"])
        
        # Ensure output directory exists
        output_dir = "./feature_histograms/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if options["single_file"]:
            self.plot_all_histograms_in_single_file(X, y, output_dir, options["with_kde"], options["kde_only"])
        else:
            #adjust according to feat
            for i, feature in enumerate(["num_dashes", "num_slashes", "num_p_tags", "num_article_tags", "num_iframe_tags", "num_embed_tags", "num_blockquote_tags", "num_of_word_blog", "num_of_word_article"]):
                self.plot_histogram(X[:, i], y, feature, output_dir, options["with_kde"], options["kde_only"])

        self.stdout.write(self.style.SUCCESS("Histograms generated and saved in 'feature_histograms' directory."))

        
    def get_data(self, path: str):
        X = []
        y = []
        urls = []
        with open(path, 'r') as file:
            for line in file:
                data = json.loads(line)
         
                X.append([
                    data["num_dashes"],
                    data["num_slashes"],
                    data["num_p_tags"],
                    data["num_article_tags"],
                    data["num_iframe_tags"],
                    data["num_embed_tags"],
                    data["num_blockquote_tags"],
                    data["num_of_word_blog"],
                    data["num_of_word_article"],
                    data["length_non_domain"]
                ])
                y.append(data["label"])
                urls.append(data.get("url", ""))
        return X, y, urls

    def truncate_outliers(self, X, y, urls, n_std):
        """Truncate outliers beyond n_std standard deviations from the mean."""
        mean = np.mean(X, axis=0)
        std = np.std(X, axis=0)
        
        mask = np.ones(X.shape[0], dtype=bool)
        
        for i in range(X.shape[1]):
            lower_bound = mean[i] - n_std * std[i]
            upper_bound = mean[i] + n_std * std[i]
            mask &= (X[:, i] >= lower_bound) & (X[:, i] <= upper_bound)
        
        return X[mask], y[mask], urls[mask]

    def save_truncated_data(self, X, y, urls, save_path):
        """Save the truncated dataset to a new JSONL file."""
        with open(save_path, 'w') as file:
            for i in range(len(X)):
                data = {
                        "num_dashes": int(X[i][0]),
                        "num_slashes": int(X[i][1]),
                        "num_p_tags": int(X[i][2]),
                        "num_article_tags": int(X[i][3]),
                        "num_iframe_tags": int(X[i][4]),
                        "num_embed_tags": int(X[i][5]),
                        "num_blockquote_tags": int(X[i][6]),
                        "num_of_word_blog": int(X[i][7]),
                        "num_of_word_article": int(X[i][8]),
                        "length_non_domain":int(X[i][9]),
                        "label": int(y[i]),
                        "url": urls[i]
                }
                file.write(json.dumps(data) + "\n")
   
    def plot_histogram(self, feature_data, labels, feature_name, output_dir, with_kde, kde_only):
        classes = np.unique(labels)
        
        plt.figure()
        for class_label in classes:
            if kde_only:
                sns.kdeplot(feature_data[labels == class_label], label=f'Class {class_label}', common_norm=False, alpha=0.5)
            else:
                sns.histplot(feature_data[labels == class_label], kde=with_kde, bins=30, label=f'Class {class_label}', stat="density", common_norm=False, alpha=0.5)
        
        plt.title(f'Feature Distribution: {feature_name}')
        plt.xlabel(feature_name)
        plt.ylabel('Density')
        plt.legend(loc='upper right')
        
        output_path = f"{output_dir}/{feature_name}_histogram.png"
        plt.savefig(output_path)
        plt.close()

    def plot_all_histograms_in_single_file(self, X, y, output_dir, with_kde, kde_only):
        classes = np.unique(y)
        
        plt.figure(figsize=(30, 10))
        for i, feature in enumerate(["num_dashes", "num_slashes", "num_p_tags", "num_article_tags", "num_iframe_tags", "num_embed_tags", "num_blockquote_tags", "num_of_word_blog", "num_of_word_article", "length_non_domain"]):
            plt.subplot(4, 4, i + 1)
            for class_label in classes:
                if kde_only:
                    sns.kdeplot(X[:, i][y == class_label], label=f'Class {class_label}', common_norm=False, alpha=0.5)
                else:
                    sns.histplot(X[:, i][y == class_label], kde=with_kde, bins=30, label=f'Class {class_label}', stat="density", common_norm=False, alpha=0.5)
            plt.title(f'Feature Distribution: {feature}')
            plt.xlabel(feature)
            plt.ylabel('Density')
            plt.legend(loc='upper right')
        
        output_path = f"{output_dir}/all_features_histogram.png"
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
