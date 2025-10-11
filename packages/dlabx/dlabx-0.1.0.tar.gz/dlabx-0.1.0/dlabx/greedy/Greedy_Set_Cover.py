# ----------- Greedy Set Cover -----------

def Greedy_Set_Cover(universe, sets):
    covered = set()
    cover = []
    remaining_sets = sets[:]
    while covered != universe:
        # Select the set that covers the most uncovered elements
        best_set = max(
            remaining_sets,
            key=lambda s: len(s & (universe - covered))
        )
        cover.append(best_set)
        covered |= best_set
        remaining_sets.remove(best_set)
    return cover