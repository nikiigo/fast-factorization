import argparse
import platform
import statistics
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


try:
    from sympy import factorint
except ImportError:
    factorint = None

import fast_factorization


CASES = (
    ("small semiprime", 91),
    ("small trial factor", 101 * 1_000_003),
    ("close semiprime", 100_000_073 * 100_000_081),
    ("Project Euler 3", 600_851_475_143),
    ("p-1 friendly", 10_009 * 1_000_000_007),
    ("rho semiprime", 1_000_003 * 1_000_000_007),
    ("perfect square", 99_991 * 99_991),
    ("prime input", 104_729),
    ("big close semiprime", (10**50 + 151) * (10**50 + 447)),
)

STRATEGIES = (
    ("single process", "fast-factorization", lambda number: fast_factorization.factorize(number)),
    (
        'processes=4, strategy="rho"',
        'fast-factorization `processes=4`',
        lambda number: fast_factorization.factorize(number, processes=4),
    ),
    (
        'processes=4, strategy="methods"',
        'fast-factorization `strategy=methods`',
        lambda number: fast_factorization.factorize(number, processes=4, strategy="methods"),
    ),
)

README_START = "## Performance Comparison"
README_END = "## Practice Numbers"


def _package_version(package: str):
    try:
        return version(package)
    except PackageNotFoundError:
        return "not installed"


def _cpu_name():
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or platform.machine()


def _flatten_factorint(result):
    factors = []
    for factor, exponent in result.items():
        factors.extend([int(factor)] * int(exponent))
    return tuple(sorted(factors))


def _median_time(function, number: int, repeats: int):
    timings = []
    last_result = None
    for _ in range(repeats):
        started_at = time.perf_counter()
        last_result = function(number)
        timings.append(time.perf_counter() - started_at)
    return statistics.median(timings), last_result


def _comparison_label(fast_elapsed: float, sympy_elapsed: float):
    if sympy_elapsed == 0:
        return "same"
    ratio = fast_elapsed / sympy_elapsed
    if 0.8 <= ratio <= 1.25:
        return "about equal"
    if ratio < 0.8:
        return "fast-factorization faster"
    if ratio >= 10:
        return "SymPy much faster"
    return "SymPy faster"


def run_comparison(repeats: int):
    if factorint is None:
        raise RuntimeError("SymPy is required: python -m pip install sympy")

    results = []
    for title, column_name, fast_function in STRATEGIES:
        rows = []
        for case_name, number in CASES:
            fast_elapsed, fast_result = _median_time(fast_function, number, repeats)
            sympy_elapsed, sympy_result = _median_time(factorint, number, repeats)
            if fast_result != _flatten_factorint(sympy_result):
                raise AssertionError(f"factor mismatch for {case_name}: {fast_result} != {sympy_result}")
            rows.append(
                {
                    "case": case_name,
                    "fast_ms": fast_elapsed * 1000,
                    "sympy_ms": sympy_elapsed * 1000,
                    "result": _comparison_label(fast_elapsed, sympy_elapsed),
                }
            )
        results.append({"title": title, "column_name": column_name, "rows": rows})
    return results


def _format_table(column_name: str, rows):
    lines = [
        f"| Case | {column_name} | SymPy `factorint` | Result |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['fast_ms']:.4f} ms | "
            f"{row['sympy_ms']:.4f} ms | {row['result']} |"
        )
    return "\n".join(lines)


def render_markdown(results, repeats: int):
    python_version = platform.python_version()
    machine = platform.machine()
    system = platform.system()
    cpu = _cpu_name()
    sympy_version = _package_version("sympy")
    gmpy2_version = _package_version("gmpy2")

    lines = [
        README_START,
        "",
        "The table below compares the current `fast-factorization` checkout with",
        f"SymPy `factorint` from `sympy=={sympy_version}`. Times are medians of",
        f"{repeats} runs on Python {python_version}, {system} {machine}, {cpu}.",
        "Lower is better. These are local benchmark results, not general",
        "performance guarantees.",
        "",
        f"Optional `gmpy2` backend: `{gmpy2_version}`.",
        "",
    ]

    for index, result in enumerate(results):
        if index == 0:
            lines.append("Single-process factorization:")
        else:
            lines.append(f"With `{result['title']}`:")
        lines.extend(("", _format_table(result["column_name"], result["rows"]), ""))

    lines.extend(
        [
            "This package is competitive on simple educational cases such as small factors,",
            "perfect squares, and prime screening. SymPy is much stronger for general-purpose",
            "integer factorization, especially Pollard-heavy cases. For small examples,",
            "multiprocessing startup overhead can dominate the actual factorization work.",
            "The `methods` strategy is experimental and is intended only for harder searches",
            "where Fermat, Pollard p-1, and Pollard Rho each have enough work to justify",
            "running in separate worker processes.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def replace_readme_section(readme_text: str, section_markdown: str):
    start = readme_text.index(README_START)
    end = readme_text.index(README_END, start)
    return f"{readme_text[:start]}{section_markdown}\n{readme_text[end:]}"


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Compare fast-factorization performance with SymPy factorint.",
    )
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--update-readme", action="store_true")
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    return parser.parse_args()


def main():
    args = _parse_args()
    if args.repeats < 1:
        print("--repeats must be greater than 0", file=sys.stderr)
        return 2

    try:
        results = run_comparison(args.repeats)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 2

    markdown = render_markdown(results, args.repeats)
    if args.update_readme:
        original = args.readme.read_text(encoding="utf-8")
        updated = replace_readme_section(original, markdown)
        args.readme.write_text(updated, encoding="utf-8")
        print(f"Updated {args.readme}")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
