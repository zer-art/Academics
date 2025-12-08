
import time
import psutil
import torch
import cv2
import numpy as np
import platform
import os
import sys
from typing import Dict, List, Any
from torchvision.models import resnet50, ResNet50_Weights

# Add project root to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.src.facemesh import MediaPipeFaceMesh

class BenchmarkRunner:
    def __init__(self, num_runs: int = 100, warm_up: int = 10):
        self.num_runs = num_runs
        self.warm_up = warm_up
        self.process = psutil.Process(os.getpid())
        self.results = {}
        
        # Test image (random noise if no real image available)
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def measure_resources(self) -> Dict[str, float]:
        """Get current CPU and Memory usage"""
        cpu_percent = self.process.cpu_percent(interval=None)
        memory_info = self.process.memory_info()
        return {
            "cpu": cpu_percent,
            "memory_mb": memory_info.rss / (1024 * 1024)
        }

    def benchmark_model(self, model_name: str, model_func: Any, input_data: Any) -> Dict[str, float]:
        print(f"Benchmarking {model_name}...")
        
        latencies = []
        cpu_usages = []
        memory_usages = []
        
        # Warm-up
        print("  Warming up...")
        for _ in range(self.warm_up):
            model_func(input_data)
        
        # Reset CPU timer
        self.process.cpu_percent(interval=None)
        
        # Measurement loop
        print(f"  Running {self.num_runs} iterations...")
        start_time_total = time.time()
        
        for i in range(self.num_runs):
            iter_start = time.time()
            model_func(input_data)
            latencies.append((time.time() - iter_start) * 1000) # ms
            
            if i % 10 == 0:
                resources = self.measure_resources()
                cpu_usages.append(resources["cpu"])
                memory_usages.append(resources["memory_mb"])
        
        total_time = time.time() - start_time_total
        
        avg_latency = np.mean(latencies)
        avg_fps = 1000 / avg_latency if avg_latency > 0 else 0
        avg_cpu = np.mean(cpu_usages) if cpu_usages else 0
        avg_memory = np.mean(memory_usages) if memory_usages else 0
        
        print(f"  -> Avg Latency: {avg_latency:.2f} ms")
        print(f"  -> Avg FPS: {avg_fps:.2f}")
        print(f"  -> Avg CPU: {avg_cpu:.1f}%")
        print(f"  -> Avg Memory: {avg_memory:.1f} MB")
        
        return {
            "latency": avg_latency,
            "fps": avg_fps,
            "cpu": avg_cpu,
            "memory": avg_memory
        }

def run_benchmark():
    runner = BenchmarkRunner(num_runs=100)
    
    # 1. MediaPipe Benchmark
    mp_tracker = MediaPipeFaceMesh()
    
    def run_mediapipe(frame):
        # MediaPipe expects RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_tracker.analyze_frame(frame) # Using the wrapper method
        
    mp_results = runner.benchmark_model("AIVOX (MediaPipe)", run_mediapipe, runner.test_image)
    
    # 2. CNN Baseline (ResNet50)
    # Using ResNet50 as a proxy for a heavy face analysis model if DeepFace isn't available
    print("\nLoading ResNet50 (Traditional CNN Proxy)...")
    try:
        cnn_model = resnet50(weights=ResNet50_Weights.DEFAULT)
        cnn_model.eval()
        
        # Standard transform for ResNet
        from torchvision import transforms
        preprocess = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        def run_cnn(frame):
            input_tensor = preprocess(frame)
            input_batch = input_tensor.unsqueeze(0) 
            with torch.no_grad():
                cnn_model(input_batch)
                
        cnn_results = runner.benchmark_model("Traditional CNN (ResNet50)", run_cnn, runner.test_image)
        
    except Exception as e:
        print(f"Failed to load CNN baseline: {e}")
        cnn_results = None

    # Generate Report
    print("\n" + "="*50)
    print("BENCHMARK RESULTS")
    print("="*50)
    
    headers = ["Metric", "Traditional CNN", "AIVOX (MediaPipe)", "Improvement"]
    row_fmt = "{:<20} {:<20} {:<20} {:<20}"
    
    print(row_fmt.format(*headers))
    print("-" * 80)
    
    if cnn_results:
        # Latency
        cnn_lat = cnn_results['latency']
        mp_lat = mp_results['latency']
        lat_imp = f"{cnn_lat / mp_lat:.1f}x Faster" if mp_lat > 0 else "N/A"
        print(row_fmt.format("Latency (ms)", f"{cnn_lat:.1f}", f"{mp_lat:.1f}", lat_imp))
        
        # FPS
        cnn_fps = cnn_results['fps']
        mp_fps = mp_results['fps']
        fps_imp = f"+{mp_fps - cnn_fps:.1f} FPS"
        print(row_fmt.format("FPS", f"{cnn_fps:.1f}", f"{mp_fps:.1f}", fps_imp))
        
        # CPU
        cnn_cpu = cnn_results['cpu']
        mp_cpu = mp_results['cpu']
        cpu_imp = f"-{cnn_cpu - mp_cpu:.1f}%"
        print(row_fmt.format("CPU Usage (%)", f"{cnn_cpu:.1f}", f"{mp_cpu:.1f}", cpu_imp))
        
        # Memory
        cnn_mem = cnn_results['memory']
        mp_mem = mp_results['memory']
        mem_imp = f"{cnn_mem / mp_mem:.1f}x Smaller" if mp_mem > 0 else "N/A"
        print(row_fmt.format("Memory (MB)", f"{cnn_mem:.1f}", f"{mp_mem:.1f}", mem_imp))
        
    print("="*50)
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python: {platform.python_version()}")

if __name__ == "__main__":
    run_benchmark()
