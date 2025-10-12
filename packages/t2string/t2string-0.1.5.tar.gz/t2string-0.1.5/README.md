# 🧩 t2string

Convert **Python 3.14’s `t` strings** (template strings) into **normal strings** — quickly and easily.

---

## ✨ Overview

Starting with **Python 3.14**, a new string literal prefix `t` was introduced for *template strings*, 
(***Note That Convert all int values to str values then pass for t2string as it will give error if int entered***)
such as:

```python
from t2string import t2string
owner = "Yuvneil"
age = 20
msg = t"Hi {owner} boss, you are {str(age)}"
print(msg)
print(t2string(msg))
