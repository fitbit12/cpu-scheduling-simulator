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


def mlfq_schedule(processes, queues_count=3, time_quantums=None):
    reset_processes(processes)

    if time_quantums is None:
        time_quantums = [2, 4, 8]

    processes = sorted(processes, key=lambda p: p.arrival_time)

    queues = [deque() for _ in range(queues_count)]

    current_time = 0
    completed = 0
    n = len(processes)
    gantt_chart = []

    arrived = set()

    while completed < n:
        for p in processes:
            if p.arrival_time <= current_time and p.pid not in arrived and p.remaining_time > 0:
                queues[0].append(p)
                arrived.add(p.pid)
                p.status = "Ready"

        selected_process = None
        selected_queue_index = None

        for i in range(queues_count):
            if queues[i]:
                selected_process = queues[i].popleft()
                selected_queue_index = i
                break

        if selected_process is None:
            add_to_gantt(gantt_chart, "IDLE", current_time, current_time + 1)
            current_time += 1
            continue

        if selected_process.start_time is None:
            selected_process.start_time = current_time
            selected_process.response_time = current_time - selected_process.arrival_time

        selected_process.status = "Running"

        quantum = time_quantums[min(selected_queue_index, len(time_quantums) - 1)]
        execution_time = min(quantum, selected_process.remaining_time)

        for _ in range(execution_time):
            add_to_gantt(gantt_chart, selected_process.pid, current_time, current_time + 1)

            selected_process.remaining_time -= 1
            current_time += 1

            for p in processes:
                if p.arrival_time <= current_time and p.pid not in arrived and p.remaining_time > 0:
                    queues[0].append(p)
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

            next_queue_index = min(selected_queue_index + 1, queues_count - 1)
            queues[next_queue_index].append(selected_process)

    return gantt_chart, processes