import re

def extract_code_blocks(
    markdown_text: str,
    languages: list[str] = None,
    include_markers: bool = False
) -> list[tuple[str, str]]:
    """Extracts code blocks from strings."""
    language_pattern = '|'.join(map(re.escape, languages))
    code_block_pattern = re.compile(rf'```({language_pattern})\s*\n(.*?)```', re.DOTALL)

    matches = code_block_pattern.findall(markdown_text)

    extracted_blocks = []
    for lang, block in matches:
        lines = block.strip().split('\n')
        if lines and lines[0].startswith('//'):
            filename = lines[0].strip('/ ')
            code = '\n'.join(lines[1:])
        elif lines and lines[0].startswith('/*'):
            filename = lines[0].strip('/* ')
            code = '\n'.join(lines[1:])
        else:
            filename = 'solution.tsx'
            code = block.strip()

        if include_markers:
            code = f"```{lang}\n{code}\n```"

        extracted_blocks.append((filename, code))
    return extracted_blocks

def extract_solution(llm_response: str) -> list[tuple[str, str]]:
    """Extracts a list of file paths and code contents from an LLM's response.

    Args:
        llm_response: The LLM's response to your concretized prompt.

    Returns:
        A list of tuples (file_path, file_content) with the file path
        relative to the current working directory and its content.
    """
    # Extract code blocks of language "typescript"
    code_blocks = extract_code_blocks(llm_response, languages=["typescript", "tsx"])

    # print(files)
    return code_blocks
