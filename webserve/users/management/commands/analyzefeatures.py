
# import json
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import os
# from django.core.management.base import BaseCommand

# class Command(BaseCommand):
#     help = "Analyze feature distributions among classes and generate histograms. Usage: python manage.py analyze_features <PATH TO FEATURES IN JSONL> [--single-file] [--with-kde] [--kde-only] [--truncate-outliers <N_STD>]"

#     def add_arguments(self, parser):
#         parser.add_argument("data_path", type=str, help="Path to the feature data in JSONL format")
#         parser.add_argument("--single-file", action="store_true", help="Save all histograms in a single file")
#         parser.add_argument("--with-kde", action="store_true", help="Include PDF (KDE curve) in the histograms")
#         parser.add_argument("--kde-only", action="store_true", help="Plot only the PDF (KDE curve) without histograms")
#         parser.add_argument("--truncate-outliers", type=float, help="Number of standard deviations from the mean to truncate outliers")

#     def handle(self, *args, **options):
#         X, y = self.get_data(path=options["data_path"])

#         features = ["num_dashes", "num_slashes", "num_p_tags", "num_article_tags", "num_iframe_tags", "num_embed_tags", "num_blockquote_tags"]

#         # Convert to numpy arrays for easier indexing
#         X = np.array(X)
#         y = np.array(y)
        
#         # Truncate outliers if specified
#         if options["truncate_outliers"]:
#             X = self.truncate_outliers(X, options["truncate_outliers"])
        
#         # Ensure output directory exists
#         output_dir = "./feature_histograms/"
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)
        
#         if options["single_file"]:
#             self.plot_all_histograms_in_single_file(X, y, features, output_dir, options["with_kde"], options["kde_only"])
#         else:
#             for i, feature in enumerate(features):
#                 self.plot_histogram(X[:, i], y, feature, output_dir, options["with_kde"], options["kde_only"])

#         self.stdout.write(self.style.SUCCESS("Histograms generated and saved in 'feature_histograms' directory."))

#     def get_data(self, path: str):
#         X = []
#         y = []
#         with open(path, 'r') as file:
#             for line in file:
#                 data = json.loads(line)
#                 X.append([
#                     data["num_dashes"],
#                     data["num_slashes"],
#                     data["num_p_tags"],
#                     data["num_article_tags"],
#                     data["num_iframe_tags"],
#                     data["num_embed_tags"],
#                     data["num_blockquote_tags"]
#                 ])
#                 y.append(data["label"])
#         return X, y

#     def truncate_outliers(self, X, n_std):
#         """Truncate outliers beyond n_std standard deviations from the mean."""
#         X_truncated = np.copy(X)
#         mean = np.mean(X_truncated, axis=0)
#         std = np.std(X_truncated, axis=0)
#         for i in range(X_truncated.shape[1]):
#             lower_bound = mean[i] - n_std * std[i]
#             upper_bound = mean[i] + n_std * std[i]
#             X_truncated[:, i] = np.clip(X_truncated[:, i], lower_bound, upper_bound)
        
#         self.stdout.write(f"Shape: {X_truncated.shape}")
#         return X_truncated

#     def plot_histogram(self, feature_data, labels, feature_name, output_dir, with_kde, kde_only):
#         classes = np.unique(labels)
        
#         plt.figure()
#         for class_label in classes:
#             if kde_only:
#                 sns.kdeplot(feature_data[labels == class_label], label=f'Class {class_label}', common_norm=False, alpha=0.5)
#             else:
#                 sns.histplot(feature_data[labels == class_label], kde=with_kde, bins=30, label=f'Class {class_label}', stat="density", common_norm=False, alpha=0.5)
        
#         plt.title(f'Feature Distribution: {feature_name}')
#         plt.xlabel(feature_name)
#         plt.ylabel('Density')
#         plt.legend(loc='upper right')
        
#         output_path = f"{output_dir}/{feature_name}_histogram.png"
#         plt.savefig(output_path)
#         plt.close()

#     def plot_all_histograms_in_single_file(self, X, y, features, output_dir, with_kde, kde_only):
#         classes = np.unique(y)
        
#         plt.figure(figsize=(20, 10))
#         for i, feature in enumerate(features):
#             plt.subplot(2, 4, i + 1)
#             for class_label in classes:
#                 if kde_only:
#                     sns.kdeplot(X[:, i][y == class_label], label=f'Class {class_label}', common_norm=False, alpha=0.5)
#                 else:
#                     sns.histplot(X[:, i][y == class_label], kde=with_kde, bins=30, label=f'Class {class_label}', stat="density", common_norm=False, alpha=0.5)
#             plt.title(f'Feature Distribution: {feature}')
#             plt.xlabel(feature)
#             plt.ylabel('Density')
#             plt.legend(loc='upper right')
        
#         output_path = f"{output_dir}/all_features_histogram.png"
#         plt.tight_layout()
#         plt.savefig(output_path)
#         plt.close()


import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

    def handle(self, *args, **options):
        X, y = self.get_data(path=options["data_path"])

        # Convert to numpy arrays for easier indexing
        X = np.array(X)
        y = np.array(y)
        
        # Truncate outliers if specified
        if options["truncate_outliers"]:
            X = self.truncate_outliers(X, options["truncate_outliers"])
        
        # Save truncated dataset if specified
        if options["save_truncated"]:
            self.save_truncated_data(X, y, options["save_truncated"])

        # Ensure output directory exists
        output_dir = "./feature_histograms/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if options["single_file"]:
            self.plot_all_histograms_in_single_file(X, y, output_dir, options["with_kde"], options["kde_only"])
        else:
            for i, feature in enumerate(["num_dashes", "num_slashes", "num_p_tags", "num_article_tags", "num_iframe_tags", "num_embed_tags", "num_blockquote_tags"]):
                self.plot_histogram(X[:, i], y, feature, output_dir, options["with_kde"], options["kde_only"])

        self.stdout.write(self.style.SUCCESS("Histograms generated and saved in 'feature_histograms' directory."))

    def get_data(self, path: str):
        X = []
        y = []
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
                    data["num_blockquote_tags"]
                ])
                y.append(data["label"])
        return X, y

    def truncate_outliers(self, X, n_std):
        """Truncate outliers beyond n_std standard deviations from the mean."""
        X_truncated = np.copy(X)
        mean = np.mean(X_truncated, axis=0)
        std = np.std(X_truncated, axis=0)
        for i in range(X_truncated.shape[1]):
            lower_bound = mean[i] - n_std * std[i]
            upper_bound = mean[i] + n_std * std[i]
            X_truncated[:, i] = np.clip(X_truncated[:, i], lower_bound, upper_bound)
        return X_truncated

    def save_truncated_data(self, X, y, save_path):
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
                        "label": int(y[i])
                }
                # print(data)
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
        
        plt.figure(figsize=(20, 10))
        for i, feature in enumerate(["num_dashes", "num_slashes", "num_p_tags", "num_article_tags", "num_iframe_tags", "num_embed_tags", "num_blockquote_tags"]):
            plt.subplot(2, 4, i + 1)
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
