from numpy import median, mean, amax, amin
from parse_logs import parse
import  matplotlib.pyplot as plt
from prettytable import PrettyTable

IMAGE_DIR = "/srv/ftp/share/archive/images/"
EXAMPLE_RUNS = {
        "training": {
            "good": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws6-train-2019-07-10T23+02:00.log",
            "bad": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmpc302-train-Clean-de-en08",
        }, "hyper_opt": {
            "Top 10": [
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.09",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws6-train-2019-07-10T23+02:00.log",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.08",
#                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws4-train-2019-07-07T12+02:00.log",
#                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmpc302-train-Clean-de-en01",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmpc302-Clean-de-en.06",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmpc302-train-Clean-de-en04",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.02",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.03",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/training-train-2019-07-02T16+02:00.log",
            ]
        }
        }

CORPORA = {
        "ECB": {
            "de-en": {
                "de": {
                    "orignal": "/srv/ftp/share/archive/stats/orig/ECB.de-en.de",
                    "train": "/srv/ftp/share/archive/stats/new/ECB/Train.de-en.de",
                    "valid": "/srv/ftp/share/archive/stats/new/ECB/Valid.de-en.de"
                }, "en": {
                    "orignal": "/srv/ftp/share/archive/stats/orig/ECB.de-en.en",
                    "valid":  "/srv/ftp/share/archive/stats/new/ECB/Train.de-en.en",
                    "train": "/srv/ftp/share/archive/stats/new/ECB/Valid.de-en.en"}
            }, "cs-en": {
                "cs": {
                    "orignal": "/srv/ftp/share/archive/stats/orig/ECB.cs-en.cs",
                    "valid":  "/srv/ftp/share/archive/stats/new/ECB/Train.cs-en.cs",
                    "train": "/srv/ftp/share/archive/stats/new/ECB/Valid.cs-en.cs"
                }, "en": {
                    "orignal": "/srv/ftp/share/archive/stats/orig/ECB.cs-en.en",
                    "valid":  "/srv/ftp/share/archive/stats/new/ECB/Train.cs-en.en",
                    "train": "/srv/ftp/share/archive/stats/new/ECB/Valid.cs-en.en"}}
    }, "EMEA": {
        "de-en": {
            "de": {
                "orignal": "/srv/ftp/share/archive/stats/orig/EMEA.de-en.de",
                "valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.de-en.de",
                "train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.de-en.de" 
            }, "en": {
                "orignal": "/srv/ftp/share/archive/stats/orig/EMEA.de-en.en",
                "valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.de-en.en",
                "train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.de-en.en"}
        }, "cs-en": {
            "cs": {
                "orignal": "/srv/ftp/share/archive/stats/orig/EMEA.cs-en.cs",
                "valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.cs-en.cs",
                "train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.cs-en.cs"
            }, "en": {
                "orignal": "/srv/ftp/share/archive/stats/orig/EMEA.cs-en.en",
                "valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.cs-en.en",
                "train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.cs-en.en"}}
    }, "Europarl": {
        "de-en": {
            "de": {
                "orignal": "/srv/ftp/share/archive/stats/orig/Europarl.de-en.de",
                "valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.de-en.de",
                "train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.de-en.de" 
            }, "en": {
                "orignal": "/srv/ftp/share/archive/stats/orig/Europarl.de-en.en",
                "valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.de-en.en",
                "train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.de-en.en"}
        }, "cs-en": {
            "cs": {
                "orignal": "/srv/ftp/share/archive/stats/orig/Europarl.cs-en.cs",
                "valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.cs-en.cs",
                "train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.cs-en.cs"
            }, "en": {
                "orignal": "/srv/ftp/share/archive/stats/orig/Europarl.cs-en.en",
                "valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.cs-en.en",
                "train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.cs-en.en"}}
                }
        }

def calculate_corpus_stats(path):
    number_of_words = [len(line.split()) for line in open(path)]
    word_lengths = [len(word) for line in open(path) for word in line.split()]
    return {
        "number_of_words": {
            "min": amin(number_of_words),
            "median": median(number_of_words),
            "mean": mean(number_of_words),
            "max": amax(number_of_words),
        }, "word_lengths": {
            "min": amin(word_lengths),
            "median": median(word_lengths),
            "mean": mean(word_lengths),
            "max": amax(word_lengths),
        }
    }

def print_corpus_stats(corpora=CORPORA):
    table = PrettyTable(["corpus", "pair", "locale", "type", "words", "word length"])
    table.sortby = "words"
    table.float_format = "0.3"
    for corpus, pairs in corpora.items():
        for pair, locales in pairs.items():
            for locale, files in locales.items():
                for name, path in files.items():
                    stats = calculate_corpus_stats(path)
                    table.add_row([corpus, pair, locale, name, stats["number_of_words"]["mean"], stats["word_lengths"]["mean"]]) 
    print(table)

def plot_corpus_stats(corpora=CORPORA):
    for metric in ["Number of Words per Sentence", "Word Length"]:
        fig = plt.figure()
        fig.suptitle(metric)
        plot_index = 1
        for corpus, pairs in corpora.items():
            for pair, locales in pairs.items():
                for locale, files in locales.items():
                    axis = plt.subplot(len(corpora), len(locales) * 2, plot_index)
                    if metric == "Word Length":
                        axis.set_ylim(0, 20)
                    elif metric =="Number of Words per Sentence":
                        axis.set_ylim(0, 75)
                    plot_index += 1
                    plt.title(f"{corpus}: {pair}.{locale}")
                    data = []
                    for name, path in files.items():
                        if metric == "Word Length":
                            data.append([len(word) for line in open(path) for word in line.split()])
                        elif metric == "Number of Words per Sentence":
                            data.append([len(line.split()) for line in open(path)])
                    plt.boxplot(data, labels=files.keys(), showfliers=False, positions=range(1, len(data)*2, 2))
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(f"{IMAGE_DIR}/corpus_stats-{metric.replace(' ','_')}.png", bbox_inches="tight", dpi=400)
        plt.clf()

def plot_trainings_curve(files=EXAMPLE_RUNS["training"]):
    for name, path in files.items():
        train_stats = parse(path)
        for corpus in train_stats:
            fig = plt.figure()
            fig.suptitle(f"Trainings Curve: {corpus}")
            plot_index = 1
            for run in train_stats[corpus]["train"]:
                axis = plt.subplot(len(train_stats[corpus]["train"]), 1, plot_index)
                axis.set_xlabel("Trainings Steps")
                axis.set_ylabel("Accuracy")
                plot_index += 1
                axis.set_ylim(0, 100)

                data = {
                        "step":[point.get("step", 0) for point in run["steps"]],
                        "train":[point.get("train_accuracy", 0) for point in run["steps"]],
                        "valid":[point.get("valid_accuracy", 0) for point in run["steps"]],
                        }
                plt.scatter(data["step"], data["train"], label="Trainings Accuracy")
                plt.scatter(data["step"], data["valid"], label="Validation Accuracy")
                axis.legend()

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(f"{IMAGE_DIR}/trainings_curve-{name}.png", bbox_inches="tight", dpi=200)
        plt.clf()

def plot_hyperparameter_optim(files=EXAMPLE_RUNS["hyper_opt"], metric="bleu"):
    for group in files:
        fig = plt.figure()
        fig.suptitle(f"Model Fittness according to {metric}-Score")
        train_stats = parse(files[group])
        for corpus in train_stats:
            plot_index = 1
            axis = plt.subplot(len(train_stats) * 2, 1, plot_index)
            for i, run in enumerate(train_stats[corpus]["train"]):
                axis.set_ylim(0, 100)
                axis.set_xlabel("Trainings Steps")
                axis.set_ylabel("Score")
                data = {
                        "train-steps":[int(point.get("step", 0)) for point in run["steps"][::5]],
                        "valid":[float(point.get("valid_accuracy", 0)) for point in run["steps"][::5]],
                        }
                if i == 0:
                    plt.scatter(data["train-steps"], data["valid"], marker="x", label=f"Validation Accuracy")
                else:
                    plt.scatter(data["train-steps"], data["valid"], 0.1, marker="x")
            axis.legend()

            plot_index += 1
            axis = plt.subplot(len(train_stats) * 2, 1, plot_index)
            for i, run in enumerate(train_stats[corpus]["train"]):
                axis.set_ylim(0, 100)
                axis.set_xlabel("Trainings Steps")
                axis.set_ylabel("Score")
                data = {
                        "score-steps":[int(point.get("step", 0)) for point in run["scores"]],
                        "score":[float(point.get(metric, 0)) for point in run["scores"]],
                        }
                if i == 0:
                    plt.scatter(data["score-steps"], data["score"], marker="^", label=f"{metric}-Score")
                else:
                    plt.scatter(data["score-steps"], data["score"], 5, marker="o")
            axis.legend()

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(f"{IMAGE_DIR}/optim_comparison-{group.replace(' ','_')}.png", bbox_inches="tight", dpi=200)
    plt.clf()

