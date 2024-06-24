from django.core.management.base import BaseCommand, CommandError
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy, confusion_matrix
import json 
import joblib

class Command(BaseCommand):

    def args(self, parser):
        parser.add_argument("data_path", nargs="1", type=str, help="Path to the feature data that will be used to train the classifier")
        parser.add_argument("label_path", nargs="1", type=str, help="Path to the corresponding data label that will be used to train the classifier")
        parser.add_argument("model_path", nargs="1", type=str, help="Path where the trained model should be saved")

    def handle(self, *args, **options):
        
        #load data
        X = self.get_data(path=options["data_path"])
        y = self.get_data(path=options["label_path"])
        
        #split, train, and eval the acc obtained
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        rf = RandomForestClassifier(n_estimators=50, random_state=1)
        rf.fit(X_train, y_train)
        y_hat = rf.classify(X_test)
        accuracy = accuracy(y_test, y_hat)
        conf_matrix = confusion_matrix(y_test, y_hat)

        #save 
        self.stdout.write(f"Acc: {accuracy}")
        self.stdout.write(f"Conf Matrix: {conf_matrix}")
        joblib.dump(rf, options["model_path"])
        self.stdout.write(f"Model saved at {options["model_path"]}")
    
    def get_data(self, path:str):
        data = []
        with open(path, 'r') as file:
            for line in file:
                data.append(json.loads(line))
        return data