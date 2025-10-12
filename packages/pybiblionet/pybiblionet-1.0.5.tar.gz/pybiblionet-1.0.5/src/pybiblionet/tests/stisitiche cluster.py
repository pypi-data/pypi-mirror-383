import pandas as pd

# Carica il CSV
df = pd.read_csv("cluster_and_fields_citation.csv")

# Conta quanti autori per ciascun cluster
cluster_sizes = df['cluster'].value_counts()

# Statistiche di base
num_clusters = cluster_sizes.shape[0]
total_authors = cluster_sizes.sum()
mean_size = cluster_sizes.mean()
median_size = cluster_sizes.median()
min_size = cluster_sizes.min()
max_size = cluster_sizes.max()

# Copertura cumulativa per capire l’80%
sorted_sizes = cluster_sizes.sort_values(ascending=False)
cumulative = sorted_sizes.cumsum() / total_authors
num_clusters_80 = (cumulative <= 0.8).sum() + 1  # +1 per includere quello che supera 80%

# Quota dei 5 cluster più grandi
top5_share = sorted_sizes.head(5).sum() / total_authors * 100

# Stampa report
print("=== Analisi distribuzione cluster ===")
print(f"Numero totale di cluster: {num_clusters}")
print(f"Numero totale di autori: {total_authors}")
print(f"Dimensione media cluster: {mean_size:.2f}")
print(f"Dimensione mediana cluster: {median_size}")
print(f"Minima dimensione cluster: {min_size}")
print(f"Massima dimensione cluster: {max_size}")
print()
print(f"Cluster necessari per coprire l'80% degli autori: {num_clusters_80} ({num_clusters_80/num_clusters*100:.1f}% dei cluster)")
print(f"Quota di autori nei 5 cluster più grandi: {top5_share:.2f}%")
print()
print("=== Alcuni esempi di dimensioni ===")
print("Top 5 cluster:", sorted_sizes.head(5).tolist())
print("Bottom 5 cluster:", sorted_sizes.tail(5).tolist())
