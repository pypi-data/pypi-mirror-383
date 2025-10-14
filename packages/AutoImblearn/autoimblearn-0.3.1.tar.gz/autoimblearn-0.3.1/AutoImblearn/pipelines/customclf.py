import logging

import numpy as np
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, classification_report, \
    average_precision_score
from AutoImblearn.components.classifiers import RunSklearnClf, RunXGBoostClf

# Docker-based classifiers - factory functions similar to imputers
clfs = {
    "lr": lambda **kw: RunSklearnClf(model='lr', **kw),
    "mlp": lambda **kw: RunSklearnClf(model='mlp', **kw),
    "ada": lambda **kw: RunSklearnClf(model='ada', **kw),
    "svm": lambda **kw: RunSklearnClf(model='svm', **kw),
    # "ensemble": lambda **kw: RunXGBoostClf(model='ensemble', **kw),
}

class CustomClassifier:
    def __init__(self, args):
        # def __init__(self, X: pd.DataFrame, Y: pd.DataFrame):
        self.args = args
        self.data_folder = args.path
        # self.f1 = None
        # self.precision = None
        # self.recall = None
        # self.w_precision = None
        # self.w_recall = None
        # self.auroc = None
        # self.auprc = None
        #
        # self.c_index = None
        self.clf = None
        self.clf_name = None

    def train(self, X_train: np.ndarray, Y_train: np.ndarray, clf=None):
        # Train classifier
        if clf in clfs.keys():
            # Instantiate classifier with data_folder
            factory = clfs[clf]
            self.clf = factory(data_folder=self.data_folder)
            self.clf_name = clf
        else:
            raise Exception("Model {} not defined in model.py".format(clf))

        self.clf.fit(X_train, Y_train)

    def predict(self, X_test: np.ndarray, Y_test: np.ndarray):

        if self.args.metric == "auroc":
            y_proba = self.clf.predict_proba(X_test)[:, 1]
            auroc = roc_auc_score(Y_test, y_proba)
            self.result = auroc
            return auroc
        elif self.args.metric == "macro_f1":
            y_pred = self.clf.predict(X_test)
            _, _, f1, _ = (
                precision_recall_fscore_support(Y_test, y_pred, average='macro'))
            self.result = f1
            return f1
        else:
            raise ValueError("Metric {} is not supported in {}".format(self.args.metric, self.clf_name))
