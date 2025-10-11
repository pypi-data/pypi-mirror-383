# ----------- Activity Selection Problem -----------

def Activity_Selection(intervals):
    # Sort activities based on their end times
    sorted_intervals = sorted(intervals, key=lambda x: x[1])
    selected_activities = []
    last_end = float('-inf')
    for start, end in sorted_intervals:
        if start >= last_end:
            selected_activities.append((start, end))
            last_end = end
    return selected_activities