import re

def parse_diff(patch: str, filename: str) -> dict:
    """
    Builds a map of {absolute_line_number: diff_position}

    absolute_line_number = the real line number in the file
    diff_position        = position within the PR diff (what GitHub API wants)

    Only added lines (starting with +) are included —
    you can only comment on lines that are IN the diff.
    """
    line_map = {}
    diff_position = 0
    current_line = 0

    if not patch:
        return line_map

    for line in patch.split("\n"):

        if line.startswith("@@"):
            # Parse hunk header to find where this hunk starts in the file
            # Format: @@ -old_start,old_count +new_start,new_count @@
            match = re.search(r"\+(\d+)", line)
            if match:
                current_line = int(match.group(1)) - 1
            diff_position += 1

        elif line.startswith("+"):
            # Added line — this is reviewable
            current_line += 1
            diff_position += 1
            line_map[current_line] = diff_position

        elif line.startswith("-"):
            # Removed line — doesn't exist in new file, not reviewable
            diff_position += 1

        else:
            # Context line — unchanged, exists in file but not reviewable
            current_line += 1
            diff_position += 1

    return line_map