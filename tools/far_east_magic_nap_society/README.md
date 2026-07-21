# Far East Magic Nap Society Tooling

Dedicated tools for the **极东魔术昼寝结社之夏** civilization mod.

Current validation entry point:

```powershell
python tools/far_east_magic_nap_society/check_static.py
```

Owned structure:

```text
tools/far_east_magic_nap_society/
  check_static.ps1
  check_static.py
  tests/test_check_static.py
  deploy.ps1
```

This mod keeps its static contracts, deployment rules and future asset rules in this directory. Only stable validation and texture primitives are imported from `tools/common`.
