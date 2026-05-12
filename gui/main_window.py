from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QFrame, QTextEdit, QMessageBox, QDialog, QHeaderView, QScrollArea
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QIntValidator
from PyQt6.QtCore import Qt

from models.process import Process
from core.simulator import Simulator
from core.adaptive_feedback import generate_feedback


APP_STYLE = """
QMainWindow {
    background-color: #0B1220;
}

QWidget {
    color: #F8FAFC;
    font-family: Segoe UI;
    font-size: 14px;
}

QScrollArea {
    border: none;
    background-color: #0B1220;
}

QFrame {
    background-color: #162033;
    border-radius: 16px;
}

QLabel {
    color: #F8FAFC;
}

QLineEdit, QComboBox {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding-left: 12px;
    padding-right: 12px;
    min-height: 36px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #38BDF8;
}

QComboBox::drop-down {
    width: 28px;
    border: none;
}

QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px;
    font-weight: bold;
    min-height: 38px;
}

QPushButton:hover {
    background-color: #1D4ED8;
}

QPushButton:pressed {
    background-color: #1E40AF;
}

QTableWidget {
    background-color: #0F172A;
    color: white;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 12px;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #2563EB;
    color: white;
}

QHeaderView::section {
    background-color: #1E293B;
    color: #38BDF8;
    padding: 10px;
    border: none;
    font-weight: bold;
}

QTextEdit {
    background-color: #0F172A;
    color: #CBD5E1;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 10px;
}
"""

class GanttChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.gantt_chart = []
        self.process_colors = {}
        self.setMinimumHeight(160)

    def set_gantt_chart(self, gantt_chart):
        self.gantt_chart = gantt_chart
        self.update()

    def get_color(self, pid):
        if pid == "IDLE":
            return QColor("#6B7280")

        colors = [
            "#8B5CF6", "#22D3EE", "#10B981", "#F59E0B",
            "#EF4444", "#EC4899", "#6366F1", "#14B8A6"
        ]

        if pid not in self.process_colors:
            self.process_colors[pid] = QColor(
                colors[len(self.process_colors) % len(colors)]
            )

        return self.process_colors[pid]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1A1B2E"))

        if not self.gantt_chart:
            painter.setPen(QColor("#9CA3AF"))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Gantt Chart will appear here"
            )
            return

        total_time = self.gantt_chart[-1]["end"]
        if total_time == 0:
            return

        left_margin = 35
        right_margin = 35
        top = 40
        height = 55
        width = self.width() - left_margin - right_margin

        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

        for item in self.gantt_chart:
            start = item["start"]
            end = item["end"]
            pid = item["pid"]

            x = left_margin + int((start / total_time) * width)
            block_width = max(35, int(((end - start) / total_time) * width))

            painter.setBrush(self.get_color(pid))
            painter.setPen(QPen(QColor("#111827"), 2))
            painter.drawRoundedRect(x, top, block_width, height, 8, 8)

            painter.setPen(QColor("white"))
            painter.drawText(
                x,
                top,
                block_width,
                height,
                Qt.AlignmentFlag.AlignCenter,
                pid
            )

            painter.setPen(QColor("#D1D5DB"))
            painter.drawText(x, top + height + 25, str(start))

        last_x = left_margin + width
        painter.drawText(last_x - 10, top + height + 25, str(total_time))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CPU Scheduling Simulator")
        self.setGeometry(80, 60, 1400, 850)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(APP_STYLE)

        self.sim = Simulator()
        self.build_ui()

    def build_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(10, 10, 10, 10)

        sidebar = self.create_sidebar()
        content = self.create_content()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, stretch=1)

        self.setCentralWidget(main_widget)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(14)
        layout.setContentsMargins(14, 14, 14, 14)

        title = QLabel("CPU Scheduler")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #A78BFA;")
        layout.addWidget(title)

        subtitle = QLabel("Simulation Dashboard")
        subtitle.setStyleSheet("color: #9CA3AF;")
        layout.addWidget(subtitle)

        layout.addSpacing(18)

        algorithms = [
            "FCFS",
            "SJF",
            "SRTF",
            "Priority Non-Preemptive",
            "Priority Preemptive",
            "Round Robin",
            "MLFQ"
        ]

        for algo in algorithms:
            btn = QPushButton(algo)
            btn.clicked.connect(
                lambda checked, a=algo: self.algorithm_combo.setCurrentText(a)
            )
            layout.addWidget(btn)

        layout.addStretch()

        compare_btn = QPushButton("Compare Algorithms")
        compare_btn.setStyleSheet("background-color: #22D3EE; color: #0F172A;")
        compare_btn.clicked.connect(self.compare_algorithms)
        layout.addWidget(compare_btn)

        return sidebar

    def create_content(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Real-Time Interactive CPU Scheduling Simulator")
        header.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        header.setMinimumHeight(30)
        layout.addWidget(header)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        top_layout.addWidget(self.create_input_card(), stretch=2)
        top_layout.addWidget(self.create_metrics_card(), stretch=1)

        layout.addLayout(top_layout)

        self.gantt_widget = GanttChartWidget()
        gantt_frame = self.wrap_card("Live Gantt Chart", self.gantt_widget)
        gantt_frame.setMinimumHeight(190)
        layout.addWidget(gantt_frame)

        self.process_table = QTableWidget()
        self.process_table.setColumnCount(11)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "Arrival", "Burst", "Remaining", "Priority",
            "Start", "Completion", "Waiting", "Turnaround",
            "Response", "Status"
        ])

        self.process_table.setMinimumHeight(230)
        self.process_table.verticalHeader().setVisible(False)
        self.process_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.process_table.setShowGrid(False)
        self.process_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.process_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        table_frame = self.wrap_card("Process Table", self.process_table)
        table_frame.setMinimumHeight(270)
        layout.addWidget(table_frame)

        self.feedback_box = QTextEdit()
        self.feedback_box.setReadOnly(True)
        self.feedback_box.setMinimumHeight(70)
        self.feedback_box.setText(
            "Adaptive feedback will appear after running simulation."
        )

        feedback_frame = self.wrap_card("Adaptive Feedback", self.feedback_box)
        feedback_frame.setMinimumHeight(115)
        layout.addWidget(feedback_frame)

        scroll.setWidget(content)
        return scroll

    def create_input_card(self):
        frame = QFrame()
        frame.setMinimumHeight(260)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        title = QLabel("Process Configuration")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #22D3EE;")
        layout.addWidget(title)

        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.pid_input = QLineEdit()
        self.pid_input.setPlaceholderText("P1")

        self.arrival_input = QLineEdit()
        self.arrival_input.setText("0")
        self.arrival_input.setValidator(QIntValidator(0, 999))

        self.burst_input = QLineEdit()
        self.burst_input.setText("1")
        self.burst_input.setValidator(QIntValidator(1, 999))

        self.priority_input = QLineEdit()
        self.priority_input.setText("1")
        self.priority_input.setValidator(QIntValidator(1, 99))

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            "FCFS",
            "SJF",
            "SRTF",
            "Priority Non-Preemptive",
            "Priority Preemptive",
            "Round Robin",
            "MLFQ"
        ])

        self.quantum_input = QLineEdit()
        self.quantum_input.setText("2")
        self.quantum_input.setValidator(QIntValidator(1, 50))

        form.addWidget(QLabel("Process ID"), 0, 0)
        form.addWidget(self.pid_input, 0, 1)

        form.addWidget(QLabel("Arrival Time"), 0, 2)
        form.addWidget(self.arrival_input, 0, 3)

        form.addWidget(QLabel("Burst Time"), 1, 0)
        form.addWidget(self.burst_input, 1, 1)

        form.addWidget(QLabel("Priority"), 1, 2)
        form.addWidget(self.priority_input, 1, 3)

        form.addWidget(QLabel("Algorithm"), 2, 0)
        form.addWidget(self.algorithm_combo, 2, 1)

        form.addWidget(QLabel("Time Quantum"), 2, 2)
        form.addWidget(self.quantum_input, 2, 3)

        form.setColumnStretch(1, 2)
        form.setColumnStretch(3, 1)

        layout.addLayout(form)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        add_btn = QPushButton("Add Process")
        add_btn.clicked.connect(self.add_process)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected_process)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)

        run_btn = QPushButton("Run Simulation")
        run_btn.setStyleSheet("background-color: #10B981;")
        run_btn.clicked.connect(self.run_simulation)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(run_btn)

        layout.addLayout(button_layout)

        return frame

    def create_metrics_card(self):
        frame = QFrame()
        frame.setMinimumHeight(260)
        frame.setMinimumWidth(330)

        layout = QVBoxLayout(frame)
        layout.setSpacing(6)
        layout.setContentsMargins(14, 14, 14, 14)

        title = QLabel("Performance Metrics")
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #22D3EE;")
        layout.addWidget(title)

        self.metric_labels = {}

        metric_names = [
            "Average Waiting Time",
            "Average Turnaround Time",
            "Average Response Time",
            "CPU Utilization",
            "Throughput",
            "Completion Order"
        ]

        for name in metric_names:
            label = QLabel(f"{name}: -")
            label.setMinimumHeight(28)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("""
                QLabel {
                    background-color: #111827;
                    border-radius: 10px;
                    padding: 6px 10px;
                    color: #E5E7EB;
                    font-size: 13px;
                }
            """)
            self.metric_labels[name] = label
            layout.addWidget(label)

        layout.addStretch()
        return frame

    def wrap_card(self, title_text, widget):
        frame = QFrame()

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #A78BFA;")

        layout.addWidget(title)
        layout.addWidget(widget)

        return frame

    def add_process(self):
        pid = self.pid_input.text().strip()

        if not pid:
            QMessageBox.warning(self, "Input Error", "Please enter Process ID.")
            return

        for p in self.sim.processes:
            if p.pid == pid:
                QMessageBox.warning(
                    self,
                    "Duplicate Process",
                    "Process ID already exists."
                )
                return

        try:
            arrival = int(self.arrival_input.text())
            burst = int(self.burst_input.text())
            priority = int(self.priority_input.text())
        except ValueError:
            QMessageBox.warning(
                self,
                "Input Error",
                "Arrival, Burst, and Priority must be valid numbers."
            )
            return

        process = Process(pid, arrival, burst, priority)
        self.sim.add_process(process)

        self.refresh_process_table()

        self.pid_input.clear()
        self.arrival_input.setText("0")
        self.burst_input.setText("1")
        self.priority_input.setText("1")

    def delete_selected_process(self):
        selected_row = self.process_table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "Selection Error",
                "Please select a process row."
            )
            return

        pid = self.process_table.item(selected_row, 0).text()
        self.sim.processes = [p for p in self.sim.processes if p.pid != pid]

        self.refresh_process_table()

    def clear_all(self):
        self.sim.clear_processes()
        self.gantt_widget.set_gantt_chart([])
        self.feedback_box.setText(
            "Adaptive feedback will appear after running simulation."
        )
        self.refresh_process_table()

        for key, label in self.metric_labels.items():
            label.setText(f"{key}: -")

    def run_simulation(self):
        if not self.sim.processes:
            QMessageBox.warning(
                self,
                "No Processes",
                "Please add at least one process."
            )
            return

        algorithm = self.algorithm_combo.currentText()

        try:
            quantum = int(self.quantum_input.text())
        except ValueError:
            QMessageBox.warning(
                self,
                "Input Error",
                "Time Quantum must be a valid number."
            )
            return

        gantt_chart, metrics = self.sim.run(algorithm, time_quantum=quantum)

        self.gantt_widget.set_gantt_chart(gantt_chart)
        self.update_metrics(metrics)
        self.refresh_process_table()

        feedback = generate_feedback(metrics)
        self.feedback_box.setText("\n".join(f"• {item}" for item in feedback))

    def update_metrics(self, metrics):
        for key, label in self.metric_labels.items():
            value = metrics.get(key, "-")
            label.setText(f"{key}: {value}")

    def refresh_process_table(self):
        self.process_table.setRowCount(len(self.sim.processes))

        for row, p in enumerate(self.sim.processes):
            self.process_table.setRowHeight(row, 38)

            values = [
                p.pid,
                p.arrival_time,
                p.burst_time,
                p.remaining_time,
                p.priority,
                "-" if p.start_time is None else p.start_time,
                "-" if p.completion_time is None else p.completion_time,
                p.waiting_time,
                p.turnaround_time,
                "-" if p.response_time is None else p.response_time,
                p.status
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if col == 10:
                    if value == "Completed":
                        item.setBackground(QColor("#065F46"))
                    elif value == "Running":
                        item.setBackground(QColor("#1D4ED8"))
                    elif value == "Ready":
                        item.setBackground(QColor("#92400E"))
                    else:
                        item.setBackground(QColor("#374151"))

                self.process_table.setItem(row, col, item)

    def compare_algorithms(self):
        if not self.sim.processes:
            QMessageBox.warning(
                self,
                "No Processes",
                "Please add processes first."
            )
            return

        algorithms = [
            "FCFS",
            "SJF",
            "SRTF",
            "Priority Non-Preemptive",
            "Priority Preemptive",
            "Round Robin",
            "MLFQ"
        ]

        dialog = QDialog(self)
        dialog.setWindowTitle("Algorithm Comparison")
        dialog.setGeometry(200, 150, 950, 450)
        dialog.setStyleSheet(APP_STYLE)

        layout = QVBoxLayout(dialog)

        title = QLabel("Algorithm Performance Comparison")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #22D3EE;")
        layout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Algorithm",
            "Avg Waiting",
            "Avg Turnaround",
            "Avg Response",
            "CPU Utilization",
            "Throughput"
        ])
        table.setRowCount(len(algorithms))
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        try:
            quantum = int(self.quantum_input.text())
        except ValueError:
            quantum = 2

        for row, algo in enumerate(algorithms):
            temp_sim = Simulator()

            for process in self.sim.processes:
                temp_sim.add_process(
                    Process(
                        process.pid,
                        process.arrival_time,
                        process.burst_time,
                        process.priority
                    )
                )

            _, metrics = temp_sim.run(algo, time_quantum=quantum)

            values = [
                algo,
                metrics.get("Average Waiting Time", "-"),
                metrics.get("Average Turnaround Time", "-"),
                metrics.get("Average Response Time", "-"),
                metrics.get("CPU Utilization", "-"),
                metrics.get("Throughput", "-")
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)

        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()