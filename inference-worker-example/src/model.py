import pathlib

from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

import joblib


def train():
    iris_dataset = load_iris()

    X_train, X_test, y_train, y_test = train_test_split(
        iris_dataset["data"], iris_dataset["target"], random_state=0
    )
    kn = KNeighborsClassifier(n_neighbors=1)
    kn.fit(X_train, y_train)
    return kn


def save_model(kn):
    location = (
        pathlib.Path(__file__)
        .parent.parent.absolute()
        .joinpath("models", "clf_iris.joblib")
    )
    joblib.dump(kn, location)
    return location


def load_model():
    loaded_clf = joblib.load(
        str(
            pathlib.Path(__file__)
            .parent.joinpath("models", "clf_iris.joblib")
            .absolute()
        )
    )
    return loaded_clf


if __name__ == "__main__":
    kn = train()
    location = save_model(kn)
    kn = load_model()
    inp = [3, 4, 4, 3]
    print(kn.predict([inp]))
