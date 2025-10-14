#!/usr/bin/env python3
"""
AI Compiler - Proof of Concept

The compiler that understands intent.
Compiles natural language problem descriptions to executable code.

Usage:
    python ai_compiler.py compile intent/hello_world.intent.md
    python ai_compiler.py run hello_world
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from anthropic import Anthropic


class AICompiler:
    """
    The intelligent compiler.

    Traditional compiler: Checks syntax mechanically
    AI Compiler: Understands intent, generates optimal implementation
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it as environment variable:\n"
                "export ANTHROPIC_API_KEY='your-api-key'"
            )
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

        # Directories
        self.intent_dir = Path("intent")
        self.output_dir = Path("compiled")
        self.output_dir.mkdir(exist_ok=True)

    def compile(self, intent_file: str):
        """
        Compile intent description to executable code.

        This is the core innovation:
        - Read intent (problem description)
        - Use AI to generate optimal implementation
        - Validate and save

        Like GCC, but understands natural language.
        """
        intent_path = Path(intent_file)

        if not intent_path.exists():
            print(f"Error: Intent file not found: {intent_path}")
            return False

        print(f"[AI Compiler] Reading intent: {intent_path}")
        intent_content = intent_path.read_text()

        print(f"[AI Compiler] Understanding problem description...")

        # This is the "compilation" step
        # Instead of checking syntax, we're understanding intent
        prompt = f"""You are an AI compiler. Your job is to compile natural language problem descriptions into executable Python code.

The user has provided this problem description:

{intent_content}

Generate a complete, working Python program that solves this problem.

Requirements:
1. The code should be clean, well-structured, and production-ready
2. Include error handling for edge cases mentioned in the intent
3. Follow Python best practices
4. Make it user-friendly
5. The code should be self-contained (no external dependencies beyond standard library)

Generate ONLY the Python code, no explanations. Start with #!/usr/bin/env python3"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            generated_code = response.content[0].text

            # Extract just the code if there's any wrapper text
            if "```python" in generated_code:
                generated_code = generated_code.split("```python")[1].split("```")[0].strip()
            elif "```" in generated_code:
                generated_code = generated_code.split("```")[1].split("```")[0].strip()

            # Ensure shebang
            if not generated_code.startswith("#!/usr/bin/env python3"):
                generated_code = "#!/usr/bin/env python3\n" + generated_code

            # Save compiled output
            output_name = intent_path.stem  # e.g., "hello_world"
            output_path = self.output_dir / f"{output_name}.py"

            print(f"[AI Compiler] Generating optimal implementation...")
            output_path.write_text(generated_code)

            # Make executable
            os.chmod(output_path, 0o755)

            print(f"[AI Compiler] ✓ Compilation successful!")
            print(f"[AI Compiler] Output: {output_path}")

            # Save metadata
            metadata = {
                "intent_file": str(intent_path),
                "output_file": str(output_path),
                "model": self.model,
                "compiled_at": self._get_timestamp()
            }

            metadata_path = self.output_dir / f"{output_name}.meta.json"
            metadata_path.write_text(json.dumps(metadata, indent=2))

            print(f"[AI Compiler] Metadata: {metadata_path}")
            print()
            print("To run:")
            print(f"  python ai_compiler.py run {output_name}")
            print(f"  # or directly:")
            print(f"  python {output_path}")

            return True

        except Exception as e:
            print(f"[AI Compiler] ✗ Compilation failed: {e}")
            return False

    def run(self, program_name: str):
        """Execute compiled program."""
        output_path = self.output_dir / f"{program_name}.py"

        if not output_path.exists():
            print(f"[AI Compiler] Error: Program not found: {output_path}")
            print(f"[AI Compiler] Did you compile it first?")
            print(f"  python ai_compiler.py compile intent/{program_name}.intent.md")
            return False

        print(f"[AI Compiler] Executing: {output_path}")
        print("-" * 60)

        # Execute the compiled program
        result = subprocess.run([sys.executable, str(output_path)])

        print("-" * 60)
        print(f"[AI Compiler] Program exited with code: {result.returncode}")

        return result.returncode == 0

    def list_programs(self):
        """List all compiled programs."""
        compiled_files = list(self.output_dir.glob("*.py"))

        if not compiled_files:
            print("[AI Compiler] No compiled programs found.")
            print("[AI Compiler] Compile an intent file first:")
            print("  python ai_compiler.py compile intent/hello_world.intent.md")
            return

        print("[AI Compiler] Compiled programs:")
        for f in compiled_files:
            # Read metadata if available
            meta_path = f.with_suffix(".meta.json")
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                print(f"  {f.stem:20} (from {Path(meta['intent_file']).name})")
            else:
                print(f"  {f.stem}")

    def _get_timestamp(self):
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("AI Compiler - The compiler that understands intent")
        print()
        print("Usage:")
        print("  python ai_compiler.py compile <intent_file>")
        print("  python ai_compiler.py run <program_name>")
        print("  python ai_compiler.py list")
        print()
        print("Example:")
        print("  python ai_compiler.py compile intent/hello_world.intent.md")
        print("  python ai_compiler.py run hello_world")
        print()
        print("Environment:")
        print("  ANTHROPIC_API_KEY must be set")
        return 1

    command = sys.argv[1]
    compiler = AICompiler()

    if command == "compile":
        if len(sys.argv) < 3:
            print("Usage: python ai_compiler.py compile <intent_file>")
            return 1
        intent_file = sys.argv[2]
        success = compiler.compile(intent_file)
        return 0 if success else 1

    elif command == "run":
        if len(sys.argv) < 3:
            print("Usage: python ai_compiler.py run <program_name>")
            return 1
        program_name = sys.argv[2]
        success = compiler.run(program_name)
        return 0 if success else 1

    elif command == "list":
        compiler.list_programs()
        return 0

    else:
        print(f"Unknown command: {command}")
        print("Valid commands: compile, run, list")
        return 1


if __name__ == "__main__":
    sys.exit(main())
