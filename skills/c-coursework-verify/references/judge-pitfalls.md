# Judge-style C checklist

## Format specifiers

| Type | `scanf` | `printf` |
| --- | --- | --- |
| `int` | `%d` | `%d` |
| `float` | `%f` | `%f` |
| `double` | `%lf` | `%f` |
| `char` | `%c` | `%c` |
| string | `%s` | `%s` |

Always pass addresses to `scanf`: `scanf("%d", &year)`.

## Worked example: data-size conversion

Prompt requirements:

- Read one `float` in KB.
- Print KB, MB, and B with two decimals.
- Use full-width `：` in the labels, exactly as shown.
- Keep one trailing newline per line.

```c
#include <stdio.h>

int main(void) {
    float kb;
    scanf("%f", &kb);
    printf("数据量：%.2fKB\n", kb);
    printf("数据量：%.2fMB\n", kb / 1024);
    printf("数据量：%.2fB\n", kb * 1024);
    return 0;
}
```

Sample input:

```text
1024
```

Expected output:

```text
数据量：1024.00KB
数据量：1.00MB
数据量：1048576.00B
```

Common failures: ASCII `:` instead of `：`, `printf("...KB")` without `\n`, or dividing with integer arithmetic.

## Boundary cases worth running

| Prompt type | Cases |
| --- | --- |
| 4-digit PIN | `999`, `1000`, `9999`, `10000` |
| IPv4 octet | `0.0.0.0`, `255.255.255.255`, `256.0.0.1` |
| Leap year | `1900`, `2000`, `2024`, `2023` |
| Single character | normal letter, space, newline, control character |

## Byte-level checks

The verifier normalizes CRLF to LF but does not trim spaces or drop the final newline. If it reports a difference at the final byte, compare `\n` versus no newline before changing logic.
