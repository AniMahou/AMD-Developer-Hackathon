import json
import time
from orchestrator import process_task
from pathlib import Path

def run_benchmark(input_file="benchmark_tasks.json", output_file="submission.json"):
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: {input_file} not found. Please place your benchmark file here.")
        return
    
    with open(input_path, 'r') as f:
        tasks = json.load(f)
    
    print(f"Loaded {len(tasks)} tasks.")
    results = []
    start_time = time.time()
    
    for idx, task in enumerate(tasks):
        prompt = task.get("prompt", "")
        task_id = task.get("id", idx)
        
        print(f"\n--- Task {idx+1}/{len(tasks)} (ID: {task_id}) ---")
        answer = process_task(prompt)
        results.append({"id": task_id, "answer": answer})
        
        elapsed = time.time() - start_time
        avg_time = elapsed / (idx + 1)
        remaining = avg_time * (len(tasks) - idx - 1)
        print(f"Progress: {idx+1}/{len(tasks)} | Avg: {avg_time:.2f}s/task | ETA: {remaining/60:.1f} min")
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Done! Submission saved to {output_file}")
    print(f"Total time: {(time.time() - start_time)/60:.2f} minutes")

if __name__ == "__main__":
    run_benchmark()
