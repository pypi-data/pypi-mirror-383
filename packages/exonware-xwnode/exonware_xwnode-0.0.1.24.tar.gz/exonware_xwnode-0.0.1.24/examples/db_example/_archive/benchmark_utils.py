#!/usr/bin/env python3
"""
Benchmark Utilities

Provides time and memory measurement utilities for database benchmarking.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 11, 2025
"""

import time
import psutil
import os
from typing import Dict, Any, Callable
from contextlib import contextmanager


class BenchmarkMetrics:
    """Stores and manages benchmark metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.process = psutil.Process(os.getpid())
        
    def start_operation(self, operation_name: str):
        """Start timing an operation"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'count': 0,
                'total_time_ms': 0.0,
                'min_time_ms': float('inf'),
                'max_time_ms': 0.0,
                'avg_time_ms': 0.0,
                'peak_memory_mb': 0.0
            }
        
        self.metrics[operation_name]['_start_time'] = time.perf_counter()
        self.metrics[operation_name]['_start_memory'] = self.process.memory_info().rss / (1024 * 1024)
        
    def end_operation(self, operation_name: str):
        """End timing an operation"""
        if operation_name not in self.metrics:
            return
        
        # Calculate time
        end_time = time.perf_counter()
        start_time = self.metrics[operation_name].get('_start_time', end_time)
        elapsed_ms = (end_time - start_time) * 1000
        
        # Calculate memory
        end_memory = self.process.memory_info().rss / (1024 * 1024)
        start_memory = self.metrics[operation_name].get('_start_memory', end_memory)
        memory_delta = end_memory - start_memory
        
        # Update metrics
        metrics = self.metrics[operation_name]
        metrics['count'] += 1
        metrics['total_time_ms'] += elapsed_ms
        metrics['min_time_ms'] = min(metrics['min_time_ms'], elapsed_ms)
        metrics['max_time_ms'] = max(metrics['max_time_ms'], elapsed_ms)
        metrics['avg_time_ms'] = metrics['total_time_ms'] / metrics['count']
        metrics['peak_memory_mb'] = max(metrics['peak_memory_mb'], end_memory)
        
        # Clean up temporary keys
        metrics.pop('_start_time', None)
        metrics.pop('_start_memory', None)
        
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager for measuring operations"""
        self.start_operation(operation_name)
        try:
            yield
        finally:
            self.end_operation(operation_name)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {k: v for k, v in self.metrics.items() if not k.startswith('_')}
    
    def get_total_time(self) -> float:
        """Get total time across all operations in milliseconds"""
        return sum(m['total_time_ms'] for m in self.metrics.values() if 'total_time_ms' in m)
    
    def get_peak_memory(self) -> float:
        """Get peak memory usage across all operations in MB"""
        return max((m['peak_memory_mb'] for m in self.metrics.values() if 'peak_memory_mb' in m), default=0.0)
    
    def print_summary(self, title: str = "Benchmark Summary"):
        """Print a formatted summary of metrics"""
        print(f"\n{'='*80}")
        print(f"{title}")
        print(f"{'='*80}")
        
        for operation, metrics in self.metrics.items():
            if operation.startswith('_'):
                continue
            print(f"\n[{operation}]:")
            print(f"   Count: {metrics['count']}")
            print(f"   Total Time: {metrics['total_time_ms']:.2f} ms")
            print(f"   Avg Time: {metrics['avg_time_ms']:.4f} ms")
            print(f"   Min Time: {metrics['min_time_ms']:.4f} ms")
            print(f"   Max Time: {metrics['max_time_ms']:.4f} ms")
            print(f"   Peak Memory: {metrics['peak_memory_mb']:.2f} MB")
        
        print(f"\n{'='*80}")
        print(f"TOTAL TIME: {self.get_total_time():.2f} ms")
        print(f"PEAK MEMORY: {self.get_peak_memory():.2f} MB")
        print(f"{'='*80}\n")


def measure_function(func: Callable, metrics: BenchmarkMetrics, operation_name: str, *args, **kwargs):
    """Measure a function call"""
    with metrics.measure(operation_name):
        return func(*args, **kwargs)

