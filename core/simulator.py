from schedulers.fcfs import fcfs_schedule
from schedulers.sjf import sjf_schedule
from schedulers.srtf import srtf_schedule
from schedulers.priority import (
    priority_non_preemptive_schedule,
    priority_preemptive_schedule
)
from schedulers.round_robin import round_robin_schedule
from schedulers.mlfq import mlfq_schedule
from core.metrics import calculate_metrics


class Simulator:
    def __init__(self):
        self.processes = []
        self.gantt_chart = []
        self.metrics = {}

    def add_process(self, process):
        self.processes.append(process)

    def clear_processes(self):
        self.processes.clear()
        self.gantt_chart.clear()
        self.metrics.clear()

    def run(self, algorithm="FCFS", time_quantum=2):
        if algorithm == "FCFS":
            self.gantt_chart, completed_processes = fcfs_schedule(self.processes)

        elif algorithm == "SJF":
            self.gantt_chart, completed_processes = sjf_schedule(self.processes)

        elif algorithm == "SRTF":
            self.gantt_chart, completed_processes = srtf_schedule(self.processes)

        elif algorithm == "Priority Non-Preemptive":
            self.gantt_chart, completed_processes = priority_non_preemptive_schedule(self.processes)

        elif algorithm == "Priority Preemptive":
            self.gantt_chart, completed_processes = priority_preemptive_schedule(self.processes)

        elif algorithm == "Round Robin":
            self.gantt_chart, completed_processes = round_robin_schedule(
                self.processes,
                time_quantum=time_quantum
            )

        elif algorithm == "MLFQ":
            self.gantt_chart, completed_processes = mlfq_schedule(
                self.processes,
                queues_count=3,
                time_quantums=[2, 4, 8]
            )

        else:
            return [], {}

        self.metrics = calculate_metrics(completed_processes, self.gantt_chart)

        return self.gantt_chart, self.metrics