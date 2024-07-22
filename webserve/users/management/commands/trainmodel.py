from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, precision_score, recall_score, f1_score, roc_auc_score
import json
import joblib
import numpy as np
import matplotlib.pyplot as plt

class Command(BaseCommand):
    help = "Train RF Model for article detection. Usage: python manage.py trainmodel <PATH TO FEATURES IN JSONL> <PATH TO SAVE MODEL>"

    def add_arguments(self, parser):
        parser.add_argument("data_path", type=str, help="Path to the feature data that will be used to train the classifier")
        parser.add_argument("model_path", type=str, help="Path where the trained model should be saved")

    def handle(self, *args, **options):
        X, y, urls, feature_names = self.get_data(path=options["data_path"])

        f = open("./logTrain.txt", "a")
        f.write(f"\n** New Run on {options['data_path']}** \n")
        f.write(f"Total # samples: {len(y)}\n")
        f.write(f"Articles: {np.array(y).sum(0)}\n")
        f.close()

        # Split, train, and evaluate the accuracy obtained
        X_train, X_test, y_train, y_test, urls_train, urls_test = train_test_split(X, y, urls, test_size=0.1, random_state=2)
        rf = RandomForestClassifier(n_estimators=100, random_state=2, class_weight='balanced', criterion='log_loss')
        rf.fit(X_train, y_train)
        y_hat = rf.predict(X_test)
        y_proba = rf.predict_proba(X_test)
   
        acc = accuracy_score(y_test, y_hat)
        precision = precision_score(y_test, y_hat)
        recall = recall_score(y_test, y_hat)
        f1 = f1_score(y_test, y_hat)
        roc_auc = roc_auc_score(y_test, y_hat)
        conf_matrix = confusion_matrix(y_test, y_hat, labels=rf.classes_)
        tn, fp, fn, tp = confusion_matrix(y_test, y_hat).ravel()
        disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix,
                                       display_labels=rf.classes_)
        disp.plot()
        plt.savefig("conf_matrix.png")

        f = open("./logTrain.txt", "a")
        f.write(f"Articles in test set:{np.array(y_test).sum(0)}\n")
        f.write("Random Forest \n")
        f.write(f"Confusion Matrix: {conf_matrix}\n")
        f.write(f"Precision: {precision}\n")
        f.write(f"Recall: {recall}\n")
        f.write(f"F1 Score: {f1}\n")
        f.write(f"ROC AUC Score: {roc_auc}\n")
        f.write(f"True Positives: {tp}\n")
        f.write(f"False Positives: {fp}\n")
        f.write(f"True Negatives: {tn}\n")
        f.write(f"False Negatives: {fn}\n")
        f.close()

        ## SVM
        svm = SVC(random_state=2)
        svm.fit(X_train, y_train)
        y_hat_svm = svm.predict(X_test)

        acc_svm = accuracy_score(y_test, y_hat_svm)
        precision_svm = precision_score(y_test, y_hat_svm)
        recall_svm = recall_score(y_test, y_hat_svm)
        f1_svm = f1_score(y_test, y_hat_svm)
        roc_auc_svm = roc_auc_score(y_test, y_hat_svm)
        conf_matrix_svm = confusion_matrix(y_test, y_hat_svm, labels=svm.classes_)
        tn_svm, fp_svm, fn_svm, tp_svm = confusion_matrix(y_test, y_hat_svm).ravel()
        f = open("./logTrain.txt", "a")
        f.write("SVM \n")
        f.write(f"Precision: {precision_svm}\n")
        f.write(f"Recall: {recall_svm}\n")
        f.write(f"F1 Score: {f1_svm}\n")
        f.write(f"ROC AUC Score: {roc_auc_svm}\n")
        f.write(f"True Positives: {tp_svm}\n")
        f.write(f"False Positives: {fp_svm}\n")
        f.write(f"True Negatives: {tn_svm}\n")
        f.write(f"False Negatives: {fn_svm}\n")
        f.close()



        # Find top 20 near misses for false positives
        false_positives = (y_test == 0) & (y_hat == 1)
        false_positive_probas = y_proba[false_positives, 1]
        sorted_indices_fp = np.argsort(false_positive_probas)
        near_misses_indices_fp = sorted_indices_fp[:20]
        top_20_near_misses_fp = X_test[false_positives][near_misses_indices_fp]
        top_20_near_misses_probas_fp = false_positive_probas[near_misses_indices_fp]
        top_20_near_misses_urls_fp = urls_test[false_positives][near_misses_indices_fp]

        # Save the false positive near misses to a JSONL file
        with open("./top_20_near_misses_fp.jsonl", "w") as file:
            for features, proba, url in zip(top_20_near_misses_fp, top_20_near_misses_probas_fp, top_20_near_misses_urls_fp):
                record = {name: int(value) if isinstance(value, np.integer) else value for name, value in zip(feature_names, features)}
                record["predicted_probability"] = float(proba)
                record["url"] = url
                file.write(json.dumps(record) + "\n")

        # Find top 20 near misses for false negatives
        false_negatives = (y_test == 1) & (y_hat == 0)
        false_negative_probas = y_proba[false_negatives, 0]
        sorted_indices_fn = np.argsort(false_negative_probas)
        near_misses_indices_fn = sorted_indices_fn[:20]
        top_20_near_misses_fn = X_test[false_negatives][near_misses_indices_fn]
        top_20_near_misses_probas_fn = false_negative_probas[near_misses_indices_fn]
        top_20_near_misses_urls_fn = urls_test[false_negatives][near_misses_indices_fn]

        # Save the false negative near misses to a JSONL file
        with open("./top_20_near_misses_fn.jsonl", "w") as file:
            for features, proba, url in zip(top_20_near_misses_fn, top_20_near_misses_probas_fn, top_20_near_misses_urls_fn):
                record = {name: int(value) if isinstance(value, np.integer) else value for name, value in zip(feature_names, features)}
                record["predicted_probability"] = float(proba)
                record["url"] = url
                file.write(json.dumps(record) + "\n")

        # Save the model and print stats
        joblib.dump(rf, options["model_path"])
        self.stdout.write(f"RF Acc: {acc}")
        self.stdout.write(f"SVM Acc: {acc_svm}")
        self.stdout.write(f"Model saved at {options['model_path']}")

    def get_data(self, path: str):
        feature_names = [
            "num_dashes",
            "num_slashes",
            "num_p_tags",
            "num_article_tags",
            "num_iframe_tags",
            "num_embed_tags",
            "num_blockquote_tags",
            "num_of_word_blog",
            "num_of_word_article"
        ]
        X = []
        y = []
        urls = []
        with open(path, 'r') as file:
            for line in file:
                data = json.loads(line)
                X.append([data[feature] for feature in feature_names])
                y.append(data["label"])
                urls.append(data["url"])
        return np.array(X), np.array(y), np.array(urls), feature_names
