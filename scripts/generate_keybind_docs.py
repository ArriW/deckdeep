import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deckdeep.config import KEYBINDS  # noqa: E402


def generate_keybind_markdown():
    markdown = "## Controls\n\n"
    for category, binds in KEYBINDS.items():
        markdown += f"### {category}\n\n"
        markdown += "| Key | Action |\n"
        markdown += "|-----|--------|\n"
        for key, action in binds.items():
            markdown += f"| {key} | {action} |\n"
        markdown += "\n"
    return markdown


if __name__ == "__main__":
    keybind_docs = generate_keybind_markdown()
    with open("keybind_docs.md", "w") as f:
        f.write(keybind_docs)
    print("Keybind documentation generated in keybind_docs.md")
