"""
.. module:: Datasets.py

setup.py
******

:Description: Datasets.py

    Datasets functions

:Authors:
    bejar

:Version: 

:Date:  06/05/2022
"""

from apafib.config import DATALINK, datasets
import pandas as pd
from sklearn.utils import Bunch
import remotezip
import gzip
import struct
import requests
from io import BytesIO
import numpy as np
import re
from collections import Counter


def fetch_apa_data(name, version, target_column, return_X_y=False, as_frame=True):
    """_dataset fetching function_

    Args:
        name (_type_): _description_
        version (_type_): _description_
        target_column (_type_): _description_
        return_X_y (bool, optional): _description_. Defaults to True.
        as_frame (bool, optional): _description_. Defaults to False.
    """
    if name not in datasets:
        raise NameError("Dataset is not valid")
    maxver, fname = datasets[name]
    if version > maxver:
        raise NameError("Invalid version")

    fname += f"{version}"
    data = pd.read_csv(f"{DATALINK}/{fname}.csv", header=0, delimiter=",", decimal=".")

    # Check if target column/columns exist
    if type(target_column) is not list:
        target_column = [target_column]

    for t in target_column:
        if t not in data.columns:
            raise NameError(f"Target column {t} invalid")

    data_X = data.loc[:, ~data.columns.isin(target_column)].copy()
    data_y = data.loc[:, target_column].copy()

    if return_X_y:
        return (data_X.to_numpy(), data_y.to_numpy())

    b = Bunch()
    b["data"] = data_X if as_frame else data_X.to_numpy()
    b["target"] = data_y if as_frame else data_y.to_numpy()
    b["feature_names"] = data_X.columns
    b["target_names"] = data_y.columns
    if as_frame:
        b["frame"] = data.copy()

    return b


def fetch_dataset(fname, compressed=False, index=False, pickled=False):
    if compressed:
        if index:
            return pd.read_csv(
                f"{DATALINK}/{fname}.csv.gz",
                na_values="",
                sep=",",
                header=0,
                index_col=0,
            )
        else:
            return pd.read_csv(
                f"{DATALINK}/{fname}.csv.gz", na_values="", sep=",", header=0
            )
    elif index:
        return pd.read_csv(
            f"{DATALINK}/{fname}.csv", na_values="", sep=",", header=0, index_col=0
        )
    elif pickled:
        return pd.read_pickle(f"{DATALINK}/{fname}.pkl")
    else:
        return pd.read_csv(f"{DATALINK}/{fname}.csv", na_values="", sep=",", header=0)


def load_vehiculos():
    r = requests.get(f"{DATALINK}/cifar10.npz", stream=True)
    data = np.load(BytesIO(r.raw.read()))
    return data["data"], data["labels"]


def load_smile():
    r = requests.get(f"{DATALINK}/smile.npz", stream=True)
    data = np.load(BytesIO(r.raw.read()))
    return data["images"], data["labels"]


def load_BCN_Francia():
    return fetch_dataset("BCN_Francia", index=True)


def load_BCN_air():
    return fetch_dataset("BCN_air", index=True)


def load_BCN_vuelos():
    return fetch_dataset("BCN_vuelos", index=True)


def load_BCN_ruidosos():
    return fetch_dataset("BCN_ruidosos", index=True)


def load_BCN_conmuters():
    return fetch_dataset("BCN_conmuters", index=True)


def load_Google():
    return fetch_dataset("NASDAQ_Google", index=True)


def load_alzheimer():
    return fetch_dataset("alzheimers", compressed=False)


def load_clientes():
    return fetch_dataset("customer_data", compressed=False)


def load_dormir():
    return fetch_dataset("Sleep_health", compressed=False)


def load_cupid():
    return fetch_dataset("OKCupid_profiles", compressed=False)


def load_fraude():
    return fetch_dataset("fraud_data", compressed=False)


def load_health_news():
    return fetch_dataset("health_news", compressed=True)


def load_MITBIH():
    return fetch_dataset("mitbih_data", compressed=True)


def load_sms_spam():
    return pd.read_csv(f"{DATALINK}/SMSSpamCollection.csv.gz", header=None, delimiter='\t')


def load_stress():
    return fetch_dataset("StudentStress", compressed=True)


def load_food():
    return fetch_dataset("food_data", compressed=True, index=True)


def load_travel_review():
    return fetch_dataset("trip_review")


def load_wages():
    return fetch_dataset("wages")


def load_credit_scoring():
    return fetch_dataset("credsco")


def load_medical_costs():
    return fetch_dataset("insurance")


def load_stroke():
    return fetch_dataset("stroke-data")


def load_wind_prediction():
    return fetch_dataset("wind-dataset")


def load_BCN_IBEX():
    return fetch_dataset("BCNDiari2021-IBEX")


def load_BCN_UK():
    return fetch_dataset("BCNDiari2021-UK")


def load_BCN_cesta():
    return fetch_dataset("BCNDiari2021-CESTA")


def load_BCN_vuelos2021():
    return fetch_dataset("BCNDiari2021-vuelos")


def load_BCN_ruido():
    return fetch_dataset("BCNDiari2021-ruido")


def load_BCN_calor():
    return fetch_dataset("BCN_calor", index=True)


def load_BCN_museos():
    return fetch_dataset("BCN_Museos", index=True)


def load_BCN_NO2():
    return fetch_dataset("BCN_NO2", index=True)


def load_BCN_sanciones():
    return fetch_dataset("BCN_sanciones", index=True)


def load_BCN_precios():
    return fetch_dataset("BCN_precios", index=True)


def load_titanic():
    return fetch_dataset("titanic")


def load_king_county_houses():
    return fetch_dataset("kc_house_data", compressed=True)


def load_crabs():
    return fetch_dataset("crabs").drop(columns="index")


def load_life_expectancy():
    return fetch_dataset("Life_Expectancy_Data")


def load_electric_devices():
    data = pd.read_csv(
        f"{DATALINK}/ElectricDevices_TRAIN.csv", header=None, na_values="?"
    )
    data.columns = ["Class"] + [
        f"H{i:02d}:{j}" for i in range(24) for j in ["00", "15", "30", "45"]
    ]
    data["Class"] = data["Class"] - 1
    return data


def load_energy():
    return fetch_dataset("Energy")


def load_attrition():
    return fetch_dataset("attrition")


def load_heart_failure():
    return fetch_dataset("heart_failure")


def load_darwin():
    return fetch_dataset("DARWIN")


def load_bands():
    return fetch_dataset("bands")


def load_column():
    return fetch_dataset("column_3C")


def load_mpg():
    return fetch_dataset("mpg")

def load_potability():
    return fetch_dataset("water_potability")

def load_world_music():
    return fetch_dataset("WorldMusic", pickled=True)

def load_car_sales():
    return fetch_dataset("CarSales", pickled=True)

def load_CIS_Impuestos():
    return fetch_dataset("Impuestos", pickled=True)

def load_CIS_ICC():
    return fetch_dataset("IndiceConfianzaClass", pickled=True)

def load_CIS_cultura():
    return fetch_dataset("CulturaClass", pickled=True)

def load_arxiv():
    bk = remotezip.RemoteZip(f"{DATALINK}/arxiv.zip", initial_buffer_size=6_000_000)
    text = []
    labels = []
    for f in sorted([fn for fn in bk.namelist() if "0" in fn]):
        labels.append(f.split("/")[1].lower())
        text.append(str(bk.read(f)).replace("\\n", " "))

    return text, labels

def load_papers():
    bk = remotezip.RemoteZip(f"{DATALINK}/papers.zip", initial_buffer_size=6_000_000)
    text = []
    labels = []
    for f in sorted([fn for fn in bk.namelist() if "0" in fn]):
        labels.append(f.split("/")[1].lower())
        text.append(str(bk.read(f)).replace("\\n", " "))

    return text, labels


def load_literature():
    authors = [
        "bacon",
        "machiavelli",
        "montaigne",
        "erasmus",
        "descartes",
        "defoe",
        "spinoza",
        "swift",
        "hobbes",
        "kant",
        "conrad",
        "austen",
        "goethe",
        "rousseau",
        "schopenhauer",
        "melville",
        "dumas",
        "bronte",
        "doyle",
        "wells",
        "lovecraft",
        "london",
        "fitzgerald",
    ]

    bk = remotezip.RemoteZip(f"{DATALINK}/Books.zip", initial_buffer_size=6_000_000)
    book_class = pd.read_csv(
        bk.open("Books/Classes.csv"), header=0, index_col=0, delimiter=","
    )

    text = []
    labels = []
    lab = "century"
    for f in sorted([fn for fn in bk.namelist() if "txt" in fn]):
        fname = f.split("/")
        if len(fname) > 1:
            author = fname[2]
            if author[:-6].lower() in authors:
                labels.append(book_class.loc[author[:-6].lower(), lab])
                frag = str(bk.read(f))
                text.append(frag)

    return text, labels


def load_translation():
    authors = [
        "lovecraft",
        "hobbes",
        "wilde",
        "stevenson",
        "joyce",
        "fitzgerald",
        "austen",
        "bacon",
        "melville",
        "kipling",
        "flaubert",
        "cervantes",
        "goethe",
        "plato",
        "nietzsche",
        "dostoyevsky",
        "verne",
        "pushkin",
        "dante",
        "spinoza",
    ]

    bk = remotezip.RemoteZip(f"{DATALINK}/Books.zip", initial_buffer_size=6_000_000)
    book_class = pd.read_csv(
        bk.open("Books/Classes.csv"), header=0, index_col=0, delimiter=","
    )

    text = []
    labels = []
    lab = "language"
    for f in sorted([fn for fn in bk.namelist() if "txt" in fn]):
        fname = f.split("/")
        if len(fname) > 1:
            author = fname[2]
            if author[:-6].lower() in authors:
                labels.append(book_class.loc[author[:-6].lower(), lab])
                frag = str(bk.read(f))
                text.append(frag)

    return text, labels


def load_MNIST(digits=(3, 5, 6, 8, 9), sel=4):
    def load_data(link, labels=False):
        file = requests.get(link)
        with gzip.open(BytesIO(file.content), "rb") as f:
            magic, size = struct.unpack(">II", f.read(8))
            if labels:
                data = np.frombuffer(
                    f.read(), dtype=np.dtype(np.uint8).newbyteorder(">")
                )
                data = data.reshape((size,))  # (Optional)
            else:
                nrows, ncols = struct.unpack(">II", f.read(8))
                data = np.frombuffer(
                    f.read(), dtype=np.dtype(np.uint8).newbyteorder(">")
                )
                data = data.reshape((size, nrows, ncols))
        return data

    X_train_o = load_data(f"{DATALINK}/train-images.idx3-ubyte.gz")
    X_test_o = load_data(f"{DATALINK}/t10k-images.idx3-ubyte.gz")
    y_train_o = load_data(f"{DATALINK}/train-labels.idx1-ubyte.gz", labels=True
    )
    y_test_o = load_data(f"{DATALINK}/t10k-labels.idx1-ubyte.gz", labels=True
    )

    cselect = np.zeros(y_train_o.shape, dtype=bool)
    for d in digits:
        cselect = np.logical_or(cselect, y_train_o == d)
    X_train = X_train_o[cselect]
    y_train = y_train_o[cselect]

    cselect = np.zeros(y_test_o.shape, dtype=bool)
    for d in digits:
        cselect = np.logical_or(cselect, y_test_o == d)  
    X_test = X_test_o[cselect]
    y_test = y_test_o[cselect]

    for i in range(len(digits)):
        y_train[y_train == digits[i]] = i+10
        y_test[y_test == digits[i]] = i+10
    y_train = y_train - 10
    y_test = y_test - 10
    return (
        X_train.reshape(-1, 28 * 28)[::sel] / 255,
        X_test.reshape(-1, 28 * 28)[::sel] / 255,
        y_train[::sel],
        y_test[::sel],
    )


def load_NASDAQ():
    files = [
        "HistoricalData_GOOGLE.csv",
        "HistoricalData_MSFT.csv",
        "HistoricalData_AAPL.csv",
        "HistoricalData_INTEL.csv",
        "HistoricalData_AMD.csv",
    ]

    ddata = {}

    for f in files:
        hcdo = (
            pd.read_csv(f"{DATALINK}/{f}", index_col="Date")
            .reset_index()
            .sort_index(ascending=False)
            .reset_index()
        )
        ddata[f.split(".")[0].split("_")[1] + "-P"] = hcdo["Close/Last"]
        ddata[f.split(".")[0].split("_")[1] + "-V"] = hcdo["Volume"]
        ddata[f.split(".")[0].split("_")[1] + "-GAP"] = (
            hcdo["High"] - hcdo["Low"]
        ).abs()

    return pd.DataFrame(ddata).reset_index().drop(columns="index")


def load_sentiment(nwords, train_size=0.8):
    def tweet_to_words(raw_tweet):
        letters_only = re.sub("[^a-zA-Z@]", " ", raw_tweet)
        words = letters_only.lower().split()
        meaningful_words = [w for w in words if not re.match("^[@]", w)]
        return " ".join(meaningful_words)

    bk = remotezip.RemoteZip(f"{DATALINK}/Airlines.zip", initial_buffer_size=6_000_000)
    Tweet = pd.read_csv(bk.open("Airlines.csv"))
    Tweet["clean_tweet"] = Tweet["text"].apply(lambda x: tweet_to_words(x))
    Tweet["sentiment"] = Tweet["twsentiment"].apply(
        lambda x: 0 if x == "negative" else 1
    )
    all_text = " ".join(Tweet["clean_tweet"])
    words = all_text.split()

    counts = Counter(words)
    vocab = sorted(counts, key=counts.get, reverse=True)[:nwords]
    vocab_to_int = {word: ii for ii, word in enumerate(vocab, 1)}

    tweet_ints = []
    for each in Tweet["clean_tweet"]:
        tweet_ints.append(
            [vocab_to_int[word] for word in each.split() if word in vocab_to_int]
        )

    labels = np.array(Tweet["sentiment"])
    tweet_len = Counter([len(x) for x in tweet_ints])
    tweet_idx = [idx for idx, tweet in enumerate(tweet_ints) if len(tweet) > 0]
    labels = labels[tweet_idx]
    Tweet = Tweet.iloc[tweet_idx]
    tweet_ints = [tweet for tweet in tweet_ints if len(tweet) > 0]

    seq_len = max(tweet_len)
    features = np.zeros((len(tweet_ints), seq_len), dtype=int)
    for i, row in enumerate(tweet_ints):
        features[i, -len(row) :] = np.array(row)[:seq_len]

    split_idx = int(len(features) * train_size)
    X_train, val_x = features[:split_idx], features[split_idx:]
    y_train, val_y = labels[:split_idx], labels[split_idx:]

    test_idx = int(len(val_x) * 0.5)
    X_val, X_test = val_x[:test_idx], val_x[test_idx:]
    y_val, y_test = val_y[:test_idx], val_y[test_idx:]

    return X_train, y_train, X_val, y_val, X_test, y_test
