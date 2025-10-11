# For distance calculations, define a manual Euclidean distance
def euclidean_distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5


# ----------- Closest Pair of Points -----------

def Closest_Pair_Of_Points(points):
    """Closest Pair of Points (Divide and Conquer)"""
    def distance(p1, p2):
        return euclidean_distance(p1, p2)

    def recursive(points_sorted_x, points_sorted_y):
        n = len(points_sorted_x)
        if n <= 3:
            min_dist = float('inf')
            pair = None
            for i in range(n):
                for j in range(i + 1, n):
                    dist = distance(points_sorted_x[i], points_sorted_x[j])
                    if dist < min_dist:
                        min_dist = dist
                        pair = (points_sorted_x[i], points_sorted_x[j])
            return min_dist, pair
        mid = n // 2
        mid_point = points_sorted_x[mid]

        left_x = points_sorted_x[:mid]
        right_x = points_sorted_x[mid:]

        left_y = list(filter(lambda p: p[0] <= mid_point[0], points_sorted_y))
        right_y = list(filter(lambda p: p[0] > mid_point[0], points_sorted_y))

        dl, pair_left = recursive(left_x, left_y)
        dr, pair_right = recursive(right_x, right_y)

        d = dl if dl < dr else dr
        min_pair = pair_left if dl < dr else pair_right

        strip = [p for p in points_sorted_y if abs(p[0] - mid_point[0]) < d]
        for i in range(len(strip)):
            for j in range(i + 1, min(i + 7, len(strip))):
                dist = distance(strip[i], strip[j])
                if dist < d:
                    d = dist
                    min_pair = (strip[i], strip[j])
        return d, min_pair

    points_sorted_x = sorted(points, key=lambda p: p[0])
    points_sorted_y = sorted(points, key=lambda p: p[1])
    _, pair = recursive(points_sorted_x, points_sorted_y)
    return pair