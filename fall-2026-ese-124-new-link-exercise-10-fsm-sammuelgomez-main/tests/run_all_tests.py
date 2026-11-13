#!/usr/bin/env python3
"""
ESE 124 - lab autograder (friendly "easy pass" version)

  python3 tests/run_all_tests.py             -> run everything, show your score
  python3 tests/run_all_tests.py q2          -> run only the Q2 tests
  python3 tests/run_all_tests.py q6_memory   -> run one test (used by GitHub Actions)
  python3 tests/run_all_tests.py --list      -> list every test and its points

The checks are forgiving: UPPER/lower case and extra spaces do not matter,
and extra lines you print (debug messages) are ignored.
Only the lines listed in the handout / expected_output.txt are checked.
"""
import os, re, subprocess, sys, tempfile, shutil

LAB = "Exercise 10"          # <- LAB-SPECIFIC: shown in the report header

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "tests", ".build")
DEBUG = os.path.join(ROOT, "tests", "debug")
REPORT = os.path.join(ROOT, "tests", "last_report.txt")
WINDOWS = os.name == "nt"
LINUX = sys.platform.startswith("linux")
EXE = ".exe" if WINDOWS else ""
PY = "py" if WINDOWS else "python3"

def find_compiler():
    if os.environ.get("CC"):
        return os.environ["CC"]
    for cc in ("gcc", "clang", "cc"):
        if shutil.which(cc):
            return cc
    return None

CC = find_compiler()
CFLAGS = ["-Wall", "-Wextra", "-std=c11"]
SANFLAGS = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"]
TIMEOUT = 5

# ============================================================================
# LAB-SPECIFIC (1/4): test data. Given data = the starter's .txt files; add a
# SECOND, different input per question so hard-coded answers fail.
# ============================================================================
COINS = "N D\nD D\nQ N C\nN N N\nD x N\nD\n"
COINS2 = "DNDNN\nCCQQ\nDDDD n D N C\nNNC\nND?DD\nN"            # lower-case n and ? are ignored; ends in S5

MESSAGES = "that lab was hard frfr\nfrfrfr no cap\n\nBroBot said FRFRFRFR\nfor real for real\nFrFr fRfR\nfrffrfr\n"
MESSAGES2 = ("fr fr\r\nFRFRFRFRFR\r\nffffrfrrrr\r\nfrfr!frfr...frfr\r\nFRFRFRFRFR again\r\nFRF RFR\r\nxfrfrx")  # tie: msg 2 and 5

ACCOUNTS = "3\nAlice 1234 500.00\nBro 2024 80.00\nChen 1111 0.00\n"
SESSION = ("PIN 1234\nCARD Alice\nPIN 1111\nPIN 1234\nBALANCE\nWITHDRAW 120\nWITHDRAW 900\nEJECT\nCARD Dave\n"
           "CARD Bro\nBALANCE\nPIN 2024\nWITHDRAW 0\nWITHDRAW 80\nBALANCE\nEJECT\nEJECT\n")
ACCOUNTS2 = "4\nWolf 7 1000.25\nSky 100 0.75\nRay 55 300\nZed 8 12.5\n"
SESSION2 = ("CARD Sky\nPIN 100\nWITHDRAW 0.75\nWITHDRAW 0.01\nBALANCE\nEJECT\n\nCARD Ray\nPIN 56\nPIN 55\n"
            "WITHDRAW 300.01\nWITHDRAW 299.5\nWITHDRAW abc\ncard Ray\nEJECT\nCARD Zed\nPIN 1\nEJECT\nCARD\nCARD Wolf\nPIN\nPIN x7\nPIN 7\n"
            "WITHDRAW -5\nBALANCE\n")                                     # ends with the card still in (READY)

KEYPAD = "0110110\n01100110\n0111 0110\n\n1101101100110\n01#10110\n1111\n"
KEYPAD2 = "0110\r\nx\r\n00110\r\n011001100110\r\n0110a0110b0110\r\n0110110110\r\n0"

CODE = """/* BroBot speed check */
#include <stdio.h>

int main(void) {
    int laps = 12;      /* laps today */
    int avg = laps / 4; /* integer division */
    /* a comment
       on two lines */
    printf("%d\\n", avg * 2); /** done **/
    return 0;
}
"""
CODE2 = ("x = a / b;\ny = 8/4/2; /**/ z = 1;\n/* ** stars ** */w = 2;\n/*/ still a comment */v = 3;\n"
         "p = *q / *r; //* c */ d\nm = n /\nk = 0;/ ")                     # ends with '/' + ' ', no final \n
CODE_OPEN = "int a = 1; /* this comment\nnever ends ** /\nint b = 2;\n"
CODE_SLASH_END = "a = b /"                                                  # text ends right after '/'

# ============================================================================
# LAB-SPECIFIC (2/4): Python reference answers, written independently of the C key.
# ============================================================================
def lines_of(text):
    return [l.rstrip("\r") for l in text.split("\n")]

def ref_vending(text):
    cents, step, out = 0, 0, []
    vends = change = refund = 0
    for c in text:
        if c not in "NDQC":
            continue
        step += 1
        old = cents
        if c == "Q":
            act = "REJECT"
        elif c == "C":
            act = "REFUND" if cents else "WAIT"; refund += cents; cents = 0
        else:
            cents += 5 if c == "N" else 10
            if cents < 15:
                act = "WAIT"
            elif cents == 15:
                act = "VEND"; vends += 1; cents = 0
            else:
                act = "VEND_CHANGE"; vends += 1; change += cents - 15; cents = 0
        out.append(f"STEP {step}: S{old} --{c}/{act}--> S{cents}")
    return out, [("VENDS", vends), ("CHANGE_CENTS", change), ("REFUND_CENTS", refund), ("FINAL", f"S{cents}")]

def ref_frfr(text):
    out, counts = [], []
    for l in lines_of(text):
        if l == "":
            continue
        n = len(re.findall(r"(?=frfr)", l.lower()))          # overlapping matches
        counts.append(n)
        out.append(f"MSG {len(counts)}: FRFR={n}")
    most = "NONE" if not counts or max(counts) == 0 else counts.index(max(counts)) + 1
    return out, [("MESSAGES", len(counts)), ("TOTAL", sum(counts)), ("MOST", most)]

def ref_atm(acc_text, sess_text):
    nums = acc_text.split()
    n = int(nums[0])
    acc = [[nums[1 + 3 * i], int(nums[2 + 3 * i]), float(nums[3 + 3 * i])] for i in range(n)]
    names = [a[0] for a in acc]
    state, cur, rej, k, out = "IDLE", None, 0, 0, []
    def num(s, conv):
        try:
            return conv(s)
        except ValueError:
            return None
    for raw in sess_text.split("\n"):
        line = raw.rstrip("\r")
        w = line.split()
        if not w:
            continue
        k += 1
        before, msg = state, "REJECTED"
        cmd, arg = w[0], (w[1] if len(w) > 1 else None)
        if state == "IDLE" and cmd == "CARD" and arg:
            if arg in names:
                cur, state, msg = names.index(arg), "WAIT_PIN", "INSERT PIN"
            else:
                msg = "NO SUCH ACCOUNT"
        elif state == "WAIT_PIN" and cmd == "PIN" and arg and num(arg, int) is not None:
            if int(arg) == acc[cur][1]:
                state, msg = "READY", "PIN OK"
            else:
                msg = "WRONG PIN"
        elif state in ("WAIT_PIN", "READY") and cmd == "EJECT" and arg is None:
            state, msg = "IDLE", "CARD RETURNED"
        elif state == "READY" and cmd == "BALANCE" and arg is None:
            msg = f"BALANCE {acc[cur][2]:.2f}"
        elif state == "READY" and cmd == "WITHDRAW" and arg and num(arg, float) is not None:
            a = float(arg)
            if a <= 0:
                msg = "INVALID AMOUNT"
            elif a > acc[cur][2]:
                msg = "INSUFFICIENT FUNDS"
            else:
                acc[cur][2] -= a; msg = f"CASH {a:.2f}"
        if msg == "REJECTED":
            rej += 1
        out.append(f"EVENT {k}: {line} | {before} -> {state} | {msg}")
    final = [f"ACCOUNT {a[0]} {a[2]:.2f}" for a in acc]
    return out, [("FINAL", state), ("REJECTED", rej)], final

LOCK_NAMES = ["SX", "S0", "S01", "S011"]

def ref_lock(text, pattern="0110"):
    """Mealy: state = the longest ending of the keys (since the last wrong key) that starts 0110 (0..3 keys).
    Output 1 on the key that completes 0110; then keep the longest ending of 0110 that starts it again ("0")."""
    out, total, k = [], 0, 0
    for l in lines_of(text):
        if l == "":
            continue
        k += 1
        typed, trace, u = "", ["SX"], ""
        for c in l[:60]:
            o = "0"
            if c not in "01":
                typed = ""
            else:
                typed += c
                m = max(j for j in range(len(pattern) + 1) if typed.endswith(pattern[:j]))
                if m == len(pattern):
                    o = "1"
                    m = max(j for j in range(len(pattern)) if pattern.endswith(pattern[:j]) and j < len(pattern))
                typed = pattern[:m]
            trace.append(LOCK_NAMES[len(typed)])
            u += o
        out.append(f"TRACE {k}: " + " ".join(trace))
        out.append(f"LOG {k}: OUT={u} OPENS={u.count('1')}")
        total += u.count("1")
    return out, [("LOGS", k), ("TOTAL_OPENS", total)]

def ref_strip(src):
    """Remove every /* ... */ (it becomes one space). No strings, no // comments."""
    out, i, n, comments, unclosed = [], 0, len(src), 0, False
    while i < n:
        if src[i:i + 2] == "/*":
            comments += 1
            j = src.find("*/", i + 2)
            if j < 0:
                unclosed = True
                break
            out.append(" ")
            i = j + 2
        else:
            out.append(src[i]); i += 1
    return "".join(out), [("COMMENTS", comments), ("UNCLOSED", "YES" if unclosed else "NO"), ("AGREE", "YES")]


# ---- RANDOM inputs: a new one on every run, checked with the Python answers above,
#      so a program that only prints the sample answers can never pass. ----
import random
RNG = random.Random()

def rand_coins():
    return "".join(RNG.choice("NNDDQCC xn\n") for _ in range(RNG.randint(15, 30)))

def rand_messages():
    parts = ["fr", "FR", "Fr", "fR", "f", "r", "F", "R", "x", " ", "!", "frfr"]
    lines = ["".join(RNG.choice(parts) for _ in range(RNG.randint(1, 12))) for _ in range(RNG.randint(3, 6))]
    return "\n".join(lines) + "\n"

def rand_session():
    names, pins = ["Wolf", "Sky", "Ray", "Zed", "Nobody"], ["7", "100", "55", "8", "1", "x"]
    cmds = []
    for _ in range(RNG.randint(12, 22)):
        cmds.append(RNG.choice(["CARD " + RNG.choice(names), "PIN " + RNG.choice(pins), "BALANCE", "EJECT",
                                "WITHDRAW " + RNG.choice(["0", "-3", "0.5", "12.5", "300", "2000", "abc"]),
                                "card Sky", "HELLO", "PIN " + RNG.choice(pins), "CARD " + RNG.choice(names)]))
    return "\n".join(cmds) + "\n"

def rand_keypad():
    lines = ["".join(RNG.choice("0011100x ") for _ in range(RNG.randint(3, 25))) for _ in range(RNG.randint(3, 6))]
    return "\n".join(lines) + "\n"

def rand_code():
    parts = ["a", "b", " ", "=", "1;", "\n", "/", "*", "/*", "*/", "/* c */", "8/4", "**", "//"]
    return "".join(RNG.choice(parts) for _ in range(RNG.randint(10, 40)))

def random_round(label, fn, *inputs):
    reset_ctx()
    CTX["expected"].append((True, f"(a NEW random {label} - different on every run)"))
    fn(*inputs)

# ============================================================================
# ENGINE - keep as is (only QUESTIONS below is lab-specific)
# ============================================================================
# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
class Fail(Exception):
    pass

# What the current test gave the program and what it expected. Printed on FAIL
# (or always with -v) so you can see exactly what was asked.
CTX = {}

def reset_ctx():
    CTX.clear()
    CTX.update(inputs=[], expected=[], output=None, files_out={}, hint="")


# LAB-SPECIFIC (3/4): folder / program / module / functions
# Each question is a small project: main.c + <module>.h + <module>.c + Makefile (all given except the TODOs)
QUESTIONS = {
    "q1": dict(folder="q1_vending",  prog="vending",   mod="vending", funcs=["column_of", "vend_step"]),
    "q2": dict(folder="q2_frfr",     prog="frfr",      mod="frfr",    funcs=["frfr_step", "count_frfr"]),
    "q3": dict(folder="q3_brobank",  prog="atm",       mod="atm",     funcs=["atm_step"]),
    "q4": dict(folder="q4_lock",     prog="lock",      mod="lock",    funcs=["column_of", "lock_step"]),
    "q5": dict(folder="q5_comments", prog="nocomment", mod="strip",   funcs=["next_switch", "next_by_table"]),
}

_built = {}

def can_sanitize():
    """AddressSanitizer + leak checks run on Linux (that is: on GitHub)."""
    if not LINUX or CC is None:
        return False
    if "san" not in _built:
        tmp = tempfile.mkdtemp(prefix="labsan_")
        try:
            src = os.path.join(tmp, "t.c")
            with open(src, "w") as f:
                f.write("int main(void){return 0;}\n")
            r = subprocess.run([CC, *SANFLAGS, src, "-o", os.path.join(tmp, "t")], capture_output=True)
            _built["san"] = r.returncode == 0
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return _built["san"]

def build(q, sanitize=False):
    """Compile every .c file in the question folder (works even if your Makefile is not done yet)."""
    key = (q, sanitize)
    if key in _built:
        return _built[key]
    info = QUESTIONS[q]
    folder = os.path.join(ROOT, info["folder"])
    srcs = sorted(f for f in os.listdir(folder) if f.endswith(".c")) if os.path.isdir(folder) else []
    if not srcs:
        raise Fail(f"No .c files found in {info['folder']}{os.sep}")
    if CC is None:
        raise Fail("No C compiler found (gcc).\n"
                   "Windows: install MinGW-w64 (e.g. from https://winlibs.com or MSYS2) and add its bin\n"
                   "folder to PATH, then open a NEW terminal and type: gcc --version\n"
                   "Mac: run  xcode-select --install   Linux: sudo apt install gcc")
    os.makedirs(BUILD, exist_ok=True)
    exe = os.path.join(BUILD, info["prog"] + ("_memcheck" if sanitize else "") + EXE)
    flags = CFLAGS + (SANFLAGS if sanitize else [])
    r = subprocess.run([CC, *flags, *srcs, "-o", exe], cwd=folder, capture_output=True, text=True)
    if r.returncode != 0:
        raise Fail(f"Your {info['folder']} code does not compile ( gcc {' '.join(srcs)} ).\n"
                   "Missing prototype in the .h file? Missing #include? First error(s):\n" + r.stderr[-1500:])
    _built[key] = exe
    return exe

SAN_ERRORS = ("ERROR: AddressSanitizer", "ERROR: LeakSanitizer", "runtime error:")

def run(q, files=None, sanitize=False):
    """Run the question's program in a fresh folder that contains `files`."""
    exe = build(q, sanitize)
    files = files or {}
    CTX["program"] = os.path.basename(exe).replace(EXE, "") if EXE else os.path.basename(exe)
    for name, content in files.items():
        CTX["inputs"].append((f"input file {name}", content))
    tmp = tempfile.mkdtemp(prefix="lab_")
    env = dict(os.environ)
    if sanitize:
        env["ASAN_OPTIONS"] = "detect_leaks=1:exitcode=23"
        env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1:exitcode=23"
    try:
        for name, content in files.items():
            with open(os.path.join(tmp, name), "w", newline="\n") as f:
                f.write(content)
        def go():
            return subprocess.run([exe], cwd=tmp, input="", capture_output=True, env=env,
                                  text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT * (4 if sanitize else 1))
        try:
            r = go()
            if sanitize and "LeakSanitizer has encountered a fatal error" in r.stderr:
                env["ASAN_OPTIONS"] = "detect_leaks=0:exitcode=23"   # leak checker unavailable here
                r = go()
        except subprocess.TimeoutExpired:
            raise Fail("Program took too long (infinite loop? waiting for input that never comes?)")
        out = r.stdout + r.stderr
        CTX["output"] = out
        produced = {}
        for name in os.listdir(tmp):
            if name not in files:
                with open(os.path.join(tmp, name), encoding="utf-8", errors="replace") as f:
                    produced[name] = f.read()
        CTX["files_out"] = produced
        return out, r.returncode, produced
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def norm(s):
    return s.upper()

def get_value(out, key):
    """Find KEY=value (case/space-insensitive). Returns the LAST match or None."""
    k = r"\s+".join(re.escape(p) for p in key.upper().split())
    m = re.findall(r"(?<![A-Z_])" + k + r"\s*=\s*([^\s]+)", norm(out))
    return m[-1].replace(" ", "") if m else None

def fmt(v):
    return f"{v:.2f}" if isinstance(v, float) else str(v)

def same(got, want):
    if got is None:
        return False
    if isinstance(want, float):
        try:
            return abs(float(got) - want) < 0.011
        except ValueError:
            return False
    return got == str(want).upper().replace(" ", "")

def check_values(out, pairs):
    """pairs = [(KEY, value), ...]; every KEY=value line must appear in the output."""
    bad = False
    for key, want in pairs:
        got = get_value(out, key)
        ok = same(got, want)
        bad |= not ok
        note = "" if ok else ("   <- not found in your output" if got is None else f"   <- you printed {key}={got}")
        CTX["expected"].append((ok, f"{key}={fmt(want)}{note}"))
    if bad:
        raise Fail("Some expected lines are missing or have the wrong value (see EXPECTED).")

def nline(s):
    """Normalize one line: UPPER case, no spaces around = : , and single spaces."""
    s = s.upper()
    s = re.sub(r"\s*([=:,+])\s*", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()

def check_out_lines(out, wants, where="your output"):
    """Every wanted line must appear (case/space-insensitive) as one line, or as the end of one."""
    have = [nline(l) for l in out.split("\n")]
    bad = False
    for w in wants:
        nw = nline(w)
        ok = any(h == nw or h.endswith(" " + nw) for h in have)
        bad |= not ok
        CTX["expected"].append((ok, w + ("" if ok else "   <- not found")))
    if bad:
        raise Fail(f"Some expected lines are missing from {where} (see EXPECTED).")

def check_word(text, word, must_have=True):
    ok = (word.upper() in norm(text)) == must_have
    CTX["expected"].append((ok, (f"a line containing '{word}'" if must_have else f"NO line containing '{word}'")
                                + ("" if ok else "   <- wrong")))
    if not ok:
        raise Fail("Unexpected output (see EXPECTED).")

def box(title, text, n=30):
    lines = text.rstrip("\n").split("\n") if text.strip() else ["(empty)"]
    s = f"      {title}:\n" + "\n".join("        | " + l for l in lines[:n])
    if len(lines) > n:
        s += "\n        | ..."
    return s

def report_details():
    parts = []
    for title, content in CTX.get("inputs", []):
        parts.append(box(title.replace("input file", "INPUT FILE"), content))
    if CTX.get("expected"):
        parts.append("      EXPECTED (extra lines in your output are OK; case and spaces do not matter):\n" +
                     "\n".join(f"        [{' OK ' if ok else 'FAIL'}] {line}" for ok, line in CTX["expected"]))
    if CTX.get("output") is not None:
        parts.append(box("YOUR PROGRAM PRINTED", CTX["output"], n=40))
    for name, content in CTX.get("files_out", {}).items():
        parts.append(box(f"YOUR PROGRAM WROTE {name}", content))
    if CTX.get("hint"):
        parts.append("      HINT: " + CTX["hint"])
    return "\n".join(parts)

def code_only(t):   # drop comments so TODO notes do not count
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)

def read_src(q, name):
    path = os.path.join(ROOT, QUESTIONS[q]["folder"], name)
    return open(path, encoding="utf-8", errors="replace").read() if os.path.exists(path) else None

# ============================================================================
# LAB-SPECIFIC (4/4): test functions + TESTS list (points must total 100)
#   check_values() for unique KEY=VALUE lines, check_out_lines() for repeated keys / message lines,
#   run_harness() calls your functions directly (it can also change one cell of your table).
# ============================================================================
def func_body(q, fname, mod_file):
    """The body of one function in your module (comments removed), or None."""
    src = read_src(q, mod_file)
    if src is None:
        return None
    t = code_only(src)
    m = re.search(r"\b" + fname + r"\s*\([^;{)]*\)\s*\{", t)
    if not m:
        return None
    depth, i = 0, m.end() - 1
    for j in range(i, len(t)):
        depth += t[j] == "{"
        depth -= t[j] == "}"
        if depth == 0:
            return t[i:j + 1]
    return t[i:]

def rule(ok, text):
    CTX["expected"].append((bool(ok), text + ("" if ok else "   <- no")))
    return bool(ok)

def way_rules(q, mod_file, switch_funcs=(), table_funcs=()):
    """switch_funcs must use switch; table_funcs must use NO switch and NO if (the table IS the machine)."""
    ok = True
    for f in switch_funcs:
        b = func_body(q, f, mod_file)
        ok &= rule(b is not None and re.search(r"\bswitch\s*\(", b), f"{f}() in {mod_file} uses switch (way 1)")
    for f in table_funcs:
        b = func_body(q, f, mod_file)
        ok &= rule(b is not None and not re.search(r"\b(switch|if)\s*\(", b) and "?" not in b,
                   f"{f}() in {mod_file} uses only the tables: no switch, no if, no ?: (way 2)")
    if not ok:
        raise Fail("This question must be solved the way the handout says (see EXPECTED).")

def run_harness(q, harness, unconst=()):
    """Build YOUR module (without main.c) with a small test main, then run it.
    unconst: table names whose 'const' is removed so the test can change a cell."""
    info = QUESTIONS[q]
    tmp = tempfile.mkdtemp(prefix="labunit_")
    try:
        work = os.path.join(tmp, info["folder"])
        shutil.copytree(os.path.join(ROOT, info["folder"]), work,
                        ignore=shutil.ignore_patterns(info["prog"], info["prog"] + ".exe", "*.o", "main.c"))
        for name in os.listdir(work):
            if name.endswith((".c", ".h")):
                p = os.path.join(work, name)
                src = open(p, encoding="utf-8", errors="replace").read()
                for t in unconst:
                    src = re.sub(r"\bconst\s+(\w+\s+" + t + r"\s*\[)", r"\1", src)
                with open(p, "w", newline="\n") as f:
                    f.write(src)
        with open(os.path.join(work, "unit_test_main.c"), "w", newline="\n") as f:
            f.write(harness)
        srcs = sorted(f for f in os.listdir(work) if f.endswith(".c"))
        exe = os.path.join(work, "unit" + EXE)
        r = subprocess.run([CC, *CFLAGS, *srcs, "-o", exe], cwd=work, capture_output=True, text=True)
        if r.returncode != 0:
            raise Fail("Your module does not compile with the test main (wrong function or table names?):\n"
                       + r.stderr[-1200:])
        try:
            p = subprocess.run([exe], cwd=work, input="", capture_output=True, text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            raise Fail("Program took too long (infinite loop?)")
        CTX["output"] = p.stdout + p.stderr
        bads = [l[4:].strip() for l in CTX["output"].split("\n") if l.startswith("BAD:")]
        for b in bads[:8]:
            CTX["expected"].append((False, b))
        ok = "ALL OK" in CTX["output"] and not bads
        CTX["expected"].append((ok, "every function check passes (ALL OK)"))
        if not ok:
            raise Fail("Calling your functions directly gave wrong answers (see EXPECTED).")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

HARNESS_HEAD = """#include <stdio.h>
static int bad = 0;
static void want(int ok, const char *what) { if (!ok) { bad = 1; printf("BAD: %s\\n", what); } }
"""

# Q1 ---------------------------------------------------------------------------
def vending_test(text):
    out, _, _ = run("q1", {"coins.txt": text})
    steps, totals = ref_vending(text)
    check_out_lines(out, steps)
    check_values(out, totals)

def t_q1_given():
    CTX["hint"] = ("Copy the handout's table into next_state and action_table (row = state, column = input). "
                   "vend_step: a = action_table[*s][col]; *s = next_state[*s][col]; return a;")
    vending_test(COINS)

def t_q1_second():
    CTX["hint"] = ("Only N D Q C (UPPER case) are inputs: column_of returns -1 for every other char. "
                   "Cancel in S0 is WAIT (nothing to give back).")
    vending_test(COINS2)
    random_round("coins.txt", vending_test, rand_coins())

Q1_HARNESS = HARNESS_HEAD + """#include "vending.h"
int main(void) {
    const int N[3][4] = {{S5, S10, S0, S0}, {S10, S0, S5, S0}, {S0, S0, S10, S0}};
    const int O[3][4] = {{WAIT, WAIT, REJECT, WAIT}, {WAIT, VEND, REJECT, REFUND}, {VEND, VEND_CHANGE, REJECT, REFUND}};
    const char *sn[3] = {"S0", "S5", "S10"}, *in[4] = {"NICKEL", "DIME", "QUARTER", "CANCEL"};
    const char *an[5] = {"WAIT", "VEND", "VEND_CHANGE", "REJECT", "REFUND"};
    char msg[160];
    for (int s = 0; s < 3; s++)
        for (int c = 0; c < 4; c++) {
            sprintf(msg, "next_state[%s][%s] should be %s", sn[s], in[c], sn[N[s][c]]);
            want(next_state[s][c] == (VState)N[s][c], msg);
            sprintf(msg, "action_table[%s][%s] should be %s", sn[s], in[c], an[O[s][c]]);
            want(action_table[s][c] == (Action)O[s][c], msg);
        }
    want(column_of('N') == NICKEL && column_of('D') == DIME && column_of('Q') == QUARTER && column_of('C') == CANCEL,
         "column_of: N D Q C -> NICKEL DIME QUARTER CANCEL");
    want(column_of('n') == -1 && column_of('x') == -1 && column_of(' ') == -1, "column_of: any other char -> -1");
    next_state[S0][NICKEL] = S10;          /* change one cell: vend_step must follow the tables */
    action_table[S0][NICKEL] = REJECT;
    VState t = S0;
    Action a = vend_step(&t, NICKEL);
    want(a == REJECT && t == S10, "vend_step must READ action_table[*s][col] and next_state[*s][col] (we changed a cell; it did not follow)");
    if (!bad) printf("ALL OK\\n");
    return 0;
}
"""

def t_q1_table():
    CTX["hint"] = "vend_step has no switch and no if - just the two look-ups. Every cell is checked."
    way_rules("q1", "vending.c", [], ["vend_step"])
    run_harness("q1", Q1_HARNESS, unconst=("next_state", "action_table"))

# Q2 ---------------------------------------------------------------------------
def frfr_test(text):
    out, _, _ = run("q2", {"messages.txt": text})
    msgs, totals = ref_frfr(text)
    check_out_lines(out, msgs)
    check_values(out, totals)

def t_q2_given():
    CTX["hint"] = ("The state = how much of F R F R you have. Use toupper. In S_FRF an R is a MATCH: "
                   "*found = 1 and go to S_FR (overlap!). An F can always start again (go to S_F).")
    frfr_test(MESSAGES)

def t_q2_second():
    CTX["hint"] = "FRFRFRFRFR has 4 (overlapping). A space breaks the pattern: 'fr fr' is 0."
    msgs, totals = ref_frfr(MESSAGES2)
    counts = [int(m.split("=")[1]) for m in msgs]
    assert counts.count(max(counts)) >= 2          # a real tie for MOST
    frfr_test(MESSAGES2)
    random_round("messages.txt", frfr_test, rand_messages())

Q2_HARNESS = HARNESS_HEAD + """#include "frfr.h"
int main(void) {
    int f = 7;
    want(count_frfr(NULL) == 0, "count_frfr(NULL) should be 0");
    want(count_frfr("") == 0, "count_frfr(\\"\\") should be 0");
    want(count_frfr("frFRfr") == 2, "count_frfr(\\"frFRfr\\") should be 2 (overlap, any case)");
    want(frfr_step(S_FRF, 'r', &f) == S_FR && f == 1, "frfr_step(S_FRF, 'r') -> S_FR with *found = 1");
    want(frfr_step(S_F, 'F', &f) == S_F && f == 0, "frfr_step(S_F, 'F') -> S_F with *found = 0");
    want(frfr_step(S_FR, 'r', &f) == S0 && f == 0, "frfr_step(S_FR, 'r') -> S0");
    if (!bad) printf("ALL OK\\n");
    return 0;
}
"""

def t_q2_switch():
    CTX["hint"] = "frfr_step uses switch (s). Do not use strstr or strncmp: the state machine does the matching."
    src = code_only(read_src("q2", "frfr.c") or "")
    if not rule(not re.search(r"\b(strstr|strncmp|strcasestr|strncasecmp)\b", src),
                "frfr.c does not use strstr / strncmp"):
        raise Fail("Use the state machine, not string search functions (see EXPECTED).")
    way_rules("q2", "frfr.c", ["frfr_step"])
    run_harness("q2", Q2_HARNESS)

# Q3 ---------------------------------------------------------------------------
def atm_test(acc, sess):
    out, _, _ = run("q3", {"accounts.txt": acc, "session.txt": sess})
    events, totals, final = ref_atm(acc, sess)
    check_out_lines(out, events + final)
    check_values(out, totals)

def t_q3_given():
    CTX["hint"] = ("switch (m->state) FIRST, then check the command with if / else if. Start with "
                   "strcpy(msg, \"REJECTED\") - every line that does not fit keeps that message and the state.")
    atm_test(ACCOUNTS, SESSION)

def t_q3_second():
    CTX["hint"] = ("'card Ray' (lower case), 'CARD' with no name, 'PIN x7' and 'WITHDRAW abc' are REJECTED. "
                   "Withdrawing the whole balance is allowed (only a > balance is too much).")
    atm_test(ACCOUNTS2, SESSION2)
    random_round("session.txt", atm_test, ACCOUNTS2, rand_session())

def t_q3_switch():
    CTX["hint"] = "atm_step must use switch (m->state) - one case for IDLE, WAIT_PIN and READY."
    way_rules("q3", "atm.c", ["atm_step"])
    b = func_body("q3", "atm_step", "atm.c") or ""
    if not all(rule(re.search(r"\bcase\s+" + s + r"\s*:", b), f"atm_step has case {s}:") for s in ("IDLE", "WAIT_PIN", "READY")):
        raise Fail("Every state needs its own case (see EXPECTED).")

# Q4 ---------------------------------------------------------------------------
def lock_test(text):
    out, _, _ = run("q4", {"keypad.txt": text})
    lines, totals = ref_lock(text)
    check_out_lines(out, lines)
    check_values(out, totals)

def t_q4_given():
    CTX["hint"] = ("Mealy, like Q1: out = out_table[*s][col] (OLD state) FIRST, then *s = next_state[*s][col]. "
                   "Only S011 + 0 outputs 1, and it goes to S0. The ERR column always goes to SX.")
    lock_test(KEYPAD)

def t_q4_second():
    CTX["hint"] = "After the door opens (S011 + 0) you are in S0: the last 0 can start a new 0110. Wrong keys -> SX."
    lock_test(KEYPAD2)
    random_round("keypad.txt", lock_test, rand_keypad())

Q4_HARNESS = HARNESS_HEAD + """#include "lock.h"
int main(void) {
    const int N[4][3] = {{S0, SX, SX}, {S0, S01, SX}, {S0, S011, SX}, {S0, SX, SX}};
    const int O[4][3] = {{0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {1, 0, 0}};
    const char *sn[4] = {"SX", "S0", "S01", "S011"}, *in[3] = {"IN0", "IN1", "ERR"};
    char msg[160];
    for (int s = 0; s < 4; s++)
        for (int c = 0; c < 3; c++) {
            sprintf(msg, "next_state[%s][%s] should be %s", sn[s], in[c], sn[N[s][c]]);
            want(next_state[s][c] == (LState)N[s][c], msg);
            sprintf(msg, "out_table[%s][%s] should be %d", sn[s], in[c], O[s][c]);
            want(out_table[s][c] == O[s][c], msg);
        }
    want(column_of('0') == IN0 && column_of('1') == IN1, "column_of: '0' -> IN0, '1' -> IN1");
    want(column_of('x') == ERR && column_of(' ') == ERR && column_of('2') == ERR, "column_of: any other char -> ERR");
    next_state[SX][IN1] = S011;             /* change two cells: lock_step must follow the tables */
    out_table[SX][IN1] = 1;
    LState t = SX;
    int u = lock_step(&t, IN1);
    want(t == S011 && u == 1, "lock_step must READ out_table[*s][col] and next_state[*s][col] (we changed a cell; it did not follow)");
    if (!bad) printf("ALL OK\\n");
    return 0;
}
"""

def t_q4_table():
    CTX["hint"] = "lock_step has no switch and no if: out = out_table[*s][col]; *s = next_state[*s][col]; return out;"
    way_rules("q4", "lock.c", [], ["lock_step"])
    run_harness("q4", Q4_HARNESS, unconst=("next_state", "out_table"))

# Q5 ---------------------------------------------------------------------------
def check_block(out, want):
    """The lines between ---- clean code ---- and ---- end ---- must be the clean code (end spaces ignored)."""
    m = re.search(r"---- clean code ----\n(.*?)---- end ----", out.replace("\r", ""), re.S)
    got = m.group(1) if m else None
    if got is None:
        CTX["expected"].append((False, "the lines ---- clean code ---- and ---- end ----   <- not found"))
        raise Fail("The clean code block is missing.")
    g = [l.rstrip() for l in got.rstrip("\n").split("\n")]
    w = [l.rstrip() for l in want.rstrip("\n").split("\n")]
    for i, line in enumerate(w):
        ok = i < len(g) and g[i] == line
        CTX["expected"].append((ok, f"clean line {i + 1}: {line!r}" + ("" if ok else
                                f"   <- yours: {g[i]!r}" if i < len(g) else "   <- missing")))
    if len(g) > len(w):
        CTX["expected"].append((False, f"{len(g) - len(w)} extra clean line(s)"))
    if g != w:
        raise Fail("The clean code is not right (spaces at the END of a line do not matter).")

def strip_test(text):
    out, _, _ = run("q5", {"code.txt": text})
    clean, totals = ref_strip(text)
    check_values(out, totals)
    check_block(out, clean)

def t_q5_given():
    CTX["hint"] = ("CODE + '/' -> SLASH (hold it). SLASH + '*' -> BLOCK (a comment starts), SLASH + other -> CODE and "
                   "write '/' + c (A_FLUSH). BLOCK + '*' -> STAR. STAR + '/' -> CODE and write one space.")
    strip_test(CODE)

def t_q5_second():
    CTX["hint"] = ("8/4/2 is division: every '/' must come back. '/**/' and '/*/ ... */' are comments. SLASH + '/' "
                   "stays in SLASH (write one '/'). An unclosed comment -> UNCLOSED=YES.")
    strip_test(CODE2)
    reset_ctx()
    strip_test(CODE_OPEN)
    reset_ctx()
    strip_test(CODE_SLASH_END)
    random_round("code.txt", strip_test, rand_code())

Q5_HARNESS = HARNESS_HEAD + """#include <string.h>
#include "strip.h"
int main(void) {
    const int N[4][3] = {{SLASH, CODE, CODE}, {SLASH, BLOCK, CODE}, {BLOCK, STAR, BLOCK}, {CODE, STAR, BLOCK}};
    const int O[4][3] = {{A_NONE, A_COPY, A_COPY}, {A_COPY, A_START, A_FLUSH}, {A_NONE, A_NONE, A_NONE},
                         {A_SPACE, A_NONE, A_NONE}};
    const char *sn[4] = {"CODE", "SLASH", "BLOCK", "STAR"}, *cn[3] = {"C_SLASH", "C_STAR", "C_OTHER"};
    const char *an[5] = {"A_NONE", "A_COPY", "A_FLUSH", "A_START", "A_SPACE"};
    char msg[200], dst[MAX_TEXT];
    for (int s = 0; s < 4; s++)
        for (int c = 0; c < 3; c++) {
            Action a = (Action)-1;
            SState n = next_switch((SState)s, (CharClass)c, &a);
            sprintf(msg, "next_switch(%s, %s) should go to %s with %s", sn[s], cn[c], sn[N[s][c]], an[O[s][c]]);
            want(n == (SState)N[s][c] && a == (Action)O[s][c], msg);
            sprintf(msg, "next_table[%s][%s] = %s and act_table[%s][%s] = %s", sn[s], cn[c], sn[N[s][c]], sn[s], cn[c], an[O[s][c]]);
            want(next_table[s][c] == (SState)N[s][c] && act_table[s][c] == (Action)O[s][c], msg);
            a = (Action)-1;
            n = next_by_table((SState)s, (CharClass)c, &a);
            sprintf(msg, "next_by_table(%s, %s) should go to %s with %s", sn[s], cn[c], sn[N[s][c]], an[O[s][c]]);
            want(n == (SState)N[s][c] && a == (Action)O[s][c], msg);
        }
    next_table[CODE][C_OTHER] = BLOCK;      /* change one cell: next_by_table must follow the tables */
    act_table[CODE][C_OTHER] = A_START;
    Action a;
    want(next_by_table(CODE, C_OTHER, &a) == BLOCK && a == A_START,
         "next_by_table must READ next_table[s][c] and act_table[s][c] (we changed a cell; it did not follow)");
    int k = -1;
    strip_text("ab", dst, 0, &k);
    want(k == 0 && strcmp(dst, "ab") == 0, "the switch way must not use the tables");
    if (!bad) printf("ALL OK\\n");
    return 0;
}
"""

def t_q5_ways():
    CTX["hint"] = ("Way 1: next_switch = switch (s) with an if per char class. Way 2: next_by_table = two look-ups. "
                   "Both must give the same arrow for all 12 (state, class) pairs.")
    way_rules("q5", "strip.c", ["next_switch"], ["next_by_table"])
    run_harness("q5", Q5_HARNESS, unconst=("next_table", "act_table"))

# ============================================================================
# ENGINE - organize / reflection tests (keep; they read QUESTIONS)
# ============================================================================
# organize: main.c + <mod>.h + <mod>.c + Makefile -----------------------------
def find_make():
    for m in ("make", "mingw32-make"):
        if shutil.which(m):
            return m
    return None

def organize_test(q):
    """Is the question organized as main.c + <mod>.h + <mod>.c + a working Makefile?"""
    info = QUESTIONS[q]
    folder = os.path.join(ROOT, info["folder"])
    mod, prog, f = info["mod"], info["prog"], info["folder"]
    CTX["hint"] = (f"Look at {QUESTIONS['q1']['folder']}/ for the pattern. In {f}/Makefile the line under each target must start "
                   f"with a TAB. Then run:  cd {f}   and   make")
    def item(ok, text):
        ok = bool(ok)
        CTX["expected"].append((ok, text))
        return ok
    h, c, m, mk = (read_src(q, n) for n in (mod + ".h", mod + ".c", "main.c", "Makefile"))
    ok = True
    hc = code_only(h) if h else ""
    ok &= item(h is not None and all(re.search(r"#\s*" + k, hc) for k in ("ifndef", "define", "endif")),
               f"{mod}.h has an include guard (#ifndef / #define / #endif)")
    missing = [fn for fn in info["funcs"] if not re.search(r"\b" + fn + r"\s*\([^;{]*\)\s*;", hc)]
    ok &= item(not missing, f"{mod}.h declares the prototypes: {', '.join(info['funcs'])}"
               + (f"   <- missing: {', '.join(missing)}" if missing else ""))
    ok &= item(c is not None and f'#include "{mod}.h"' in c and not re.search(r"\bmain\s*\(", code_only(c)),
               f'{mod}.c has #include "{mod}.h" and NO main()')
    ok &= item(m is not None and f'#include "{mod}.h"' in m and re.search(r"\bmain\s*\(", m),
               f'main.c has #include "{mod}.h" and main()')
    mkc = re.sub(r"#[^\n]*", "", mk or "")
    for target in (prog, "run", "clean"):
        ok &= item(bool(re.search(r"^" + re.escape(target) + r"\s*:", mkc, re.M)),
                   f"Makefile has a '{target}:' target")
    make = find_make()
    if make and mk is not None:
        tmp = tempfile.mkdtemp(prefix="labmk_")
        try:
            work = os.path.join(tmp, f)
            shutil.copytree(folder, work, ignore=shutil.ignore_patterns(prog, prog + ".exe", "*.o"))
            r = subprocess.run([make], cwd=work, capture_output=True, text=True, timeout=120)
            built = os.path.exists(os.path.join(work, prog)) or os.path.exists(os.path.join(work, prog + ".exe"))
            ok &= item(built, f"'make' builds the program {prog}" + ("" if built else
                       "   <- make said: " + (r.stderr or r.stdout).strip().split("\n")[-1][:150]))
            if built and not WINDOWS:
                subprocess.run([make, "clean"], cwd=work, capture_output=True, text=True, timeout=60)
                gone = not os.path.exists(os.path.join(work, prog))
                kept = all(os.path.exists(os.path.join(work, t)) for t in os.listdir(folder) if t.endswith(".txt"))
                ok &= item(gone and kept, "'make clean' removes the program and keeps the .txt files")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        item(True, "(make is not installed on this computer: the Makefile build is checked on GitHub)")
    if not ok:
        raise Fail(f"{f} is not organized as main.c + {mod}.h + {mod}.c + Makefile yet.")

def t_reflection():
    CTX["hint"] = "Open reflection.txt, type a short answer after each label (same line), and put an x in one [ ] box."
    path = os.path.join(ROOT, "reflection.txt")
    if not os.path.exists(path):
        raise Fail("reflection.txt not found")
    text = open(path, encoding="utf-8", errors="replace").read()
    bad = False
    for field in REFLECTION_FIELDS:
        m = re.search(r"^\s*" + re.escape(field) + r"[^:\n]*:(.*)$", text, re.M | re.I)
        ok = bool(m) and len(re.findall(r"[A-Za-z0-9]+", m.group(1))) >= 1
        bad |= not ok
        CTX["expected"].append((ok, f"{field}: <your answer>" + ("" if ok else
                                ("   <- line missing (do not delete it)" if not m else "   <- still empty"))))
    marked = len(re.findall(r"\[\s*[xX]\s*\]", text)) >= 1
    bad |= not marked
    CTX["expected"].append((marked, "Result: one box marked [x]" + ("" if marked else "   <- no box marked")))
    if bad:
        raise Fail("reflection.txt is not finished.")

REFLECTION_FIELDS = ["Name", "Hardest question", "One bug I fixed",
                     "I helped", "Topic", "How I helped", "I learned"]

TESTS = [
    ("q1_given",    7, "Q1 vending machine: every step + totals",      t_q1_given),
    ("q1_second",   5, "Q1 second coins file + a random one",                         t_q1_second),
    ("q1_table",    3, "Q1 the machine IS the two 2D arrays",          t_q1_table),
    ("q2_given",    7, "Q2 frfr counts for messages.txt",              t_q2_given),
    ("q2_second",   5, "Q2 second messages + a random one",    t_q2_second),
    ("q2_switch",   3, "Q2 frfr_step uses switch, no strstr",          t_q2_switch),
    ("q3_given",    8, "Q3 BroBank ATM session (every event)",         t_q3_given),
    ("q3_second",   8, "Q3 second session + a random one",      t_q3_second),
    ("q3_switch",   4, "Q3 atm_step is a switch on the state",         t_q3_switch),
    ("q4_given",    8, "Q4 door lock: trace + outputs for keypad.txt", t_q4_given),
    ("q4_second",   7, "Q4 second keypad + a random one",       t_q4_second),
    ("q4_table",    5, "Q4 the lock IS the two 4 x 3 tables",          t_q4_table),
    ("q5_given",   10, "Q5 comments removed from code.txt",            t_q5_given),
    ("q5_second",   8, "Q5 more code files + a random one",  t_q5_second),
    ("q5_ways",     7, "Q5 switch way and table way are the same",     t_q5_ways),
    ("reflection",  5, "reflection.txt (Peer Learning)",               t_reflection),
]
assert sum(t[1] for t in TESTS) == 100

# ============================================================================
# ENGINE - debug folders, report, command line (keep)
# ============================================================================
def save_debug(name):
    """Write a folder with the exact inputs so the student can re-run the test by hand."""
    prog = CTX.get("program")
    if not prog or not CTX.get("inputs"):
        return None
    folder = os.path.join(DEBUG, name)
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder, exist_ok=True)
    for title, content in CTX["inputs"]:
        with open(os.path.join(folder, title.split()[-1]), "w", newline="\n") as f:
            f.write(content)
    exe = os.path.join(BUILD, prog + EXE)
    if os.path.exists(exe):
        shutil.copy(exe, folder)
    with open(os.path.join(folder, "expected.txt"), "w") as f:
        f.write("Lines your program must print (case and spaces do not matter):\n\n")
        for ok, line in CTX.get("expected", []):
            f.write(("[ OK ] " if ok else "[FAIL] ") + line + "\n")
        if CTX.get("hint"):
            f.write("\nHINT: " + CTX["hint"] + "\n")
    rel = os.path.relpath(folder, ROOT)
    win_rel = rel.replace("/", "\\")
    with open(os.path.join(folder, "HOW_TO_RUN.txt"), "w") as f:
        f.write(f"""Re-run test '{name}' by hand with EXACTLY the same input
=============================================================
This folder has: the input file(s), your compiled program, expected.txt

Windows (Command Prompt):
    cd {win_rel}
    {prog}.exe

Windows (PowerShell):
    cd {win_rel}
    .\\{prog}.exe

Mac / Linux:
    cd {rel}
    ./{prog}

Then compare what you see with expected.txt.
(The program here was built from ALL the .c files in your question folder.)
Tip: add printf("p - s = %d\\n", (int)(p - s)); lines in your code to trace it,
recompile, and run:  {PY} tests/run_all_tests.py {name}
""")
    return rel

class Tee:
    def __init__(self):
        self.buf = []
    def __call__(self, *a):
        line = " ".join(str(x) for x in a)
        self.buf.append(line)
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", "replace").decode())


def write_markdown(path, results, earned, total):
    """A results page for GitHub Actions: score table + what was expected for every FAIL."""
    fence = "~~~~"
    out = [f"# {LAB} - your score: **{earned} / {total}**", ""]
    if earned == total:
        out += ["All tests pass. Remember reflection.txt and to push your last version.", ""]
    out += ["| | Test | Points | What it checks |", "|---|---|---:|---|"]
    for name, pts, desc, ok, _ in results:
        out.append(f"| {'✅' if ok else '❌'} | `{name}` | {pts if ok else 0} / {pts} | {desc} |")
    fails = [r for r in results if not r[3]]
    if fails:
        out += ["", "## What to fix", "",
                "Click a test: you see the INPUT, every EXPECTED line marked `[ OK ]` or `[FAIL]`, "
                "what YOUR PROGRAM PRINTED, and a HINT. Upper/lower case and extra spaces do not matter.", ""]
        for name, pts, desc, ok, detail in fails:
            out += [f"<details><summary>❌ <b>{name}</b> ({pts} pts) - {desc}</summary>", "",
                    fence + "text", detail.strip(), fence, "",
                    f"Run it on your computer:  `py tests\\run_all_tests.py {name}`"
                    f"  (Mac: `python3 tests/run_all_tests.py {name}`)", "", "</details>", ""]
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
    except OSError:
        pass

def main():
    if "--list" in sys.argv[1:]:
        for name, pts, desc, _ in TESTS:
            sys.stdout.write(f"{name}\t{pts}\t{desc}\n")
        return 0
    md_path = sys.argv[sys.argv.index("--markdown") + 1] if "--markdown" in sys.argv[1:-1] else None
    args = [a for a in sys.argv[1:] if not a.startswith("-") and a != md_path]
    results = []
    verbose = "-v" in sys.argv[1:]
    want = args[0].lower() if args else ""
    chosen = [t for t in TESTS if t[0] == want] or [t for t in TESTS if t[0].startswith(want)]
    if not chosen:
        print("Unknown test:", want); print("Tests:", ", ".join(t[0] for t in TESTS)); return 2
    if len(chosen) == 1:
        verbose = True          # running a single test: always show the details
    print = Tee()
    total = earned = 0
    print("=" * 66)
    print(f" ESE 124 {LAB} - autograder      (add -v to see details for PASS too)")
    print("=" * 66)
    for name, pts, desc, fn in chosen:
        total += pts
        reset_ctx()
        try:
            fn()
            earned += pts
            print(f" PASS  {pts:>2}/{pts:<2} {desc}   [{name}]")
            results.append((name, pts, desc, True, ""))
            if verbose:
                print(report_details())
        except Fail as e:
            print(f" FAIL   0/{pts:<2} {desc}   [{name}]")
            print("      PROBLEM: " + str(e).replace("\n", "\n        "))
            print(report_details())
            results.append((name, pts, desc, False, "PROBLEM: " + str(e) + "\n" + report_details()))
            print(f"      Re-run just this test:  {PY} tests/run_all_tests.py {name}")
            folder = save_debug(name)
            if folder:
                print(f"      Debug it yourself: open {folder}{os.sep}HOW_TO_RUN.txt")
        except Exception as e:
            print(f" FAIL   0/{pts:<2} {desc}   [{name}]")
            print(f"      Test crashed: {e!r}")
            results.append((name, pts, desc, False, f"Test crashed: {e!r}"))
        print()
    print("-" * 66)
    print(f" SCORE: {earned} / {total}")
    if md_path:
        write_markdown(md_path, results, earned, total)
    print("=" * 66)
    try:
        with open(REPORT, "w", encoding="utf-8") as f:
            f.write("\n".join(print.buf) + "\n")
        print(f" Full report saved to tests{os.sep}last_report.txt (open it in VS Code to scroll).")
    except OSError:
        pass
    return 0 if earned == total else 1

if __name__ == "__main__":
    sys.exit(main())
