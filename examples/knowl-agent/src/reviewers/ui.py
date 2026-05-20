import os
import shutil


def t(code, text):
    return f"\033[{code}m{text}\033[0m"


def bold(text):
    return t("1", text)


def dim(text):
    return t("2", text)


def green(text):
    return t("32", text)


def yellow(text):
    return t("33", text)


def cyan(text):
    return t("36", text)


def red(text):
    return t("31", text)


def header(title):
    w = shutil.get_terminal_size().columns
    print()
    print(green("=" * w))
    print(green(f"  {title}"))
    print(green("=" * w))


def subheader(title):
    print()
    print(cyan(f"── {title}"))


def badge(status):
    return {"待评审": yellow("○ 待评审"), "通过": green("✓ 通过"), "需修改": red("✗ 需修改")}.get(status, status)


def wait():
    input(dim("\n按 Enter 继续..."))


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def confirm(prompt):
    return input(f"\n  {prompt} (y/n): ").strip().lower() == "y"


def ask_comment():
    c = input(f"  意见（可选，直接 Enter 跳过）: ").strip()
    return c
