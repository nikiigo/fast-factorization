import argparse
import importlib
import shlex
import shutil
import subprocess
import time

from fast_factorization import challenge_numbers

factorize = importlib.import_module("fast_factorization.factorize")


CASES = {
    "small semiprime": 91,
    "small trial factor": 101 * 1_000_003,
    "close semiprime": 100_000_073 * 100_000_081,
    "euler 3": challenge_numbers.PROJECT_EULER_3,
    "p-1 friendly": challenge_numbers.PM1_FRIENDLY_SEMIPRIME,
    "rho semiprime": challenge_numbers.PRACTICAL_RHO_SEMIPRIME,
    "perfect square": 99_991 * 99_991,
    "prime input": 104_729,
}

BIG_CASES = {
    "big close": challenge_numbers.BIG_CLOSE_SEMIPRIME,
}


def _parse_args():
    parser = argparse.ArgumentParser(description="Run factorization benchmarks.")
    parser.add_argument(
        "--include-big",
        action="store_true",
        help="include a larger synthetic close-prime semiprime",
    )
    parser.add_argument(
        "--show-rsa-100",
        action="store_true",
        help="print RSA-100 reference metadata without attempting factorization",
    )
    parser.add_argument(
        "--external",
        choices=("cado-nfs", "yafu"),
        help="run RSA-100 with an installed external factoring tool",
    )
    parser.add_argument(
        "--external-command",
        help="explicit command or path for the external factoring tool",
    )
    parser.add_argument(
        "--external-timeout",
        type=int,
        default=3600,
        help="timeout in seconds for an external RSA-100 run",
    )
    return parser.parse_args()


def _find_external_command(tool: str, explicit_command: str | None = None):
    if explicit_command:
        return shlex.split(explicit_command)
    candidates = (tool,)
    if tool == "cado-nfs":
        candidates = ("cado-nfs", "cado-nfs.py")
    for candidate in candidates:
        executable = shutil.which(candidate)
        if executable is not None:
            return [executable]
    return None


def _run_external_tool(tool: str, timeout: int, explicit_command: str | None = None):
    executable_command = _find_external_command(tool, explicit_command)
    if executable_command is None:
        print()
        print(f"{tool} is not installed or not on PATH")
        if tool == "cado-nfs":
            print("Tried: cado-nfs, cado-nfs.py")
        return

    command = [*executable_command, str(challenge_numbers.RSA_100)]
    if tool == "cado-nfs":
        command = [*executable_command, "-t", "all", str(challenge_numbers.RSA_100)]
    elif tool == "yafu":
        command = [*executable_command, f"factor({challenge_numbers.RSA_100})"]

    print()
    print(f"Running external RSA-100 benchmark: {' '.join(command)}")
    started_at = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"{tool} timed out after {timeout}s")
        return

    elapsed = time.perf_counter() - started_at
    print(f"{tool} exited with {completed.returncode} in {elapsed:.3f}s")
    if completed.stdout:
        print(completed.stdout[-2000:])
    if completed.stderr:
        print(completed.stderr[-2000:])


def main():
    args = _parse_args()
    cases = CASES.copy()
    if args.include_big:
        cases.update(BIG_CASES)

    for name, number in cases.items():
        started_at = time.perf_counter()
        result = factorize.factorize(number)
        elapsed = time.perf_counter() - started_at
        print(f"{name:18} {elapsed:.6f}s {result}")

    if args.show_rsa_100:
        left, right = challenge_numbers.RSA_100_FACTORS
        print()
        print("RSA-100 reference")
        print(f"digits: {len(str(challenge_numbers.RSA_100))}")
        print(f"known factors multiply correctly: {left * right == challenge_numbers.RSA_100}")
        print("not attempted by this benchmark")

    if args.external:
        _run_external_tool(args.external, args.external_timeout, args.external_command)


if __name__ == "__main__":
    main()
