    # ----------- Kruskal's Algorithm -----------

def Kruskal_Mst(edges, num_nodes):
    parent = list(range(num_nodes))
    rank = [0] * num_nodes

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        ru, rv = find(u), find(v)
        if ru != rv:
            if rank[ru] < rank[rv]:
                parent[ru] = rv
            elif rank[rv] < rank[ru]:
                parent[rv] = ru
            else:
                parent[rv] = ru
                rank[ru] += 1
            return True
        return False

    mst = []
    # Sort edges based on weight (assumed to be the first element of each edge tuple)
    for weight, u, v in sorted(edges, key=lambda e: e[0]):
        if union(u, v):
            mst.append((u, v, weight))
    return mst