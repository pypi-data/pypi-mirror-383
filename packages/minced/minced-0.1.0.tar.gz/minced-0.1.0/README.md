# Minced Script API

This repository packages the public runtime objects that Minced-compatible
scripts rely on. Install it from PyPI to build and test scripts without the
full Minced application:

```bash
pip install minced-script-api
```

After installation scripts can import the shared runtime context and base
classes:

```python
from minced import MINCED, MincedScriptBase
```

See the inline documentation for details on each helper.
