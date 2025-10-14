#!/usr/bin/env python3
"""
Benchmark Both Implementations Side-by-Side
Run aiofiles (pure Python) and aiofiles-x (C++23) in isolated environments

Usage:
    python3 compare_both.py
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def print_header(title):
    """Print fancy header."""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print(f"{'=' * 80}\n")


def run_in_subprocess(python_cmd, script_path, env_vars=None):
    """Run benchmark in subprocess with specific Python."""
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [python_cmd, script_path],
        capture_output=True,
        text=True,
        env=env,
        cwd=Path(__file__).parent,
    )

    return result.returncode, result.stdout, result.stderr


def setup_venv(venv_path, package_name, is_editable=False):
    """Setup virtual environment with specific package."""
    venv_path = Path(venv_path)

    print(f"Setting up venv: {venv_path}")

    if not venv_path.exists():
        print("  Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    python_bin = venv_path / "bin" / "python3"

    if is_editable:
        project_root = Path(__file__).parent.parent.parent
        print(f"  Installing {package_name} (editable)...")
        subprocess.run(
            [str(python_bin), "-m", "pip", "install", "-q", "-e", str(project_root)],
            check=True,
        )
    else:
        print(f"  Installing {package_name} from PyPI...")
        subprocess.run([str(python_bin), "-m", "pip", "install", "-q", package_name], check=True)

    print(f"  ✅ {package_name} installed\n")
    return python_bin


def create_isolated_benchmark_script():
    """Create temporary benchmark script that works in isolation."""
    script_content = '''
import asyncio
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import statistics
from pathlib import Path

WARMUP_ITERATIONS = 2
IS_LINUX = platform.system() == "Linux"

def drop_caches():
    """Drop filesystem caches (Linux only)."""
    if not IS_LINUX:
        return
    try:
        subprocess.run(
            ["sudo", "-n", "sh", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"],
            capture_output=True,
            timeout=5,
            check=False,
        )
    except:
        pass

async def warmup(aiofiles_module, temp_file):
    """Warmup runs."""
    for _ in range(WARMUP_ITERATIONS):
        async with aiofiles_module.open(temp_file, "r") as f:
            await f.read()
    await asyncio.sleep(0.01)

async def bench_sequential_reads(aiofiles_module, file_sizes, iterations=10):
    """Benchmark sequential reads."""
    results = {}

    for size_name, size_bytes in file_sizes.items():
        times = []

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            temp_file = tf.name
            tf.write("x" * size_bytes)

        try:
            await warmup(aiofiles_module, temp_file)

            for i in range(iterations):
                if i > 0:
                    drop_caches()
                    await asyncio.sleep(0.1)

                start = time.perf_counter_ns()
                async with aiofiles_module.open(temp_file, "r") as f:
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
        finally:
            os.unlink(temp_file)

    return results

async def bench_concurrent_operations(aiofiles_module, num_files_list, iterations=5):
    """Benchmark concurrent operations."""
    results = {}

    for num_files in num_files_list:
        times = []

        for iteration in range(iterations):
            temp_files = []
            try:
                if iteration > 0:
                    drop_caches()
                    await asyncio.sleep(0.1)

                for i in range(num_files):
                    tf = tempfile.NamedTemporaryFile(mode="w", delete=False)
                    temp_files.append(tf.name)
                    tf.write(f"Content {i}" * 100)
                    tf.close()

                start = time.perf_counter_ns()

                async def read_file(filename):
                    async with aiofiles_module.open(filename, "r") as f:
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
            "throughput": num_files / (statistics.mean(times) / 1000),
        }

    return results

async def bench_write_operations(aiofiles_module, file_sizes, iterations=10):
    """Benchmark write operations."""
    results = {}

    for size_name, size_bytes in file_sizes.items():
        times = []
        data = "x" * size_bytes

        for i in range(iterations):
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
                temp_file = tf.name

            try:
                if i > 0:
                    drop_caches()
                    await asyncio.sleep(0.1)

                start = time.perf_counter_ns()
                async with aiofiles_module.open(temp_file, "w") as f:
                    await f.write(data)
                    await f.flush()
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

    return results

async def bench_line_operations(aiofiles_module, iterations=10):
    """Benchmark line-by-line operations."""
    times = []

    for i in range(iterations):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            temp_file = tf.name
            for line_num in range(1000):
                tf.write(f"Line {line_num}\\n")

        try:
            if i > 0:
                drop_caches()
                await asyncio.sleep(0.1)

            start = time.perf_counter_ns()
            async with aiofiles_module.open(temp_file, "r") as f:
                count = 0
                async for line in f:
                    count += 1
            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            times.append(elapsed)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    return {
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
    }

async def bench_seek_operations(aiofiles_module, iterations=10):
    """Benchmark seek and tell operations."""
    times = []

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("x" * 1024 * 1024)

    try:
        for i in range(iterations):
            if i > 0:
                await asyncio.sleep(0.05)

            start = time.perf_counter_ns()
            async with aiofiles_module.open(temp_file, "r") as f:
                await f.seek(512 * 1024)
                pos = await f.tell()
                await f.read(1024)
                await f.seek(0)
                await f.read(1024)
            elapsed = (time.perf_counter_ns() - start) / 1_000_000
            times.append(elapsed)
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    return {
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
    }

async def main():
    import aiofiles

    try:
        import _aiofiles_core
        impl_name = "aiofiles-x"
    except ImportError:
        impl_name = "aiofiles"

    print(f"\\nRunning: {impl_name}")

    results = {}

    file_sizes = {
        "1KB": 1024,
        "10KB": 10 * 1024,
        "100KB": 100 * 1024,
        "1MB": 1024 * 1024,
        "10MB": 10 * 1024 * 1024,
    }

    print("  Sequential reads...", end="", flush=True)
    results["sequential_reads"] = await bench_sequential_reads(aiofiles, file_sizes)
    print(" ✓")

    print("  Write operations...", end="", flush=True)
    results["write_operations"] = await bench_write_operations(aiofiles, file_sizes)
    print(" ✓")

    num_files_list = [10, 50, 100, 200, 500]
    print("  Concurrent operations...", end="", flush=True)
    results["concurrent_operations"] = await bench_concurrent_operations(aiofiles, num_files_list)
    print(" ✓")

    print("  Line operations...", end="", flush=True)
    results["line_operations"] = await bench_line_operations(aiofiles)
    print(" ✓")

    print("  Seek operations...", end="", flush=True)
    results["seek_operations"] = await bench_seek_operations(aiofiles)
    print(" ✓")

    output_file = f"results_{impl_name}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"  Saved to: {output_file}\\n")

if __name__ == "__main__":
    asyncio.run(main())
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script_content)
        return Path(f.name)


def print_comparison(results_python, results_cpp):
    """Print side-by-side comparison."""
    print_header("📊 PERFORMANCE COMPARISON")

    def compare_category(category_name, py_data, cpp_data):
        print(f"\n{category_name}:")
        print(f"{'Benchmark':<20} {'Python (ms)':<14} {'C++23 (ms)':<14} {'Speedup':<12}")
        print(f"{'-' * 62}")

        for key in sorted(py_data.keys()):
            if key in cpp_data:
                py_time = py_data[key]["mean"]
                cpp_time = cpp_data[key]["mean"]
                speedup = py_time / cpp_time

                if speedup >= 1:
                    speedup_str = f"✅ {speedup:.2f}x faster"
                else:
                    speedup_str = f"❌ {1 / speedup:.2f}x slower"

                print(f"{key:<20} {py_time:<14.2f} {cpp_time:<14.2f} {speedup_str:<12}")

    if "sequential_reads" in results_python:
        compare_category(
            "Sequential Reads",
            results_python["sequential_reads"],
            results_cpp["sequential_reads"],
        )

    if "write_operations" in results_python:
        compare_category(
            "Write Operations",
            results_python["write_operations"],
            results_cpp["write_operations"],
        )

    if "concurrent_operations" in results_python:
        compare_category(
            "Concurrent Operations",
            results_python["concurrent_operations"],
            results_cpp["concurrent_operations"],
        )

    if "line_operations" in results_python:
        py_time = results_python["line_operations"]["mean"]
        cpp_time = results_cpp["line_operations"]["mean"]
        speedup = py_time / cpp_time
        print("\nLine Operations:")
        print(f"{'Benchmark':<20} {'Python (ms)':<14} {'C++23 (ms)':<14} {'Speedup':<12}")
        print(f"{'-' * 62}")
        speedup_str = (
            f"✅ {speedup:.2f}x faster" if speedup >= 1 else f"❌ {1 / speedup:.2f}x slower"
        )
        print(f"{'1000 lines':<20} {py_time:<14.2f} {cpp_time:<14.2f} {speedup_str:<12}")

    if "seek_operations" in results_python:
        py_time = results_python["seek_operations"]["mean"]
        cpp_time = results_cpp["seek_operations"]["mean"]
        speedup = py_time / cpp_time
        print("\nSeek Operations:")
        print(f"{'Benchmark':<20} {'Python (ms)':<14} {'C++23 (ms)':<14} {'Speedup':<12}")
        print(f"{'-' * 62}")
        speedup_str = (
            f"✅ {speedup:.2f}x faster" if speedup >= 1 else f"❌ {1 / speedup:.2f}x slower"
        )
        print(f"{'seek+tell+read':<20} {py_time:<14.2f} {cpp_time:<14.2f} {speedup_str:<12}")


def main():
    """Main entry point."""
    print_header("🚀 Benchmark Both Implementations")

    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print("Timer: time.perf_counter_ns()\n")

    bench_dir = Path(__file__).parent
    venv_python = bench_dir / ".venv_python"
    venv_cpp = bench_dir / ".venv_cpp"

    print_header("📦 Setting Up Environments")

    python_bin = setup_venv(venv_python, "aiofiles==25.1.0", is_editable=False)
    cpp_bin = setup_venv(venv_cpp, "aiofiles-x", is_editable=True)

    print("Creating benchmark script...")
    script_path = create_isolated_benchmark_script()

    try:
        print_header("⚡ Running Benchmarks")

        print("Running aiofiles (Pure Python)...")
        code, stdout, stderr = run_in_subprocess(str(python_bin), str(script_path))
        if code != 0:
            print(f"❌ Error: {stderr}")
            return 1
        print(stdout)

        print("Running aiofiles-x (C++23)...")
        code, stdout, stderr = run_in_subprocess(str(cpp_bin), str(script_path))
        if code != 0:
            print(f"❌ Error: {stderr}")
            return 1
        print(stdout)

        results_python_path = bench_dir / "results_aiofiles.json"
        results_cpp_path = bench_dir / "results_aiofiles-x.json"

        with open(results_python_path) as f:
            results_python = json.load(f)

        with open(results_cpp_path) as f:
            results_cpp = json.load(f)

        print_comparison(results_python, results_cpp)

        combined = {
            "aiofiles": results_python,
            "aiofiles-x": results_cpp,
            "metadata": {
                "platform": platform.system(),
                "python_version": sys.version.split()[0],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        }

        combined_path = bench_dir / "benchmark_comparison.json"
        with open(combined_path, "w") as f:
            json.dump(combined, f, indent=2)

        print(f"\n✅ Combined results saved to: {combined_path}")

    finally:
        script_path.unlink()

    return 0


if __name__ == "__main__":
    sys.exit(main())
