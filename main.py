import json
import time
from orchestrator import process_task

def run_benchmark():
    try:
        with open("benchmark_tasks.json", "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print("Error: benchmark_tasks.json not found.")
        return

    results = []
    print(f"Starting {len(tasks)} tasks...")
    for idx, task in enumerate(tasks):
        prompt = task.get("prompt", "")
        task_id = task.get("id", idx)
        print(f"\n--- Task {idx+1} ---")
        answer = process_task(prompt)
        results.append({"id": task_id, "answer": answer})
    
    with open("submission.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Submission saved to submission.json")
    print("Check your Fireworks dashboard for exact token count!")

if __name__ == "__main__":
    run_benchmark()
