# ⟁ Null Lens — Python SDK

Stateless API wrapper for [Null Lens](https://null-core.ai)  
Converts any natural-language input into a deterministic schema:

**[Motive] [Scope] [Priority]**

---

## ⚙️ Install
```bash
pip install null-lens
```

## 💡 Usage
```python
from null_lens import NullLens

lens = NullLens(api_key="YOUR_API_KEY")
result = lens.parse("Summarize Q4 strategy across LATAM markets.")

print(result)
# [Motive] Summarize strategic direction for Q4
# [Scope] LATAM markets
# [Priority] Identify key actions for planning cycle
```
For complete documentation and Python SDK,
see the [root README](https://github.com/null-core-ai/null-lens#readme)

## License: MIT
