# Python Environment Configuration

## Virtual Environment Setup

This project uses a virtual environment for dependency management.

### Activation Commands

**For Unix-based systems (macOS, Linux):**
```bash
source venv/bin/activate
```

**For Windows systems:**
```bash
venv\Scripts\activate
```

**For Windows with bash/git bash:**
```bash
source venv/Scripts/activate
```

### Environment Variables

When running Python commands, ensure these environment variables are set:
- `PYTHONPATH=./` (if needed)
- Any project-specific environment variables

### Testing Commands

**Unix/macOS:**
```bash
cd /path/to/project && source venv/bin/activate && python -m pytest tests/
```

**Windows:**
```bash
cd C:\path\to\project && venv\Scripts\activate && python -m pytest tests\
```

### Current Project Setup

- **Platform**: darwin (macOS)
- **Venv Path**: `./venv`
- **Activation Command**: `source venv/bin/activate`
- **Python Version**: 3.13.11 (in venv)

### Notes for AI Assistant

When running Python commands in this project:
1. Always check the OS platform
2. Use the appropriate venv activation command
3. Ensure commands are run from the project root
4. Include the full path when necessary

Example command format:
```bash
cd /path/to/project && source venv/bin/activate && [command]
```</content>
<parameter name="filePath">.kilo/python_env.md