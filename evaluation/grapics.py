from numpy import median, mean, amax, amin
from parse_logs import parse
from functools import reduce
from hyperparams import load_scores
import  matplotlib.pyplot as plt
from prettytable import PrettyTable

IMAGE_DIR = "/srv/ftp/share/archive/images/"
EXAMPLE_RUNS = {
        "training": {
            "good": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws6-train-2019-07-10T23+02:00.log",
            "bad": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmpc302-train-Clean-de-en08",
        }, "hyper_opt": {
            "Top 10-real": [
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
            ],
            "Top 10-fancy": [
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws2-train-2019-08-06T21+02:00.log",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws10-train-2019-08-06T21+02:00.log",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws4-train-2019-08-06T21+02:00.log",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-2019-08-06T21+02:00.log",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws9-train-2019-08-06T21+02:00.log",
                "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws6-train-2019-08-06T21+02:00.log",
                ]
        }, "side_constraint": {
            "de-en": {
                "ECB": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.09",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-de-en/logs/wtmgws9-train-Tagged-de-en.08",
                }, "EMEA": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.09",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-de-en/logs/wtmgws9-train-Tagged-de-en.08",
                }, "Europarl": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.09",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-de-en/logs/wtmgws9-train-Tagged-de-en.08",
                }, "mixed": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-de-en/logs/wtmgws5-train-Clean-de-en.09",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-de-en/logs/wtmgws9-train-Tagged-de-en.08",
                }
            }, "cs-en": {
                "ECB": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-cs-en/logs/wtmgws6-Clean-cs-en.09.log",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-cs-en/logs/wtmgws2-Tagged-cs-en12",
                }, "EMEA": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-cs-en/logs/wtmgws6-Clean-cs-en.09.log",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-cs-en/logs/wtmgws2-Tagged-cs-en12",
                }, "Europarl": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-cs-en/logs/wtmgws6-Clean-cs-en.09.log",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-cs-en/logs/wtmgws2-Tagged-cs-en12",
                }, "mixed": {
                    "Clean": "/srv/ftp/share/archive/results/Clean-cs-en/logs/wtmgws6-Clean-cs-en.09.log",
                    "Tagged": "/srv/ftp/share/archive/results/Tagged-cs-en/logs/wtmgws2-Tagged-cs-en12",
                }
            }
        }
    }

CORPORA = {
        "ECB": {
            "de-en": {
                "de": {
                    "Qrignal": "/srv/ftp/share/archive/stats/orig/ECB.de-en.de",
                    "Train": "/srv/ftp/share/archive/stats/new/ECB/Train.de-en.de",
                    "Valid": "/srv/ftp/share/archive/stats/new/ECB/Valid.de-en.de"
                }, "en": {
                    "Qrignal": "/srv/ftp/share/archive/stats/orig/ECB.de-en.en",
                    "Talid":  "/srv/ftp/share/archive/stats/new/ECB/Train.de-en.en",
                    "Vrain": "/srv/ftp/share/archive/stats/new/ECB/Valid.de-en.en"}
            }, "cs-en": {
                "cs": {
                    "Qrignal": "/srv/ftp/share/archive/stats/orig/ECB.cs-en.cs",
                    "Valid":  "/srv/ftp/share/archive/stats/new/ECB/Train.cs-en.cs",
                    "Train": "/srv/ftp/share/archive/stats/new/ECB/Valid.cs-en.cs"
                }, "en": {
                    "Qrignal": "/srv/ftp/share/archive/stats/orig/ECB.cs-en.en",
                    "Valid":  "/srv/ftp/share/archive/stats/new/ECB/Train.cs-en.en",
                    "Train": "/srv/ftp/share/archive/stats/new/ECB/Valid.cs-en.en"}}
    }, "EMEA": {
        "de-en": {
            "de": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/EMEA.de-en.de",
                "Valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.de-en.de",
                "Train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.de-en.de" 
            }, "en": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/EMEA.de-en.en",
                "Valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.de-en.en",
                "Train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.de-en.en"}
        }, "cs-en": {
            "cs": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/EMEA.cs-en.cs",
                "Valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.cs-en.cs",
                "Train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.cs-en.cs"
            }, "en": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/EMEA.cs-en.en",
                "Valid":  "/srv/ftp/share/archive/stats/new/EMEA/Train.cs-en.en",
                "Train": "/srv/ftp/share/archive/stats/new/EMEA/Valid.cs-en.en"}}
    }, "Europarl": {
        "de-en": {
            "de": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/Europarl.de-en.de",
                "Valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.de-en.de",
                "Train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.de-en.de" 
            }, "en": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/Europarl.de-en.en",
                "Valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.de-en.en",
                "Train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.de-en.en"}
        }, "cs-en": {
            "cs": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/Europarl.cs-en.cs",
                "Valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.cs-en.cs",
                "Train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.cs-en.cs"
            }, "en": {
                "Qrignal": "/srv/ftp/share/archive/stats/orig/Europarl.cs-en.en",
                "Valid":  "/srv/ftp/share/archive/stats/new/Europarl/Train.cs-en.en",
                "Train": "/srv/ftp/share/archive/stats/new/Europarl/Valid.cs-en.en"}}
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
        boxplots = []
        for corpus, pairs in corpora.items():
            for pair, locales in pairs.items():
                for locale, files in locales.items():
                    axis = plt.subplot(len(corpora), len(locales) * 2, plot_index)
                    axis.set_ylim(0, 20 if metric == "Word Length" else 75)
                    plot_index += 1
                    plt.title(f"{corpus}: {pair}.{locale}")
                    data = []
                    for name, path in files.items():
                        if metric == "Word Length":
                            data.append([len(word) for line in open(path) for word in line.split()])
                        elif metric == "Number of Words per Sentence":
                            data.append([len(line.split()) for line in open(path)])
                    boxplots.append(axis.boxplot(
                            data, labels=[name[0] for name in files.keys()],
                            showfliers=False,
                            positions=range(1, len(data)*2, 2),
                            patch_artist=True))
#        fig.legend( [boxplots[0]["boxes"][0], boxplots[1]["boxes"][0], boxplots[2]["boxes"][0]], 
#                    ["Original Data"        , "Validation Set"       , "Trainings Set"])
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(f"{IMAGE_DIR}/corpus_stats-{metric.replace(' ','_')}.png", bbox_inches="tight", dpi=400)
        plt.clf()

def plot_trainings_curve(files=EXAMPLE_RUNS["training"]):
    """Plots a trainings curve for the given runs.
    !!!Currently broken and output disabled!!!
    """
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
        #plt.savefig(f"{IMAGE_DIR}/trainings_curve-{name}.png", bbox_inches="tight", dpi=200)
        plt.clf()

def plot_hyperparameter_optim(files=EXAMPLE_RUNS["hyper_opt"], metric="bleu"):
    """Plots a comparison of the valid score and another metric (bleu by default)
    !!!Currently broken and output disabled!!!
    """
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
                        "score":[float(point.get(metric, 0)) * (1 if metric in ["bleu", "bleu_lc"] else 100) for point in run["scores"]],
                        }
                if i == 0:
                    plt.scatter(data["score-steps"], data["score"], marker="^", label=f"{metric}-Score")
                else:
                    plt.scatter(data["score-steps"], data["score"], 5, marker="o")
            axis.legend()

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
#        plt.savefig(f"{IMAGE_DIR}/optim_comparison-{group.replace(' ','_')}.png", bbox_inches="tight", dpi=200)
    plt.clf()

def plot_side_constraint_comparison(files=EXAMPLE_RUNS["side_constraint"], metric="bleu", name=None):
    fig = plt.figure()
    fig.suptitle(f"Performance grouped by Domain")
    plot_index = 1
    for pair, data_sets in files.items():
        results = {"labels": [], "Tagged": [], "Clean": []}

        for domain, groups in data_sets.items():
            logs = parse([f for f in groups.values()])
            scores = load_scores(
                    {corpus: [run["params"] for run in logs[corpus]["train"]] for corpus in logs},
                    metric, domain)
            if scores:
                results["labels"].append(domain)
            for corpus in scores:
                group = corpus.split("-")[0]
                best_run = reduce(
                        lambda x, y:
                        x if
                            x["scores"].get(domain, {}).get(metric, {"score": 0})["score"] >
                            y["scores"].get(domain, {}).get(metric, {"score": 0})["score"]
                        else y,
                    scores[corpus])
                results[group].append(
                        best_run["scores"].get(domain,{}).get(metric, {"score": 0})["score"] *
                        (1 if metric in ["valid", "train", "bleu", "bleu_lc"] else 100))

        # Settings for the actual bars
        # stolen from https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html
        axis = plt.subplot(len(files), 1, plot_index)

        x_positions = range(len(results["labels"]))

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.spines['bottom'].set_position('zero')
        axis.set_ylabel(f"{metric}-Score")
        axis.set_xlabel("Domains")
        axis.set_title(f"Performance for {pair}")
        axis.set_ylim(0, 100)
        
        width = 0.35

        axis.set_xticks(x_positions)
        axis.set_xticklabels(results["labels"])

        # build bars
        axis.bar([x - width/2 for x in x_positions], results["Clean"], width, label="Clean", edgecolor="black")
        axis.bar([x + width/2 for x in x_positions], results["Tagged"], width, label="Tagged", edgecolor="black")

        for i, _ in enumerate(results["labels"]):
            axis.annotate("{0:.2f}".format(results["Clean"][i]), xy=(x_positions[i] - width/2, results["Clean"][i]+1),
                    xytext=(0,3), textcoords="offset points", ha='center')
            axis.annotate("{0:.2f}".format(results["Tagged"][i]), xy=(x_positions[i] + width/2, results["Tagged"][i]+1),
                    xytext=(0,3), textcoords="offset points", ha='center')

        plot_index += 1
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.legend(["Clean", "Tagged"])
    plt.savefig(
            f"{IMAGE_DIR}/{name}" if name else f"{IMAGE_DIR}/absolute-performace-comparison.png",
            bbox_inches="tight", dpi=200)
    fig.clf()

def plot_language_comparison(files=EXAMPLE_RUNS["side_constraint"], metrics=["train", "valid", "bleu"], name=None):
    results = {}
    for pair, data_sets in files.items():
        results[pair] = {}
        for metric in metrics:
            results[pair][metric] = {"labels": [], "Tagged": [], "Clean": []}

            for domain, groups in data_sets.items():
                logs = parse([f for f in groups.values()])
                scores = load_scores({corpus: [run["params"] for run in logs[corpus]["train"]] for corpus in logs}, metric, domain)
                if scores:
                    results[pair][metric]["labels"].append(domain)
                for corpus in scores:
                    group = corpus.split("-")[0]
                    best_run = reduce(
                            lambda x, y:
                            x if
                                x["scores"].get(domain, {}).get(metric, {"score": 0})["score"] >
                                y["scores"].get(domain, {}).get(metric, {"score": 0})["score"]
                            else y,
                        scores[corpus])
                    results[pair][metric][group].append(best_run["scores"].get(domain, {}).get(metric, {"score": 0})["score"])

            results[pair][metric]["Delta"] = [
                    ((results[pair][metric]["Tagged"][i] - results[pair][metric]["Clean"][i]) / results[pair][metric]["Clean"][i]) * 100 
                    for i in range(len(results[pair][metric]["labels"]))]

    # Settings for the actual bars
    # stolen from https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html
    fig = plt.figure()
    fig.suptitle(f"Score Change between Language Pairs")
    width = 0.35

    for pair in files:
        plot_index = 1
        for metric in metrics:
            axis = plt.subplot(len(metrics), 1, plot_index)
            axis.set_ylabel(f"$\\Delta$ {metric} in %")

            if pair == "de-en":
                x_positions = range(len(results[pair][metric]["labels"]))
                axis.set_xticklabels(results[pair][metric]["labels"])
                axis.set_xticks(x_positions)
                axis.spines['bottom'].set_position('zero')
                axis.spines['right'].set_visible(False)
                axis.spines['top'].set_visible(False)
                axis.xaxis.tick_top()

            # build bars
            axis.bar(
                    [x + (width/2 * (-1 if pair == "de-en" else 1)) for x in x_positions],
                    results[pair][metric]["Delta"],
                    width, edgecolor="black",
                 #   hatch="" if pair == "de-en" else "o",
                    label=pair)

            for i, _ in enumerate(results[pair][metric]["labels"]):
                axis.annotate(
                        "{0:.2f}".format(results[pair][metric]["Delta"][i]),
                        xy=(x_positions[i] + (width/2 * (-1 if pair == "de-en" else 1)), results[pair][metric]["Delta"][i]),
                        xytext=(0, -1 if results[pair][metric]["Delta"][i] < 0 else 1),
                        textcoords="offset points",
                        ha="center", va = "top" if results[pair][metric]["Delta"][i] < 0 else "bottom")
            plot_index += 1
#            axis.legend(loc="upper right")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.legend(files.keys(), loc="lower right")
    plt.savefig(f"{IMAGE_DIR}/{name}" if name else f"{IMAGE_DIR}/language-comparison.png", bbox_inches="tight", dpi=200)
    fig.clf()
