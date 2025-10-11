def Job_Scheduling_Min_Lateness(jobs):

    sorted_jobs = sorted(jobs, key=lambda x: x[2])  # x[2] = deadline
    current_time = 0
    max_lateness = 0
    schedule = []

    for job_id, p_time, deadline in sorted_jobs:
        current_time += p_time
        lateness = max(0, current_time - deadline)
        max_lateness = max(max_lateness, lateness)
        schedule.append(job_id)

    return schedule, max_lateness
