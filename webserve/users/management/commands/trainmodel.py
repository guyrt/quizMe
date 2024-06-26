from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import json 
import joblib

class Command(BaseCommand):
    help ="Train RF Model for article detection. Usage: python manage.py trainmodel <PATH TO FEATURES IN JSONL> <PATH TO SAVE MODEL>"
    
    def add_arguments(self, parser):
        parser.add_argument("data_path", type=str, help="Path to the feature data that will be used to train the classifier")
        parser.add_argument("model_path", type=str, help="Path where the trained model should be saved")

    def handle(self, *args, **options):
        X, y = self.get_data(path=options["data_path"])

        # Split, train, and evaluate the accuracy obtained
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
        rf = RandomForestClassifier(n_estimators=50, random_state=1)
        rf.fit(X_train, y_train)
        y_hat = rf.predict(X_test)
        acc = accuracy_score(y_test, y_hat)
        # conf_matrix = confusion_matrix(y_test, y_hat)

        # Save the model and print stats
        # self.stdout.write(f"Confusion Matrix: {conf_matrix}")
        joblib.dump(rf, options["model_path"])
        self.stdout.write(f"Acc: {acc}")
        self.stdout.write(f"Model saved at {options['model_path']}")

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