"""
Fair Performance Comparison: aiofiles-x vs aiofiles (Apple to Apple)

Both implementations tested through their Python API interface.

Aiofiles-X
Copyright (C) 2025 ohmyarthur

This file is part of <https://github.com/ohmyarthur/aiofiles-x/>
Please read the GNU Affero General Public License in
<https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.
"""

import asyncio
import os
import sys
import platform
import subprocess
import tempfile
import time
import statistics
from pathlib import Path


class BenchmarkRunner:
    def __init__(self, label="aiofiles", use_aiofilesx=False):
        self.label = label
        self.use_aiofilesx = use_aiofilesx
        self.results = {}
        self.warmup_iterations = 2
        self.is_linux = platform.system() == "Linux"

        if use_aiofilesx:
            try:
                import aiofiles

                try:
                    import _aiofiles_core  # noqa: F401
                except ImportError:
                    pass

                self.aiofiles = aiofiles
                if not hasattr(aiofiles, "open"):
                    print(f"⚠️  Warning: aiofiles module attributes: {dir(aiofiles)}")
                    raise RuntimeError(
                        "aiofiles module does not have 'open' attribute. Check installation."
                    )
                print("✅ Using aiofiles-x (C++23 backend) via Python API")
            except ImportError:
                raise RuntimeError("aiofiles-x not installed. Run: pip install -e .")
        else:
            try:
                import aiofiles

                self.aiofiles = aiofiles
                if not hasattr(aiofiles, "open"):
                    print(f"⚠️  Warning: aiofiles module attributes: {dir(aiofiles)}")
                    raise RuntimeError(
                        "aiofiles module does not have 'open' attribute. Check installation."
                    )
                print("✅ Using aiofiles (Pure Python) via Python API")
            except ImportError:
                raise RuntimeError("aiofiles not installed. Run: pip install aiofiles")

    def drop_caches(self):
        if not self.is_linux:
            return

        try:
            subprocess.run(
                ["sudo", "-n", "sh", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            print("  💧 Dropped file system caches")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    async def warmup(self, temp_file):
        for _ in range(self.warmup_iterations):
            async with self.aiofiles.open(temp_file, "r") as f:
                await f.read()
        await asyncio.sleep(0.01)

    async def bench_sequential_reads(self, file_sizes, iterations=10):
        print(f"\n{'=' * 60}")
        print(f"Sequential Reads - {self.label}")
        print(f"{'=' * 60}")

        results = {}

        for size_name, size_bytes in file_sizes.items():
            times = []

            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
                temp_file = tf.name
                tf.write("x" * size_bytes)

            try:
                await self.warmup(temp_file)

                for i in range(iterations):
                    if i > 0:
                        self.drop_caches()
                        await asyncio.sleep(0.1)

                    start = time.perf_counter_ns()

                    async with self.aiofiles.open(temp_file, "r") as f:
                        await f.read()

                    elapsed = (time.perf_counter_ns() - start) / 1_000_000
                    times.append(elapsed)

                results[size_name] = {
                    "min": min(times),
                    "max": max(times),
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                }

                print(
                    f"{size_name:15s}: {results[size_name]['mean']:8.2f} ms "
                    f"(min: {results[size_name]['min']:6.2f}, "
                    f"max: {results[size_name]['max']:6.2f})"
                )

            finally:
                os.unlink(temp_file)

        self.results["sequential_reads"] = results
        return results

    async def bench_sequential_writes(self, file_sizes, iterations=10):
        print(f"\n{'=' * 60}")
        print(f"Sequential Writes - {self.label}")
        print(f"{'=' * 60}")

        results = {}

        for size_name, size_bytes in file_sizes.items():
            times = []
            data = "x" * size_bytes

            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
                warmup_file = tf.name
            try:
                for _ in range(self.warmup_iterations):
                    async with self.aiofiles.open(warmup_file, "w") as f:
                        await f.write(data[:1024])
            finally:
                os.unlink(warmup_file)

            for i in range(iterations):
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
                    temp_file = tf.name

                try:
                    if i > 0:
                        self.drop_caches()
                        await asyncio.sleep(0.1)

                    start = time.perf_counter_ns()

                    async with self.aiofiles.open(temp_file, "w") as f:
                        await f.write(data)

                    elapsed = (time.perf_counter_ns() - start) / 1_000_000
                    times.append(elapsed)
                finally:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)

            results[size_name] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            }

            print(
                f"{size_name:15s}: {results[size_name]['mean']:8.2f} ms "
                f"(min: {results[size_name]['min']:6.2f}, "
                f"max: {results[size_name]['max']:6.2f})"
            )

        self.results["sequential_writes"] = results
        return results

    async def bench_concurrent_operations(self, num_files_list, iterations=5):
        print(f"\n{'=' * 60}")
        print(f"Concurrent Operations - {self.label}")
        print(f"{'=' * 60}")

        results = {}

        for num_files in num_files_list:
            times = []

            warmup_files = []
            try:
                for i in range(min(5, num_files)):
                    tf = tempfile.NamedTemporaryFile(mode="w", delete=False)
                    warmup_files.append(tf.name)
                    tf.write(f"Warmup {i}")
                    tf.close()

                async def warmup_read(filename):
                    async with self.aiofiles.open(filename, "r") as f:
                        await f.read()

                for _ in range(self.warmup_iterations):
                    await asyncio.gather(*[warmup_read(f) for f in warmup_files])
            finally:
                for f in warmup_files:
                    if os.path.exists(f):
                        os.unlink(f)

            for iteration in range(iterations):
                temp_files = []

                try:
                    if iteration > 0:
                        self.drop_caches()
                        await asyncio.sleep(0.1)

                    for i in range(num_files):
                        tf = tempfile.NamedTemporaryFile(mode="w", delete=False)
                        temp_files.append(tf.name)
                        tf.write(f"Content {i}" * 100)
                        tf.close()

                    start = time.perf_counter_ns()

                    async def read_file(filename):
                        async with self.aiofiles.open(filename, "r") as f:
                            return await f.read()

                    tasks = [read_file(f) for f in temp_files]
                    await asyncio.gather(*tasks)

                    elapsed = (time.perf_counter_ns() - start) / 1_000_000
                    times.append(elapsed)

                finally:
                    for tf in temp_files:
                        if os.path.exists(tf):
                            os.unlink(tf)

            results[f"{num_files}_files"] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "throughput": num_files / (statistics.mean(times) / 1000),  # files/sec
            }

            print(
                f"{num_files:4d} files: {results[f'{num_files}_files']['mean']:8.2f} ms "
                f"({results[f'{num_files}_files']['throughput']:6.0f} files/sec)"
            )

        self.results["concurrent_operations"] = results
        return results

    async def bench_line_iteration(self, num_lines_list, iterations=5):
        """Benchmark line-by-line iteration."""
        print(f"\n{'=' * 60}")
        print(f"Line Iteration - {self.label}")
        print(f"{'=' * 60}")

        results = {}

        for num_lines in num_lines_list:
            times = []

            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
                temp_file = tf.name
                for i in range(num_lines):
                    tf.write(f"Line {i}\n")

            try:
                await self.warmup(temp_file)

                for iteration in range(iterations):
                    if iteration > 0:
                        self.drop_caches()
                        await asyncio.sleep(0.1)

                    start = time.perf_counter_ns()

                    lines = []
                    async with self.aiofiles.open(temp_file, "r") as f:
                        async for line in f:
                            lines.append(line)

                    elapsed = (time.perf_counter_ns() - start) / 1_000_000
                    times.append(elapsed)

                results[f"{num_lines}_lines"] = {
                    "min": min(times),
                    "max": max(times),
                    "median": statistics.median(times),
                    "mean": statistics.mean(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                    "throughput": num_lines / (statistics.mean(times) / 1000),  # lines/sec
                }

                print(
                    f"{num_lines:6d} lines: {results[f'{num_lines}_lines']['mean']:8.2f} ms "
                    f"({results[f'{num_lines}_lines']['throughput']:8.0f} lines/sec)"
                )

            finally:
                os.unlink(temp_file)

        self.results["line_iteration"] = results
        return results

    async def run_all_benchmarks(self):
        """Run all benchmark scenarios."""
        print(f"\n{'#' * 60}")
        print(f"# STRESS TEST: {self.label}")
        print(f"{'#' * 60}")

        file_sizes = {
            "1KB": 1024,
            "10KB": 10 * 1024,
            "100KB": 100 * 1024,
            "1MB": 1024 * 1024,
            "10MB": 10 * 1024 * 1024,
        }

        await self.bench_sequential_reads(file_sizes, iterations=10)
        await self.bench_sequential_writes(file_sizes, iterations=10)

        num_files_list = [10, 50, 100, 200, 500]
        await self.bench_concurrent_operations(num_files_list, iterations=5)

        num_lines_list = [100, 1000, 5000, 10000]
        await self.bench_line_iteration(num_lines_list, iterations=5)

        return self.results


def print_comparison(cpp_results, py_results):
    """Print side-by-side comparison with speedup."""
    print(f"\n{'=' * 80}")
    print("PERFORMANCE COMPARISON")
    print(f"{'=' * 80}")

    def compare_category(category_name, cpp_data, py_data):
        print(f"\n{category_name}:")
        print(f"{'Benchmark':<20} {'C++ (ms)':<12} {'Python (ms)':<12} {'Speedup':<10}")
        print(f"{'-' * 54}")

        for key in cpp_data.keys():
            if key in py_data:
                cpp_time = cpp_data[key]["mean"]
                py_time = py_data[key]["mean"]
                speedup = py_time / cpp_time

                speedup_str = f"{speedup:.2f}x" if speedup >= 1 else f"{1 / speedup:.2f}x slower"
                color = "✅" if speedup >= 1 else "❌"

                print(f"{key:<20} {cpp_time:<12.2f} {py_time:<12.2f} {color} {speedup_str}")

    if "sequential_reads" in cpp_results and "sequential_reads" in py_results:
        compare_category(
            "Sequential Reads",
            cpp_results["sequential_reads"],
            py_results["sequential_reads"],
        )

    if "sequential_writes" in cpp_results and "sequential_writes" in py_results:
        compare_category(
            "Sequential Writes",
            cpp_results["sequential_writes"],
            py_results["sequential_writes"],
        )

    if "concurrent_operations" in cpp_results and "concurrent_operations" in py_results:
        compare_category(
            "Concurrent Operations",
            cpp_results["concurrent_operations"],
            py_results["concurrent_operations"],
        )

    if "line_iteration" in cpp_results and "line_iteration" in py_results:
        compare_category(
            "Line Iteration",
            cpp_results["line_iteration"],
            py_results["line_iteration"],
        )


async def main():
    """Run benchmarks and compare (Apple to Apple via Python API)."""
    import json

    print("\n" + "=" * 80)
    print("BENCHMARK ENVIRONMENT")
    print("=" * 80)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"CPU: {platform.processor() or platform.machine()}")
    print("Timer: time.perf_counter_ns() (nanosecond precision)")
    if platform.system() == "Linux":
        print("Cache drop: Enabled (if sudo available)")
    print("Warmup iterations: 2 per test")
    print("=" * 80)

    results_file = Path(__file__).parent / "benchmark_results.json"

    try:
        import _aiofiles_core  # noqa: F401

        current_impl = "aiofiles-x"
        print("\n✅ Detected: aiofiles-x (C++23 backend)")
    except ImportError:
        current_impl = "aiofiles"
        print("\n✅ Detected: aiofiles (Pure Python)")

    print("\n" + "=" * 80)
    print(f"Running Benchmark: {current_impl}")
    print("=" * 80)

    is_aiofilesx = current_impl == "aiofiles-x"
    runner = BenchmarkRunner(
        label=f"{current_impl} ({'C++23' if is_aiofilesx else 'Python'})",
        use_aiofilesx=is_aiofilesx,
    )
    results = await runner.run_all_benchmarks()

    all_results = {}
    if results_file.exists():
        with open(results_file, "r") as f:
            all_results = json.load(f)

    all_results[current_impl] = results

    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Results saved to: {results_file}")

    if "aiofiles-x" in all_results and "aiofiles" in all_results:
        print("\n" + "=" * 80)
        print("📊 COMPARING BOTH IMPLEMENTATIONS")
        print("=" * 80)
        print_comparison(all_results["aiofiles-x"], all_results["aiofiles"])
    else:
        missing = "aiofiles" if current_impl == "aiofiles-x" else "aiofiles-x"
        print(f"\n💡 To compare with {missing}:")
        print(f"   1. pip uninstall {current_impl}")
        if missing == "aiofiles":
            print("   2. pip install aiofiles")
        else:
            print("   2. pip install -e .")
        print("   3. Run this script again")


if __name__ == "__main__":
    asyncio.run(main())
