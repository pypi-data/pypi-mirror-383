# tfdpy
A python wrapper for tinyfiledialogs, a c library for cross-platform file dialogs.

Supports: Windows (untested), and MacOS (Sillicon), and Linux (x86 untested)

every other os does not have a compiled library yet.

## Installation

```bash
pip install tfdpy
```

## Usage

```python
import tfdpy
tfdpy.message_box("Title", "Message")
```

No dependencies, just a single file and the dylibs.