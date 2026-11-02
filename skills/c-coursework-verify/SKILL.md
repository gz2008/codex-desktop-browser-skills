---
name: c-coursework-verify
description: 'Solve strict C course or online-judge assignments and verify them locally: extract exact input/output requirements, compile with gcc, and byte-compare sample plus boundary cases. Use for C homework or lab questions with fixed output; not for CTF pwn, C++ projects, or general debugging.'
---

# C Coursework Verify

Use this for C homework, weekly lab questions, and judge-style prompts where the output string matters as much as the algorithm.

## Workflow

1. Build a small spec before coding: input type and format, exact output text and punctuation, precision, trailing newline, and value ranges.
2. Write the smallest standard C program. Avoid menus, extra prompts, and "improvements" the prompt did not ask for.
3. Save the source and fixtures under `$env:TEMP\codex-cwork\<slug>\`.
4. Verify with the bundled script:

```powershell
python "$env:CODEX_HOME\skills\c-coursework-verify\scripts\verify_c.py" `
  --src main.c --input sample.in --expect sample.out
```

It compiles in the default WSL distribution with
`gcc -std=c11 -Wall -Wextra -Werror`, runs the program, and reports the first
byte difference. Use `--distro` or `--user` when the default WSL environment is
not the intended compiler. Use `--keep` to retain the temp build; add
`--no-werror` only when a harmless warning is unavoidable.

5. Run at least one boundary case when the prompt defines a range (`0`, `9999`, `255`, invalid input).
6. Deliver one code block. If the user asked for code only, do not add prose.

## Non-obvious pitfalls

- `scanf("%d", year)` is missing `&`; the compiler warning points at it.
- Chinese full-width `：` and `（）` are different bytes from ASCII `:` and `()`. Copy them from the prompt.
- `printf`, not `print`; `%f` for float, `%lf` for double input, `%d` for int.
- Integer division truncates. Cast to `double` before dividing when a decimal result is expected.
- Many judges require the final newline. Do not drop it.
- `scanf("%c")` keeps a leading newline or space; use `scanf(" %c")` only when the spec allows skipping whitespace.
- Print a prompt line only when the sample output includes it. On many judges, an extra prompt is a wrong answer.

See [references/judge-pitfalls.md](references/judge-pitfalls.md) for the format table and a worked example.

## Rules

- Do not claim the output matches without running the sample.
- Do not submit to an external judge unless the user asks.
- If no expected output is available, say that only compilation and sample/boundary behavior were checked.
