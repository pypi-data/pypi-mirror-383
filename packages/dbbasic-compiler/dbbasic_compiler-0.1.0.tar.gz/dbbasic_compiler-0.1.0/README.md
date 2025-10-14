# DBBasic-Compiler

**The compiler that understands English.**

Traditional compilers check syntax and throw errors. DBBasic-Compiler understands what you want and generates optimal code.

For 70 years, compilers have been mechanical syntax checkers. Now there's one that thinks.

## Quick Start

**1. Install:**
```bash
pip install -r requirements.txt
```

**2. Set your API key:**
```bash
export ANTHROPIC_API_KEY='your-api-key'
```

**3. Write an intent file** (describe what you want):
```markdown
# Calculator

Create a simple calculator program.

## Features
- Add, subtract, multiply, divide
- Handle division by zero
- Loop until user types "quit"
```

**4. Compile:**
```bash
python ai_compiler.py compile intent/calculator.intent.md
```

**5. Run:**
```bash
python ai_compiler.py run calculator.intent
```

**That's it.** No code written. Just intent compiled to execution.

## What Is This?

A compiler that:
- **Understands natural language** (no syntax to learn)
- **Asks clarifying questions** (no cryptic error messages)
- **Generates optimal code** (not just syntax checking)
- **Validates correctness** (against your intent)

## Traditional Compiler vs DBBasic-Compiler

### Traditional Compiler (GCC, Python, etc):
```bash
$ gcc program.c
program.c:42:5: error: expected ';' before 'return'
```
**Dumb syntax checker. You fix semicolons.**

### DBBasic-Compiler:
```bash
$ python ai_compiler.py compile intent/myapp.intent.md
[AI Compiler] Understanding problem description...
[AI Compiler] ✓ Compilation successful!
```
**Intelligent translator. It understands intent.**

## Examples

### Hello World

**Intent file** (`intent/hello_world.intent.md`):
```markdown
# Hello World - Greeting Program

Create a simple program that greets users.

## What It Should Do
1. Ask the user for their name
2. Greet them with a friendly message
3. Ask if they want to greet someone else
4. If yes, repeat; if no, say goodbye
```

**Compile and run:**
```bash
python ai_compiler.py compile intent/hello_world.intent.md
python ai_compiler.py run hello_world.intent
```

**Output:**
```
What's your name? Alice
Hello, Alice! Nice to meet you!
Greet someone else? (yes/no): no
Goodbye! Have a great day!
```

### More Examples

See `intent/` directory for example intent files.

## How It Works

```
Intent Description (.intent.md)
        ↓
AI Compiler (Claude Sonnet 4.5)
- Understands natural language
- Generates optimal implementation
- Handles edge cases
        ↓
Executable Code (.py)
        ↓
Runs!
```

## Commands

```bash
# Compile an intent file
python ai_compiler.py compile intent/<name>.intent.md

# Run a compiled program
python ai_compiler.py run <name>.intent

# List all compiled programs
python ai_compiler.py list
```

## Philosophy

**Code is a liability, not an asset. Intent is the asset.**

Programming should be about clearly describing problems, not fighting syntax errors.

DBBasic-Compiler makes problem description the programming language.

## The Paradigm Shift

### Old Way:
1. Think of solution
2. Translate to Python syntax
3. Fix syntax errors
4. Fix logic errors
5. Add error handling
6. Test

### New Way:
1. Describe the problem clearly
2. Compile
3. Run

## Why "Compiler"?

For 70 years, compilers have been:
- Syntax validators
- Mechanical translators
- Rule followers

But now we have AI that can:
- Understand intent
- Make decisions
- Learn patterns
- Ask questions

**We're not misusing the term "compiler."**
**We're using it correctly for the first time.**

A compiler should compile *ideas* into code, not just check syntax.

## Part of DBBasic

DBBasic is about simplicity:
- **DBBasic framework**: Simple Python web framework
- **DBBasic-Compiler**: Simple way to write programs

Both share:
- Minimalism over complexity
- Readability over magic
- Simplicity over features

## Requirements

- Python 3.7+
- Anthropic API key (Claude Sonnet 4.5)

Get your API key: https://console.anthropic.com/

## Installation

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY='your-api-key'
```

## Contributing

This is experimental. We're exploring:
- What does programming look like with intelligent compilation?
- How should intent be structured?
- What are the patterns in problem descriptions?
- Can this scale to complex systems?

Ideas and feedback welcome.

## License

MIT

## Tagline

**"The first compiler that compiles ideas into code."**

---

*From the makers of DBBasic - because simple is better.*
