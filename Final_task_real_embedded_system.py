
from math import gcd
from functools import reduce
import matplotlib.pyplot as plt

# Tâches définies par (C, T)
tasks = {
    'τ1': (2, 10),
    'τ2': (3, 10),
    'τ3': (2, 20),
    'τ4': (2, 20),
    'τ5': (2, 40),
    'τ6': (2, 40),
    'τ7': (3, 80)
}

# Fonctions utilitaires
def lcm(a, b):
    return a * b // gcd(a, b)

def hyperperiod(task_list):
    periods = [t[1] for t in task_list]
    return reduce(lcm, periods)

# Scheduleur non préemptif RMS
def rms_non_preemptive_scheduler(tasks, H):
    jobs = []
    priority = {name: T for name, (C, T) in tasks.items()}

    for name, (C, T) in tasks.items():
        for release in range(0, H, T):
            jobs.append({
                'name': name,
                'release': release,
                'deadline': release + T,
                'remaining': C,
                'executed': False,
                'start': None,
                'finish': None
            })

    timeline = []
    current_time = 0

    while current_time < H:
        ready_jobs = [
            job for job in jobs
            if job['release'] <= current_time and not job['executed']
        ]
        ready_jobs.sort(key=lambda j: priority[j['name']])

        if ready_jobs:
            job = ready_jobs[0]
            job['start'] = current_time
            duration = job['remaining']
            for _ in range(duration):
                timeline.append(job['name'])
            job['executed'] = True
            job['finish'] = current_time + duration - 1
            current_time += duration
        else:
            timeline.append("IDLE")
            current_time += 1

    return timeline, jobs

# Affichage et analyse
def try_scheduler(name, scheduler_func):
    print(f"\n=== Trying scheduler: {name} ===")
    H = hyperperiod(tasks.values())
    timeline, jobs = scheduler_func(tasks, H)

    # Vérifie les deadlines
    all_met = True
    job_data = {}
    for job in jobs:
        if not job['executed']:
            print(f" Job {job['name']} (release {job['release']}) not executed.")
            all_met = False
        elif job['finish'] >= job['deadline']:
            print(f" Job {job['name']} (release {job['release']}) missed its deadline.")
            all_met = False
        else:
            R = job['finish'] - job['release'] + 1
            job_data.setdefault(job['name'], []).append({
                'release': job['release'],
                'R': R
            })

    if all_met:
        print(" All deadlines were met.")
    else:
        print(" Some deadlines were missed.")

    # Temps de réponse selon ta formule
    print("\n Response Times with Recurrence Formula:")
    for name in sorted(job_data.keys()):
        R_list = []
        jobs_list = job_data[name]
        for i, job in enumerate(jobs_list):
            a_n = job['release']
            C_n = tasks[name][0]
            if i == 0:
                R_n = C_n
            else:
                a_prev = jobs_list[i - 1]['release']
                R_prev = R_list[i - 1]
                R_n = C_n + R_prev - (a_n - a_prev)
            R_list.append(R_n)
            print(f"{name} - Job {i}: a={a_n}, R={R_n}")
    plot_schedule(timeline, H)

# Diagramme de Gantt simplifié
def plot_schedule(timeline, H):
    exec_blocks = []
    start = 0
    while start < len(timeline):
        task = timeline[start]
        end = start + 1
        while end < len(timeline) and timeline[end] == task:
            end += 1
        if task != 'IDLE':
            exec_blocks.append((task, start, end - start))
        start = end

    task_names = sorted(set(t for t in timeline if t != 'IDLE'))
    task_y = {name: i for i, name in enumerate(task_names)}
    colors = plt.cm.get_cmap('tab20', len(task_names))

    fig, ax = plt.subplots(figsize=(12, 4))
    for task, start, dur in exec_blocks:
        y = task_y[task]
        ax.broken_barh([(start, dur)], (y - 0.4, 0.8),
                       facecolors=colors(task_names.index(task)))

    ax.set_xlabel("Time")
    ax.set_ylabel("Tasks")
    ax.set_yticks(range(len(task_names)))
    ax.set_yticklabels(task_names)
    ax.set_title("Non-Preemptive RMS Schedule Timeline")
    ax.grid(True)
    plt.tight_layout()
    plt.show()

# Lancer le test
try_scheduler("Rate Monotonic Scheduling (Non-Preemptive)", rms_non_preemptive_scheduler)
