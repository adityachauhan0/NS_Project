import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your centrality data
df = pd.read_csv(r"C:\Documentss\Github\NS_Project\streamlit_artifacts\centrality.csv")

# Remove placeholder node
df = df[df["node"] != '0']

# Normalize for better spread
df["degree_norm"] = df["degree"] / df["degree"].max()
df["betweenness_norm"] = df["betweenness"] / df["betweenness"].max()

# Set up seaborn plot
plt.figure(figsize=(10, 6))
sns.set(style="whitegrid")

# Plot with color and annotation
ax = sns.scatterplot(
    data=df,
    x="degree_norm",
    y="betweenness_norm",
    s=100,
    color='steelblue',
    edgecolor="black"
)

# Annotate top 5 influential nodes
top_nodes = df.sort_values("betweenness", ascending=False).head(5)
for _, row in top_nodes.iterrows():
    plt.text(row["degree_norm"] + 0.01, row["betweenness_norm"] + 0.01,
             f"{row['node']}", fontsize=9, weight='bold', color='darkred')

plt.title("Node Influence: Degree vs Betweenness Centrality")
plt.xlabel("Normalized Degree Centrality")
plt.ylabel("Normalized Betweenness Centrality")
plt.tight_layout()

# Save the figure
plt.savefig("degree_betweenness_enhanced.png")
plt.show()
