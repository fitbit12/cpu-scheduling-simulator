from collections import deque


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


def round_robin_schedule(processes, time_quantum=2):
    reset_processes(processes)

    processes = sorted(processes, key=lambda p: p.arrival_time)

    current_time = 0
    completed = 0
    n = len(processes)
    gantt_chart = []

    ready_queue = deque()
    arrived = set()

    while completed < n:
        for p in processes:
            if p.arrival_time <= current_time and p.pid not in arrived and p.remaining_time > 0:
                ready_queue.append(p)
                arrived.add(p.pid)
                p.status = "Ready"

        if not ready_queue:
            add_to_gantt(gantt_chart, "IDLE", current_time, current_time + 1)
            current_time += 1
            continue

        selected_process = ready_queue.popleft()

        if selected_process.start_time is None:
            selected_process.start_time = current_time
            selected_process.response_time = current_time - selected_process.arrival_time

        selected_process.status = "Running"

        execution_time = min(time_quantum, selected_process.remaining_time)

        for _ in range(execution_time):
            add_to_gantt(gantt_chart, selected_process.pid, current_time, current_time + 1)

            selected_process.remaining_time -= 1
            current_time += 1

            for p in processes:
                if p.arrival_time <= current_time and p.pid not in arrived and p.remaining_time > 0:
                    ready_queue.append(p)
                    arrived.add(p.pid)
                    p.status = "Ready"

            if selected_process.remaining_time == 0:
                break

        if selected_process.remaining_time == 0:
            selected_process.completion_time = current_time
            selected_process.status = "Completed"
            completed += 1
        else:
            selected_process.status = "Ready"
            ready_queue.append(selected_process)

    return gantt_chart, processes