from numpy import median, mean, amax, amin
import  matplotlib.pyplot as plt
from prettytable import PrettyTable
IMAGE_DIR="/srv/ftp/share/archive/images/"

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
    for metric in ["Number of Words", "Word length"]:
        fig = plt.figure()
        fig.suptitle(metric)
        plot_index = 1
        for corpus, pairs in corpora.items():
            for pair, locales in pairs.items():
                for locale, files in locales.items():
                    axis = plt.subplot(len(corpora), len(locales) * 2, plot_index)
                    if metric == "Word length":
                        axis.set_ylim(0, 20)
                    elif metric == "Number of Words":
                        axis.set_ylim(0, 75)
                    plot_index += 1
                    plt.title(f"{corpus}: {pair}.{locale}")
                    data = []
                    for name, path in files.items():
                        if metric == "Word length":
                            data.append([len(word) for line in open(path) for word in line.split()])
                        elif metric == "Number of Words":
                            data.append([len(line.split()) for line in open(path)])
                    plt.boxplot(data, labels=files.keys(), showfliers=False, positions=range(1, len(data)*2, 2))
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(f"{IMAGE_DIR}/corpus_stats-{metric.replace(' ','_')}.png", bbox_inches="tight", dpi=100)

