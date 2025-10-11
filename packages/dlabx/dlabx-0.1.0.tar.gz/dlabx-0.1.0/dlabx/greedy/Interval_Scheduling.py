# ----------- Interval Scheduling -----------

def Interval_Scheduling(intervals):
    sorted_intervals = sorted(intervals, key=lambda x: x[1])
    count = 0
    last_end = float('-inf')
    for start, end in sorted_intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count