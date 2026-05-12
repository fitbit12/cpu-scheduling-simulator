def reset_processes(processes):
    for p in processes:
        p.remaining_time = p.burst_time
        p.start_time = None
        p.completion_time = None
        p.waiting_time = 0
        p.turnaround_time = 0
        p.response_time = None
        p.status = "New"


def add_to_gantt(gantt_chart, pid, start, end):
    if gantt_chart and gantt_chart[-1]["pid"] == pid:
        gantt_chart[-1]["end"] = end
    else:
        gantt_chart.append({
            "pid": pid,
            "start": start,
            "end": end
        })


def srtf_schedule(processes):
    reset_processes(processes)

    current_time = 0
    completed = 0
    n = len(processes)
    gantt_chart = []

    while completed < n:
        ready_queue = [
            p for p in processes
            if p.arrival_time <= current_time and p.remaining_time > 0
        ]

        if not ready_queue:
            add_to_gantt(gantt_chart, "IDLE", current_time, current_time + 1)
            current_time += 1
            continue

        selected_process = min(
            ready_queue,
            key=lambda p: (p.remaining_time, p.arrival_time)
        )

        if selected_process.start_time is None:
            selected_process.start_time = current_time
            selected_process.response_time = current_time - selected_process.arrival_time

        selected_process.status = "Running"

        add_to_gantt(gantt_chart, selected_process.pid, current_time, current_time + 1)

        selected_process.remaining_time -= 1
        current_time += 1

        if selected_process.remaining_time == 0:
            selected_process.completion_time = current_time
            selected_process.status = "Completed"
            completed += 1

    return gantt_chart, processes