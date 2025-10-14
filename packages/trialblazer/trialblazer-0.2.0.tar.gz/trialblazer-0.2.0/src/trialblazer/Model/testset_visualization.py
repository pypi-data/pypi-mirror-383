import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import cm


def plot_score_distribution_with_significance(data, p_values) -> None:
    custom_palette = {
        "Benign compounds\nTraining set": "#8ecae6",
        "Toxic compounds\nTraining set": "#fb8500",
        "Benign compounds\nTest set": "orangered",
    }
    plt.figure(figsize=(6, 6))
    
    alphas = [0.8, 0.8, 1] 
    for i, (cat, alpha) in enumerate(zip(data["Category"].unique(), alphas)):
        sns.violinplot(
            data=data[data["Category"]==cat],
            x="Category", 
            y="Value",
            hue="Category",
            legend=False,
            inner="quartile", 
            alpha=alpha,
            palette={cat: custom_palette[cat]}
        )
    y_max = data["Value"].max() + 0.5
    step = 5
    for i, ((cat1, cat2), p) in enumerate(p_values.items()):
        x1, x2 = list(data["Category"].unique()).index(cat1), list(data["Category"].unique()).index(cat2)
        y = y_max + ((i + 1) * step)
        plt.plot([x1, x1, x2, x2], [y, y + 1, y + 1, y], lw=1.5, color="black")
        p_text = f"p = {p:.2e}"
        plt.text((x1 + x2) / 2, y + 2, p_text, ha="center", fontsize=11, fontweight="bold")

    plt.ylim(-15, 70)
    plt.xlabel("Category", labelpad=10)
    plt.ylabel("PrOCTOR Score")
    plt.show()

def plot_correlation(predict_result_toxic, predict_result_benign) -> None:
    plt.figure(figsize=(10, 6))
    all_logP = predict_result_toxic["logP"].tolist() + predict_result_benign["logP"].tolist()
    all_scores = predict_result_toxic["PrOCTOR_score"].tolist() + predict_result_benign["PrOCTOR_score"].tolist()

    correlation_logP = np.corrcoef(all_logP, all_scores)[0, 1]

    scatter = plt.scatter(predict_result_toxic["mw"], predict_result_toxic["PrOCTOR_score"],
                        c=predict_result_toxic["logP"], cmap="plasma", alpha=0.9)
    plt.scatter(predict_result_benign["mw"], predict_result_benign["PrOCTOR_score"],
                c=predict_result_benign["logP"], cmap="plasma", alpha=0.9)

    cbar = plt.colorbar(scatter)
    cbar.set_label("logP")

    all_mw = predict_result_toxic["mw"].tolist() + predict_result_benign["mw"].tolist()
    correlation_mw = np.corrcoef(all_mw, all_scores)[0, 1]

    decision_threshold = 0.15
    prediction_threshold = np.log2((1 - decision_threshold) / decision_threshold)
    plt.axhline(y=prediction_threshold, color="navy", linestyle="--", linewidth=1.5, label="Prediction threshold")

    plt.text(633, 1.8, f"Threshold = {prediction_threshold:.2f}", fontsize=10, color="black")
    plt.text(140, 17.3, f"r (MW) = {correlation_mw:.2f}", fontsize=10, color="black")
    plt.text(140, 16.3, f"r (logP) = {correlation_logP:.2f}", fontsize=10, color="black")

    plt.xlabel("Molecular Weight (mw)")
    plt.ylabel("PrOCTOR Score")
    plt.legend()
    plt.grid(True)
    plt.show()

def SuspectedAdverseDrugEvents_count_for_eachdrug(prediction_combine, adverse_drug_reactions) -> None:
    num_categories = len(adverse_drug_reactions)
    color_map = cm.get_cmap("tab20b", num_categories)
    colors = [mcolors.rgb2hex(color_map(i)) for i in range(num_categories)]

    bar_width = 0.8
    gap_between_drugs = 25

    x_indexes = np.arange(len(prediction_combine["Drugs"])) * (1 + gap_between_drugs)

    plt.figure(figsize=(30, 10))
    for i, (column, color) in enumerate(zip(prediction_combine[adverse_drug_reactions], colors)):
        plt.bar(x_indexes + i * bar_width, prediction_combine[column], width=bar_width,
                label=column, color=color)

    xtick_positions = x_indexes + bar_width * (num_categories - 1) / 2
    plt.xticks(ticks=xtick_positions, labels=prediction_combine["Drugs"],rotation=45, ha="right", fontsize=8)

    plt.xlabel("Drug", fontsize=10)
    plt.ylabel("Number of adverse drug reaction reports", fontsize=10)

    mid_index = len(prediction_combine["Drugs"]) // 2
    separation_x = (x_indexes[mid_index - 1] + x_indexes[mid_index + 1]) / 2
    plt.axvline(x=separation_x, color="navy", linestyle="--", linewidth=2)

    plt.text(separation_x - 10, plt.ylim()[1] * 0.9, "Benign", fontsize=16,fontweight="bold", ha="right", color="#8ea5c8")
    plt.text(separation_x + 10, plt.ylim()[1] * 0.9, "Toxic", fontsize=16,fontweight="bold", ha="left", color="#a17db4")
    plt.legend(title="Severity", loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=5)
    plt.tight_layout()
    plt.show()

def SuspectedAdverseDrugEvents_count(pre_benign, pre_toxic, list_of_adverse_reaction) -> None:
    benign_not_serious_list_array, benign_serious_list_array = process_adverse_reactions(pre_benign, list_of_adverse_reaction)
    toxic_not_serious_list_array, toxic_serious_list_array = process_adverse_reactions(pre_toxic, list_of_adverse_reaction)
    
    benign_category_totals = benign_not_serious_list_array.sum(axis=1) + benign_serious_list_array.sum(axis=1)
    toxic_category_totals = toxic_not_serious_list_array.sum(axis=1) + toxic_serious_list_array.sum(axis=1)
    
    toxic_higher_count = np.sum(toxic_category_totals > benign_category_totals)
    percent_toxic_higher = float(toxic_higher_count / len(list_of_adverse_reaction) * 100)
    
    category_counts_benign = {
        "Non Serious": benign_not_serious_list_array.sum(axis=1),
        "Serious": benign_serious_list_array.sum(axis=1),
    }
    category_counts_toxic = {
        "Non Serious": toxic_not_serious_list_array.sum(axis=1),
        "Serious": toxic_serious_list_array.sum(axis=1),
    }
    
    print("Category-wise totals and comparison:")
    for i, category in enumerate(list_of_adverse_reaction):
        print(f"\n{category}:")
        print(f"Predicted Benign: Total={benign_category_totals[i]}")
        print(f"  Non-Serious: {benign_not_serious_list_array[i].sum()}")
        print(f"  Serious: {benign_serious_list_array[i].sum()}")
        print(f"Predicted Toxic: Total={toxic_category_totals[i]}")
        print(f"  Non-Serious: {toxic_not_serious_list_array[i].sum()}")
        print(f"  Serious: {toxic_serious_list_array[i].sum()}")
        if toxic_category_totals[i] > benign_category_totals[i]:
            print("*** Toxic count higher than Benign ***")
    
    print(f"\nOut of {len(list_of_adverse_reaction)} categories, {toxic_higher_count} ({percent_toxic_higher:.1f}%) have higher counts in predicted toxic drugs")
    
    width = 0.4
    base_color_benign = "#8ecae6"
    base_color_toxic = "#fb8500"
    alphas = [0.6,0.8]
    offset = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    bottom_benign = np.zeros(len(list_of_adverse_reaction))
    bottom_toxic = np.zeros(len(list_of_adverse_reaction))
    x_positions = np.arange(len(list_of_adverse_reaction)) * 1.2

    for i, (label, counts) in enumerate(category_counts_benign.items()):
        ax.bar(
            [x - offset for x in x_positions], counts, width=width, label=f"Predicted benign: {label}", color=base_color_benign,
            alpha=alphas[i], edgecolor="black", linewidth=1, bottom=bottom_benign,
        )
        bottom_benign += counts

    for i, (label, counts) in enumerate(category_counts_toxic.items()):
        ax.bar(
            [x + offset for x in x_positions], counts, width=width, label=f"Predicted toxic: {label}",
            color=base_color_toxic, alpha=alphas[i], edgecolor="black", linewidth=1, bottom=bottom_toxic,
        )
        bottom_toxic += counts

    ax.set_xticks(x_positions)
    ax.set_xticklabels(list_of_adverse_reaction, rotation=45, ha="right", fontsize=10)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_xlabel("Adverse drug reaction", fontsize=12)
    ax.legend()
    plt.show()

def SuspectedAdverseDrugEvents_Totalcount_for_eachdrug(prediction_combine) -> None:
    x_indexes = np.arange(len(prediction_combine["Drugs"]))
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.bar(x_indexes, prediction_combine["Total"], color="orangered")
    mid_index = len(prediction_combine["Drugs"]) // 2
    separation_x = (x_indexes[mid_index - 1] + x_indexes[mid_index]) / 2
    plt.axvline(x=separation_x, color="navy", linestyle="--", linewidth=2)
    plt.text(separation_x - 3, plt.ylim()[1] * 0.9, "Benign", fontsize=10, fontweight="bold",ha="right", color="#8ea5c8")
    plt.text(separation_x + 3, plt.ylim()[1] * 0.9, "Toxic", fontsize=10, fontweight="bold",ha="left", color="#a17db4")
    plt.xticks(ticks=x_indexes, labels=prediction_combine["Drugs"], rotation=45, ha="right",fontsize=8)
    plt.xlabel("Drug")
    plt.ylabel("Total count of adverse reactions")
    plt.tight_layout()
    plt.show()

def process_adverse_reactions(prediction, list_of_adverse_reaction):
    not_serious_list, serious_list = [], []
    for reaction in list_of_adverse_reaction:
        not_serious_list.append(prediction.loc[prediction["Seriousness"] == "Non Serious", reaction].tolist())
        serious_list.append(prediction.loc[prediction["Seriousness"] == "Serious", reaction].tolist())
    not_serious_list_array = np.array(not_serious_list)
    serious_list_array = np.array(serious_list)
    return not_serious_list_array, serious_list_array