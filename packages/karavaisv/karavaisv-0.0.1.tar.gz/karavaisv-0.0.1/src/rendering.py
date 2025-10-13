import re
import copy


KSV_META_FLAGS: set[str] = {"if", "elif", "else", "endif", "for", "endfor"}
KSV_META_OPENINGS: set[str] = {"if", "for"}
KSV_META_CLOSURES: set[str] = {"endif", "endfor"}
KSV_META_COLONS: set[str] = {"if", "elif", "else", "for"}


def ksv_check_line_for_meta(line: str) -> str:
    if re.match(r"\s*\~\$\sif.*\$\~.*", line):      # ksv if
        return "if"
    if re.match(r"\s*\~\$\selif.*\$\~.*", line):    # ksv elif
        return "elif"
    if re.match(r"\s*\~\$\selse.*\$\~.*", line):    # ksv else
        return "else"
    if re.match(r"\s*\~\$\sendif.*\$\~.*", line):   # ksv endif
        return "endif"
    if re.match(r"\s*\~\$\sfor.*\$\~.*", line):     # ksv for
        return "for"
    if re.match(r"\s*\~\$\sendfor.*\$\~.*", line):  # ksv endfor
        return "endfor"
    return None


def ksv_is_meta_in_block(content: str) -> bool:
    all_lines = content.split('\n')[:-1]

    for line in all_lines:
        if ksv_check_line_for_meta(line) is not None:
            return True

    return False


def ksv_render_single_line(parameters: dict, line: str, ext_locals:dict) -> str:
    inline_templates: list[str] = re.findall(r"\~/.*?/\~", line)
    exec_locals: dict = locals() | ext_locals
    templated_line: str = copy.copy(line) + '\n'

    if len(inline_templates) > 0:
        for inline_template in inline_templates:
            exec(f"templated_line = str({inline_template[3:-3]})", globals=globals(), locals=exec_locals)
            templated_line = templated_line.replace(inline_template, exec_locals['templated_line'])

    return templated_line


def ksv_meta_to_py_line(line: str) -> str:
    converted_line: str = copy.copy(line)

    beginning_meta: list[str] = re.findall(r"^\s*\~\$\s*", line)
    trailing_meta: list[str] = re.findall(r"\s*\$\~.*$", line)
    add_colon: bool = ksv_check_line_for_meta(line) in KSV_META_COLONS

    converted_line = converted_line.replace(beginning_meta[0], '')
    converted_line = converted_line.replace(trailing_meta[0], '')

    if add_colon:
        converted_line += ':'

    return converted_line


def ksv_render_single_block(parameters: dict, content: str) -> str:
    all_lines: list[str] = content.split('\n')[:-1]
    data_width_max: int = 32  # FIXME TODO FIXME TODO FIXME FIXME TODO FIXME TODO FIXME TODO FIXME TODO FIXME TODO FIXME TODO DEBUG ONLY
    executable_content: str = ""
    executed_content: str = ""
    exec_locals: dict = locals()
    block_contains_meta: bool = ksv_is_meta_in_block(content)

    for line in all_lines:
        if ksv_check_line_for_meta(line) is not None: # meta
            executable_content += ksv_meta_to_py_line(line)

        else:                                         # non-meta
            if block_contains_meta:
                executable_content += 4 * ' '
            executable_content += "executed_content += "
            executable_content += f'ksv_render_single_line(parameters, "{line}", ext_locals=locals())'

        executable_content += '\n'

    exec(executable_content, locals=exec_locals)
    executed_content = exec_locals['executed_content']

    return executed_content


def ksv_divide_into_blocks(content: str) -> list[str]:
    meta_flags_seq: list[str] = []
    depth_level: int = 0
    ksv_blocks: list[str] = []
    line_skip: bool = False
    all_lines: list[str] = content.split('\n')[:-1]

    for i, line in enumerate(all_lines):
        meta_key: str = ksv_check_line_for_meta(line)
        meta_flags_seq.append(meta_key)
        line_skip = False

        if meta_key in KSV_META_OPENINGS:
            depth_level += 1
            ksv_blocks.append("")

        if meta_key in KSV_META_CLOSURES:
            depth_level -= 1
            ksv_blocks.append("")
            line_skip = True

        if not line_skip:
            if len(ksv_blocks) == 0:
                ksv_blocks.append("")
            ksv_blocks[-1] += line
            if (i != len(all_lines)):
                ksv_blocks[-1] += '\n'

    return ksv_blocks


def ksv_render_substring(parameters: dict, content: str) -> str:
    rendered_content: str = ""
    ksv_blocks: list[str] = ksv_divide_into_blocks(content)
    ksv_blocks_count: int = len(ksv_blocks)

    if ksv_blocks_count > 1:
        for ksv_block in ksv_blocks:
            rendered_content += ksv_render_substring(parameters, ksv_block)

    elif ksv_blocks_count == 1:
        rendered_content += ksv_render_single_block(parameters, ksv_blocks[0])

    return rendered_content


def ksv_render(parameters: dict, filepath: str) -> str:
    rendered_code: str = ""
    with open(filepath, 'r') as file:
        content = file.read()
    rendered_code = ksv_render_substring(parameters, content)

    return rendered_code
