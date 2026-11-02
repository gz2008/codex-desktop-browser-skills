import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def win_to_wsl(path):
    path = os.path.abspath(path)
    drive, rest = os.path.splitdrive(path)
    rest = rest.replace("\\", "/")
    return "/mnt/{}{}".format(drive[0].lower(), rest)


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def normalize(data):
    return data.replace(b"\r\n", b"\n")


def show(data, limit=1200):
    text = normalize(data).decode("utf-8", errors="replace")
    if len(text) > limit:
        text = text[:limit] + "\n...[truncated]"
    return repr(text)


def first_difference(expected, actual):
    limit = min(len(expected), len(actual))
    for i in range(limit):
        if expected[i] != actual[i]:
            return i
    if len(expected) != len(actual):
        return limit
    return None


def main():
    parser = argparse.ArgumentParser(description="Compile and byte-compare a C assignment.")
    parser.add_argument("--src", required=True, help="C source file")
    parser.add_argument("--input", help="stdin fixture")
    parser.add_argument("--expect", help="expected stdout fixture")
    parser.add_argument("--timeout", type=int, default=10, help="program timeout in seconds")
    parser.add_argument("--distro", help="WSL distro; defaults to the WSL default")
    parser.add_argument("--user", help="WSL user; defaults to the distro default")
    parser.add_argument("--no-werror", action="store_true", help="do not treat warnings as errors")
    parser.add_argument("--keep", action="store_true", help="keep the temp build directory")
    args = parser.parse_args()

    src = os.path.abspath(args.src)
    if not os.path.isfile(src):
        print("source not found: {}".format(src))
        return 2

    base = os.path.join(tempfile.gettempdir(), "codex-cverify")
    os.makedirs(base, exist_ok=True)
    work = os.path.join(base, uuid.uuid4().hex[:10])
    os.makedirs(work, exist_ok=True)

    try:
        shutil.copyfile(src, os.path.join(work, "main.c"))
        stdin_bytes = b""
        has_input_file = False
        if args.input:
            shutil.copyfile(args.input, os.path.join(work, "input.txt"))
            has_input_file = True
        if args.expect:
            shutil.copyfile(args.expect, os.path.join(work, "expected.txt"))

        wsl_dir = win_to_wsl(work)
        flags = "-std=c11 -Wall -Wextra -O0"
        if not args.no_werror:
            flags += " -Werror"
        command = "cd '{}' && gcc {} -o main main.c".format(wsl_dir, flags)
        command += " && ./main < input.txt" if has_input_file else " && ./main"

        try:
            wsl_command = ["wsl.exe"]
            if args.distro:
                wsl_command.extend(["-d", args.distro])
            if args.user:
                wsl_command.extend(["-u", args.user])
            wsl_command.extend(["--", "bash", "-lc", command])

            proc = subprocess.run(
                wsl_command,
                input=stdin_bytes,
                capture_output=True,
                timeout=args.timeout + 10,
            )
        except FileNotFoundError:
            print("wsl.exe not found; install WSL or compile manually")
            return 2
        except subprocess.TimeoutExpired:
            print("compilation or run timed out after {}s".format(args.timeout + 10))
            return 1

        stderr = proc.stderr.decode("utf-8", errors="replace")
        stdout = proc.stdout

        print("exit code: {}".format(proc.returncode))
        if stderr.strip():
            print("compiler/runtime stderr:")
            print(stderr.rstrip())

        if proc.returncode != 0:
            return 1

        print("actual stdout: {}".format(show(stdout)))

        if not args.expect:
            print("no --expect fixture; only compilation and execution were verified")
            return 0

        expected = normalize(read_bytes(os.path.join(work, "expected.txt")))
        actual = normalize(stdout)
        diff = first_difference(expected, actual)
        if diff is None:
            print("MATCH: byte-for-byte identical after CRLF normalization")
            return 0

        print("MISMATCH at byte {}".format(diff))
        print("expected: {}".format(show(expected)))
        print("actual:   {}".format(show(actual)))
        start = max(0, diff - 20)
        print("expected context: {}".format(repr(expected[start:diff + 20].decode("utf-8", errors="replace"))))
        print("actual context:   {}".format(repr(actual[start:diff + 20].decode("utf-8", errors="replace"))))
        return 1
    finally:
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)
        else:
            print("kept: {}".format(work))


if __name__ == "__main__":
    sys.exit(main())
