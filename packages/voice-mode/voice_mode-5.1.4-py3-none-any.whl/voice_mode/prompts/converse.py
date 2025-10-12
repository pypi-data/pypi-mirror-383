"""Conversation prompts for voice interactions."""

from voice_mode.server import mcp


@mcp.prompt()
def converse() -> str:
    """Have an ongoing two-way voice conversation with the user."""
    instructions = [
        "Using tools from voice-mode, have an ongoing two-way conversation",
        "End the chat when the user indicates they want to end it",
        "Keep your utterances brief unless a longer response is requested or necessary",
    ]
    
    return "\n".join(f"- {instruction}" for instruction in instructions)
