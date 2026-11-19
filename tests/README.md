# Tests

The automated host-side tests cover the Python analysis calculations and input validation. They do not compile or execute the embedded firmware.

Run:

```bash
python -m unittest discover -s tests -v
```

Hardware tests must be executed manually on the nRF52 DK PCA10040 and recorded using `test_plan.md`.
