def reset_processes(processes):
    for p in processes:
        p.remaining_time = p.burst_time
        p.start_time = None
        p.completion_time = None
        p.waiting_time = 0
        p.turnaround_time = 0
        p.response_time = None
        p.status = "New"


def fcfs_schedule(processes):
    reset_processes(processes)

    processes = sorted(processes, key=lambda p: p.arrival_time)

    current_time = 0
    gantt_chart = []

    for process in processes:
        if current_time < process.arrival_time:
            gantt_chart.append({
                "pid": "IDLE",
                "start": current_time,
                "end": process.arrival_time
            })
            current_time = process.arrival_time

        process.start_time = current_time
        process.response_time = current_time - process.arrival_time
        process.status = "Running"

        gantt_chart.append({
            "pid": process.pid,
            "start": current_time,
            "end": current_time + process.burst_time
        })

        current_time += process.burst_time

        process.remaining_time = 0
        process.completion_time = current_time
        process.status = "Completed"

    return gantt_chart, processes