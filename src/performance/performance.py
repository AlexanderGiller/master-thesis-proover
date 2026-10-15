"""Performance tracking for proof verification operations.

This module tracks:
- WC Time (Wall-Clock Time): Real elapsed time
- CPU Time: Processor CPU time used

Example:
    tracker = PerformanceTracker()
    tracker.start()
    # ... do work ...
    tracker.stop()
    print(tracker.get_summary())
"""

import time
import os
from typing import Optional
from dataclasses import dataclass
from statistics import mean, stdev


@dataclass
class TimeMeasurement:
    """A single time measurement for an operation."""
    operation_name: str
    wc_time: float  # Wall-clock time (seconds)
    cpu_time: float  # CPU time (seconds)

    def __repr__(self):
        return f"{self.operation_name}: WC={self.wc_time:.2f}s, CPU={self.cpu_time:.2f}s"


class PerformanceTracker:
    """Track performance metrics for proof checking operations."""

    def __init__(self):
        """Initialize the performance tracker."""
        self.measurements: list[TimeMeasurement] = []
        self._start_time: Optional[float] = None
        self._start_cpu_time: Optional[float] = None

    def start(self):
        """Start measuring time for a new operation."""
        self._start_time = time.perf_counter()
        # Try to get CPU time (works on Unix-like systems)
        try:
            self._start_cpu_time = os.times().user
        except:
            self._start_cpu_time = time.process_time()

    def stop(self, operation_name: str = "operation") -> TimeMeasurement:
        """Stop measuring time and record the measurement.

        Args:
            operation_name: Name/description of the operation measured

        Returns:
            TimeMeasurement object with the elapsed times
        """
        if self._start_time is None:
            raise ValueError("Tracker was not started. Call start() first.")

        # Calculate wall-clock time
        wc_time = time.perf_counter() - self._start_time

        # Calculate CPU time
        try:
            current_cpu = os.times().user
            cpu_time = current_cpu - self._start_cpu_time
        except:
            current_cpu = time.process_time()
            cpu_time = current_cpu - self._start_cpu_time

        measurement = TimeMeasurement(
            operation_name=operation_name,
            wc_time=wc_time,
            cpu_time=cpu_time
        )

        self.measurements.append(measurement)
        self._start_time = None
        self._start_cpu_time = None

        return measurement

    def add_measurement(self, operation_name: str, wc_time: float, cpu_time: float):
        """Manually add a measurement without using start/stop.

        Args:
            operation_name: Name of the operation
            wc_time: Wall-clock time in seconds
            cpu_time: CPU time in seconds
        """
        measurement = TimeMeasurement(operation_name, wc_time, cpu_time)
        self.measurements.append(measurement)
        return measurement

    def get_summary_by_operation(self) -> dict:
        """Get summary statistics grouped by operation name.

        Returns:
            Dict with operation names as keys and statistics as values
        """
        if not self.measurements:
            return {}

        operations = {}
        for measurement in self.measurements:
            if measurement.operation_name not in operations:
                operations[measurement.operation_name] = {
                    'wc_times': [],
                    'cpu_times': [],
                    'count': 0
                }
            operations[measurement.operation_name]['wc_times'].append(measurement.wc_time)
            operations[measurement.operation_name]['cpu_times'].append(measurement.cpu_time)
            operations[measurement.operation_name]['count'] += 1

        # Calculate statistics for each operation
        summary = {}
        for op_name, times in operations.items():
            wc_list = times['wc_times']
            cpu_list = times['cpu_times']

            summary[op_name] = {
                'count': times['count'],
                'wc_time': {
                    'min': min(wc_list),
                    'max': max(wc_list),
                    'mean': mean(wc_list),
                    'total': sum(wc_list),
                    'stdev': stdev(wc_list) if len(wc_list) > 1 else 0.0
                },
                'cpu_time': {
                    'min': min(cpu_list),
                    'max': max(cpu_list),
                    'mean': mean(cpu_list),
                    'total': sum(cpu_list),
                    'stdev': stdev(cpu_list) if len(cpu_list) > 1 else 0.0
                }
            }

        return summary

    def get_overall_summary(self) -> dict:
        """Get overall performance summary across all measurements.

        Returns:
            Dict with total and average times
        """
        if not self.measurements:
            return {
                'total_measurements': 0,
                'total_wc_time': 0.0,
                'total_cpu_time': 0.0,
                'avg_wc_time': 0.0,
                'avg_cpu_time': 0.0
            }

        wc_times = [m.wc_time for m in self.measurements]
        cpu_times = [m.cpu_time for m in self.measurements]

        return {
            'total_measurements': len(self.measurements),
            'total_wc_time': sum(wc_times),
            'total_cpu_time': sum(cpu_times),
            'avg_wc_time': mean(wc_times),
            'avg_cpu_time': mean(cpu_times),
            'min_wc_time': min(wc_times),
            'max_wc_time': max(wc_times),
            'min_cpu_time': min(cpu_times),
            'max_cpu_time': max(cpu_times),
            'stdev_wc_time': stdev(wc_times) if len(wc_times) > 1 else 0.0,
            'stdev_cpu_time': stdev(cpu_times) if len(cpu_times) > 1 else 0.0
        }

    def print_summary(self, operation_filter: Optional[str] = None):
        """Print a formatted performance summary.

        Args:
            operation_filter: If provided, only show this operation name
        """
        if not self.measurements:
            print("No measurements recorded")
            return

        print("\n" + "="*80)
        print("PERFORMANCE SUMMARY")
        print("="*80)

        # Filter measurements if requested
        measurements = self.measurements
        if operation_filter:
            measurements = [m for m in measurements if m.operation_name == operation_filter]
            if not measurements:
                print(f"No measurements found for operation: {operation_filter}")
                return
            print(f"\nOperation: {operation_filter}")
        else:
            print("\nAll Operations:")

        print(f"Total runs: {len(measurements)}")
        print()

        # Calculate statistics
        wc_times = [m.wc_time for m in measurements]
        cpu_times = [m.cpu_time for m in measurements]

        print(f"Wall-Clock Time (WC Time):")
        print(f"  Average (Av.):  {mean(wc_times):.4f} s")
        print(f"  Min:            {min(wc_times):.4f} s")
        print(f"  Max:            {max(wc_times):.4f} s")
        print(f"  Total:          {sum(wc_times):.4f} s")
        if len(wc_times) > 1:
            print(f"  Std Dev:        {stdev(wc_times):.4f} s")

        print()
        print(f"CPU Time:")
        print(f"  Average (Av.):  {mean(cpu_times):.4f} s")
        print(f"  Min:            {min(cpu_times):.4f} s")
        print(f"  Max:            {max(cpu_times):.4f} s")
        print(f"  Total:          {sum(cpu_times):.4f} s")
        if len(cpu_times) > 1:
            print(f"  Std Dev:        {stdev(cpu_times):.4f} s")

        # Show overhead (time spent waiting for I/O, etc.)
        overhead = sum(wc_times) - sum(cpu_times)
        overhead_pct = (overhead / sum(wc_times) * 100) if sum(wc_times) > 0 else 0
        print()
        print(f"Overhead (I/O, waiting, etc.):")
        print(f"  Total:          {overhead:.4f} s ({overhead_pct:.1f}%)")

        print("="*80)

    def get_all_measurements(self) -> list[TimeMeasurement]:
        """Get all recorded measurements."""
        return self.measurements.copy()

    def reset(self):
        """Clear all measurements."""
        self.measurements.clear()
        self._start_time = None
        self._start_cpu_time = None


def print_performance_table(tracker: PerformanceTracker):
    """Print a table of all performance measurements.

    Args:
        tracker: PerformanceTracker instance
    """
    measurements = tracker.get_all_measurements()
    if not measurements:
        print("No measurements recorded")
        return

    print("\n" + "="*100)
    print("DETAILED PERFORMANCE MEASUREMENTS")
    print("="*100)
    print(f"{'Operation':<40} {'WC Time (s)':>15} {'CPU Time (s)':>15} {'Overhead':>15}")
    print("-"*100)

    for measurement in measurements:
        overhead = measurement.wc_time - measurement.cpu_time
        print(
            f"{measurement.operation_name:<40} {measurement.wc_time:>15.4f} "
            f"{measurement.cpu_time:>15.4f} {overhead:>15.4f}"
        )

    print("="*100)

