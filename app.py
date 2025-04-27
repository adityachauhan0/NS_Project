# app.py  ──────────────────────────────────────────────────────────
"""
Streamlit dashboard for the Noordin-Top criminal network.
Place `streamlit_artifacts.zip` in the same directory and run:

    pip install streamlit networkx pandas numpy matplotlib pyvis
    streamlit run app.py
"""
import zipfile, pathlib, pickle, shutil
import streamlit as st
import networkx as nx
import pandas as pd
import pymnet
from pyvis.network import Network

# -----------------------------------------------------------------
# 0.  Unzip artefacts (one-time) into .cache/
# -----------------------------------------------------------------
ART_ZIP = pathlib.Path("streamlit_artifacts.zip")
CACHE   = pathlib.Path(".cache")
if not CACHE.exists():
    CACHE.mkdir()
if ART_ZIP.exists() and not any(CACHE.iterdir()):
    with zipfile.ZipFile(ART_ZIP) as zf:
        zf.extractall(CACHE)
        st.sidebar.success("Artefacts extracted to .cache/")

# -----------------------------------------------------------------
# 1.  Load artefacts
# -----------------------------------------------------------------
def load_pickle(name):
    with open(CACHE / name, "rb") as f:
        return pickle.load(f)

@st.cache_resource
def load_graphs():
    G  = load_pickle("static_graph.pkl")
    mg = load_pickle("multiplex_graph.pkl")      # not used but available
    centr = pd.read_csv(CACHE / "centrality.csv")
    return G, centr

G, centr_df = load_graphs()

# -----------------------------------------------------------------
# 2.  Sidebar controls
# -----------------------------------------------------------------
st.sidebar.title("Controls")

layers = sorted({d["relation"] for _,_,d in G.edges(data=True)})
layer_choice = st.sidebar.selectbox("Layer", ["all"] + layers)

max_k = min(30, G.number_of_nodes())
k_remove = st.sidebar.slider("Remove top-k betweenness nodes", 0, max_k, 0)

# -----------------------------------------------------------------
# 3.  Filter & knock-out graph
# -----------------------------------------------------------------
H = G.copy()
if layer_choice != "all":
    H.remove_edges_from(
        [(u,v) for u,v,d in H.edges(data=True) if d["relation"]!=layer_choice]
    )

if k_remove:
    btwn = nx.betweenness_centrality(H)
    victims = [n for n,_ in sorted(btwn.items(),
                                   key=lambda x:x[1], reverse=True)[:k_remove]]
    H.remove_nodes_from(victims)

largest_cc = len(max(nx.connected_components(H), key=len))
st.sidebar.metric("Largest component", f"{largest_cc} nodes")

# -----------------------------------------------------------------
# 4.  PyVis interactive view
# -----------------------------------------------------------------
st.title("Noordin-Top Criminal Network Explorer")

color_map = {
    "business":"red", "communications":"cyan", "o_logistics":"orange",
    "o_meetings":"lightgreen", "o_operations":"yellow", "o_training":"pink",
    "t_classmates":"purple", "t_friendship":"blue", "t_kinship":"gold",
    "t_soulmates":"white"
}

net = Network(height="650px", width="100%", bgcolor="#222", font_color="white")
for n in H.nodes():
    net.add_node(n, label=str(n), size=8)

for u,v,d in H.edges(data=True):
    col = color_map.get(d["relation"], "gray")
    net.add_edge(u, v, color=col)

net.repulsion(node_distance=120, central_gravity=0.15)
html = net.generate_html()
st.components.v1.html(html, height=680, scrolling=True)

# -----------------------------------------------------------------
# 5.  Centrality table for current graph
# -----------------------------------------------------------------
st.subheader("Top-20 eigenvector centrality (current view)")
top20 = (centr_df[centr_df["node"].isin(H.nodes())]
         .sort_values("eigenvector", ascending=False)
         .head(20)
         .reset_index(drop=True))
st.dataframe(top20.style.format({"eigenvector":"{:.4f}"}), height=300)

st.caption("Layer colours: " + ", ".join(f"{k} = {v}"
                                         for k,v in color_map.items()))
