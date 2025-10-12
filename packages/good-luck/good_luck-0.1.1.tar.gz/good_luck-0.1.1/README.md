# good-luck

Strip away all function calls from tracebacks, by default.
Just install the package and enjoy much less useful information when hitting exceptions.

## Demo

```
❯ cat t.py
def rec():
    rec()

rec()

❯ python t.py
RecursionError: maximum recursion depth exceeded
```