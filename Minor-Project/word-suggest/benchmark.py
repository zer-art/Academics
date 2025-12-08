import time
import pandas as pd
import suggest

# Test dataset: (misspelled, correct)
test_data = [
    ("helllo", "hello"),
    ("wrld", "world"),
    ("aplple", "apple"),
    ("sugest", "suggest"),
    ("inforamtion", "information"),
    ("cmputer", "computer"),
    ("pyhton", "python"),
    ("dataaa", "data"),
    ("analysiss", "analysis"),
    ("inteleligence", "intelligence"),
    ("tring", "string"),
    ("lov", "love"),
    ("beter", "better"),
    ("wrok", "work"),
    ("hapiness", "happiness")
]

def benchmark():
    print("Starting Benchmark...")
    start_time = time.time()
    
    top1_correct = 0
    top5_correct = 0
    total_samples = len(test_data)
    latencies = []

    for misspelled, correct in test_data:
        t0 = time.time()
        # suggest.autocorrect returns a DataFrame with 'word' and 'probability'
        results = suggest.autocorrect(misspelled)
        t1 = time.time()
        latencies.append((t1 - t0) * 1000) # milliseconds

        if not results.empty:
            top_words = results['word'].tolist()
            
            # Top-1 Accuracy
            if top_words[0] == correct:
                top1_correct += 1
            
            # Top-5 Accuracy
            if correct in top_words[:5]:
                top5_correct += 1
        
    end_time = time.time()
    total_time = end_time - start_time
    avg_latency = sum(latencies) / len(latencies)

    top1_acc = (top1_correct / total_samples) * 100
    top5_acc = (top5_correct / total_samples) * 100

    print("\nBenchmark Results:")
    print(f"Total Samples: {total_samples}")
    print(f"Top-1 Accuracy: {top1_acc:.2f}%")
    print(f"Top-5 Accuracy: {top5_acc:.2f}%")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"Total Benchmark Time: {total_time:.2f} seconds")

if __name__ == "__main__":
    try:
        benchmark()
    except Exception as e:
        print(f"An error occurred during benchmarking: {e}")
