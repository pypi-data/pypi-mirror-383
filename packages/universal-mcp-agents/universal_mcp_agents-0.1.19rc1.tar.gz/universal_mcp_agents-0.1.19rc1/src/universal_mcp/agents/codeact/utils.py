import re

from universal_mcp.logger import logger

BACKTICK_PATTERN = r"(?:^|\n)```(.*?)(?:```(?:\n|$))"


def extract_and_combine_codeblocks(text: str) -> str:
    """
    Extracts all codeblocks from a text string and combines them into a single code string.

    Args:
        text: A string containing zero or more codeblocks, where each codeblock is
            surrounded by triple backticks (```).

    Returns:
        A string containing the combined code from all codeblocks, with each codeblock
        separated by a newline.

    Example:
        text = '''Here's some code:

        ```python
        print('hello')
        ```
        And more:

        ```
        print('world')
        ```'''

        result = extract_and_combine_codeblocks(text)

        Result:

        print('hello')

        print('world')
    """
    # Find all code blocks in the text using regex
    # Pattern matches anything between triple backticks, with or without a language identifier
    try:
        code_blocks = re.findall(BACKTICK_PATTERN, text, re.DOTALL)
    except Exception as e:
        logger.error(f"Error extracting code blocks: {e}")
        logger.error(f"Text: {text}")
        return ""

    if not code_blocks:
        return ""

    # Process each codeblock
    processed_blocks = []
    for block in code_blocks:
        # Strip leading and trailing whitespace
        cleaned_block = block.strip()

        # If the first line looks like a language identifier, remove it
        lines = cleaned_block.split("\n")
        if lines and (not lines[0].strip() or " " not in lines[0].strip()):
            # First line is empty or likely a language identifier (no spaces)
            cleaned_block = "\n".join(lines[1:])

        processed_blocks.append(cleaned_block)

    # Combine all codeblocks with newlines between them
    combined_code = "\n\n".join(processed_blocks)
    return combined_code
