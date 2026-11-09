"""Acceptance tests for the Hi, Bob! exercise.

Each test runs your program as a whole, exactly as a user would: it types
a name after the "What's your name? " question, then checks what your
program prints and tries to explain what is wrong.

Run the tests from the exercise folder with:

    python test_hibob.py
"""

import os
import random
import subprocess
import sys
from pathlib import Path

EXERCISE_DIR = Path(__file__).resolve().parent
SCRIPT = "hibob.py"
PROMPT = "What's your name? "
TIMEOUT = 5  # seconds

# Each test case: (what is checked, name typed by the user).
CASES = [
    ("Bob (example of the instructions)", "Bob"),
    ("Barbara (example of the instructions)", "Barbara"),
    ("a name with a space", "Ed Baldwin"),
    ("a name with accents", "Hélène"),
    ("a name with digits", "c6p0"),
    ("an empty name", ""),
    ("a random number (it cannot be guessed in advance)",
     str(random.randint(1000, 99999))),
]


# ---------------------------------------------------------------------------
# Running the student's program
# ---------------------------------------------------------------------------

def run_program(name):
    """Run the program, typing the name followed by Enter.

    Return (stdout, stderr, return code), or None if the program
    did not stop in time.
    """
    try:
        # sys.executable is the Python running the tests,
        # so "python" vs "python3" does not matter.
        result = subprocess.run(
            [sys.executable, SCRIPT],
            input=name + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=EXERCISE_DIR,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None
    stdout = result.stdout.replace("\r\n", "\n")
    return stdout, result.stderr.strip(), result.returncode


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def show(lines):
    """Indent lines and make spaces visible (shown as '·')."""
    if not lines:
        return "    (nothing)"
    return "\n".join("    " + line.replace(" ", "·") for line in lines)


def last_lines(text, nb_lines=4):
    """Return the last lines of a text, indented."""
    lines = text.split("\n")[-nb_lines:]
    return "\n".join("    " + line for line in lines)


def expected_greeting(name):
    """Return the line the program should print, e.g. 'Hi, Bob!'."""
    return f"Hi, {name}!"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_question(stdout, stderr, return_code):
    """Check that the program asks the question once, then reads the name.

    Return (error message or None, rest of the output after the question).
    """
    printed = "Your program printed:\n" + show(stdout.splitlines())
    question = PROMPT.strip()

    if return_code != 0:
        if "EOFError" in stderr:
            return ("Your program called input() more than once: "
                    "it should ask only one question."), ""
        message = f"Your program crashed:\n{last_lines(stderr)}"
        if "NameError" in stderr:
            message += ("\nA NameError means a name is unknown: check that "
                        "your variable is spelled the same way everywhere "
                        "(Python is case-sensitive) and that the text is "
                        "between quotes.")
        elif "SyntaxError" in stderr:
            message += ("\nA SyntaxError means Python cannot read your code: "
                        "check the quotes and the parentheses on the line "
                        "shown above.")
        return message, ""

    if stdout.startswith(PROMPT):
        return None, stdout[len(PROMPT):]
    if stdout.startswith(question + "\n"):
        return (f"The name must be typed on the same line as the question: "
                f"use input({PROMPT!r}) instead of print() then input().\n"
                f"{printed}"), ""
    if stdout.startswith(question):
        return (f"The question must be exactly {PROMPT!r}, "
                f"with a space after the question mark.\n{printed}"), ""
    if question in stdout:
        extra = stdout[:stdout.index(question)]
        return (f"Your program printed {extra!r} before the question. "
                f"It should start by asking {PROMPT!r}.\n{printed}"), ""
    if stdout.lower().startswith(question.lower()):
        return (f"The question must be exactly {PROMPT!r} "
                f"(check upper and lower case letters).\n{printed}"), ""
    return (f"Your program should start by asking exactly {PROMPT!r}.\n"
            f"{printed}"), ""


def explain_wrong_greeting(line, name):
    """Explain why the greeting printed is wrong."""
    expected = expected_greeting(name)

    if line.strip() == expected:
        return "Nothing should be printed before or after the greeting " \
               "(not even spaces)."
    if "{" in line and "}" in line:
        return ("Your program printed braces { }: did you forget the f "
                "before the quotes of your f-string?")
    if line.replace(" ", "") == expected.replace(" ", ""):
        message = "The letters are right, but not the spaces."
        if line.endswith(" !"):
            message += (" print() puts a space between its arguments "
                        "(print('a', 'b') prints 'a b'): use an f-string "
                        "instead, e.g. print(f\"...{variable}...\").")
        elif "," + name in line:
            message += " A space is missing after the comma."
        return message
    if line.lower() == expected.lower():
        return ("Check upper and lower case letters: 'Hi' starts with a "
                "capital H, and the name must be printed exactly as typed.")
    if name != "Bob" and "Bob" in line:
        return ("Your program printed 'Bob' although the user typed "
                f"{name!r}: greet the name read with input(), "
                "not a name written in your code.")
    if "name" in line and "name" not in name:
        return ("Your program printed the word 'name' instead of the name "
                "typed by the user: a variable must not be written between "
                "quotes (or, in an f-string, between braces { }).")
    if line.startswith("Hi, ") and not line.endswith("!"):
        return "The greeting must end with an exclamation mark (!)."
    return "The greeting is not the expected one."


def check_greeting(rest, name):
    """Check what is printed after the question. Return a message or None."""
    expected = expected_greeting(name)
    lines = rest.splitlines()
    comparison = (f"Expected after the question:\n{show([expected])}\n"
                  f"Your program printed after the question:\n{show(lines)}")

    if lines == [expected]:
        return None
    if not lines:
        return (f"Your program printed nothing after reading the name: "
                f"it should print {expected!r} with print().")
    if len(lines) > 1:
        message = "Your program should print only the greeting, " \
                  "on a single line."
        if expected in lines:
            message += (" The right greeting is there: remove the other "
                        "print() (for instance prints used to debug).")
        return f"{message}\n{comparison}"
    return f"{explain_wrong_greeting(lines[0], name)}\n{comparison}"


def check_case(name):
    """Run one test case. Return None if it passes, else an error message."""
    result = run_program(name)
    if result is None:
        return ("Your program did not stop (infinite loop?). It should ask "
                "the question once, print the greeting, and stop.")
    stdout, stderr, return_code = result

    message, rest = check_question(stdout, stderr, return_code)
    if message is not None:
        return message
    return check_greeting(rest, name)


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(errors="replace")
    use_colors = sys.stdout.isatty() and (
        os.name != "nt" or "WT_SESSION" in os.environ)
    green = "\033[32m" if use_colors else ""
    red = "\033[31m" if use_colors else ""
    reset = "\033[0m" if use_colors else ""

    if not (EXERCISE_DIR / SCRIPT).is_file():
        print(f"No {SCRIPT} found in {EXERCISE_DIR}")
        return 1

    nb_ok = 0
    for description, name in CASES:
        message = check_case(name)
        if message is None:
            nb_ok += 1
            print(f"{green}✔{reset} {description}")
        else:
            print(f"{red}✗{reset} {description}")
            print(f"    Name typed: {name!r}")
            print("    " + message.replace("\n", "\n    ") + "\n")

    color = green if nb_ok == len(CASES) else red
    print(f"Validated: {color}{nb_ok}/{len(CASES)}{reset}")
    return 0 if nb_ok == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
