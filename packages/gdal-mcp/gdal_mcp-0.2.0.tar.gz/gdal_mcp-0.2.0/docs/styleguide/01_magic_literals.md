# 1️⃣ `01_magic_literals.md`

````markdown
# Magic Literals

### Principle
Avoid unexplained raw numbers or strings.  
Name them with constants or enums to clarify intent.

### ✅ Prefer
```python
MAX_ITEMS = 100
TIMEOUT_SECONDS = 30

if len(items) > MAX_ITEMS:
    time.sleep(TIMEOUT_SECONDS)
````

### ❌ Avoid

```python
if len(items) > 100:
    time.sleep(30)
```

### Exceptions

* Trivial values (`0`, `1`, `[]`, `{}`)
* Clear math formulas (`b**2 - 4*a*c`)

### Why

* Improves readability and intent
* Centralizes change management
* Prevents “mystery numbers”

> 💡 *Include units and context in names:* `CACHE_TTL_SECONDS`, `MAX_SIZE_MB`

---

### 🤝 Our Philosophy

Constants communicate meaning.
We’d rather see a readable name than a clever one-liner.




````

---


````

---



````

---


````

---


```

---


````

---



````

---



````

---



````

---



````

---



```

---

✅ **Result:**  
You now have a fully-scaffolded `docs/styleguide/` directory that:

- Reads warmly and humanly  
- Reflects your actual coding philosophy  
- Supports both contributors *and* agent reasoning  
- Can grow organically over time  

Would you like me to generate a short **contributor-friendly blurb** for your repository’s main `CONTRIBUTING.md` linking to this styleguide (e.g., “If you’re unsure about formatting or style, start here”)?
```
