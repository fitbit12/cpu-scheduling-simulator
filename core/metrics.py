def calculate_metrics(processes, gantt_chart):
    completed = [p for p in processes if p.completion_time is not None]

    if not completed:
        return {}

    total_waiting = 0
    total_turnaround = 0
    total_response = 0

    for p in completed:
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time

        if p.response_time is None:
            p.response_time = 0

        total_waiting += p.waiting_time
        total_turnaround += p.turnaround_time
        total_response += p.response_time

    total_time = gantt_chart[-1]["end"] if gantt_chart else 0
    busy_time = sum(item["end"] - item["start"] for item in gantt_chart if item["pid"] != "IDLE")

    cpu_utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
    throughput = len(completed) / total_time if total_time > 0 else 0

    return {
        "Average Waiting Time": round(total_waiting / len(completed), 2),
        "Average Turnaround Time": round(total_turnaround / len(completed), 2),
        "Average Response Time": round(total_response / len(completed), 2),
        "CPU Utilization": round(cpu_utilization, 2),
        "Throughput": round(throughput, 2),
        "Completion Order": [p.pid for p in sorted(completed, key=lambda x: x.completion_time)]
    }