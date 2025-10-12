# Zipwrap

A config-driven wrapper around the Linux `zip` tool

## Usage

```sh
zipwrap --config config.json
```

```sh
zipwrap --root . --include "*.py" --exclude "venv/**" --outfile dist/code.zip --recurse --compression 9
```
