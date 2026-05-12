def generate_feedback(metrics):
    feedback = []

    avg_waiting = metrics.get("Average Waiting Time", 0)
    avg_response = metrics.get("Average Response Time", 0)
    cpu_util = metrics.get("CPU Utilization", 0)

    if avg_waiting > 10:
        feedback.append("High waiting time detected. SJF or SRTF may perform better.")

    if avg_response > 5:
        feedback.append("High response time detected. Round Robin is recommended.")

    if cpu_util < 70:
        feedback.append("CPU utilization is low. Check process arrival gaps.")

    if not feedback:
        feedback.append("Current scheduling performance looks good.")

    return feedback