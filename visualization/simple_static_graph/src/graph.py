import networkx as nx
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt 
import random
from sklearn.model_selection import train_test_split


def draw(img_name):
    g1 = nx.DiGraph()
    g1.add_edge('a', 2)
    g1.add_edge('a', 3)
    g1.add_edge(2, 4)
    g1.add_edge(3, 4)

    node_list = ['a', 2, 3, 4]
    node_list_a, node_list_b = train_test_split(node_list, test_size=0.5, shuffle=True)
    node_list_b, node_list_c = train_test_split(node_list_b, test_size=0.5, shuffle=True)
    print(node_list_a, node_list_b, node_list_c)
    #pos = nx.spring_layout(g1)
    pos = {
        'a':[2, 4],
        2:[1, 3],
        3:[3, 3],
        4:[2, 2],
    }
    plt.tight_layout()
    nx.draw_networkx(g1, pos, nodelist=node_list_a, node_color="#FF0000", arrows=True)
    nx.draw_networkx(g1, pos, nodelist=node_list_b, node_color="#FFFF00", arrows=True)
    nx.draw_networkx(g1, pos, nodelist=node_list_c, node_color="#00FFFF", arrows=True)
    plt.savefig(img_name, format="PNG")
    plt.clf()
    print("DONE")