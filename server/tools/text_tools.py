
def read_text(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


def append_text(path: str, text: str):
    with open(path, 'a') as f:
        f.write(text + "\n")
    return {"status": "success", "text_added": text}

def edit_text(path: str, line_number: int, new_text: str):
    with open(path, 'r') as f:
        lines = f.readlines()
    if 0 <= line_number < len(lines):
        lines[line_number] = new_text + "\n"
        with open(path, 'w') as f:
            f.writelines(lines)
        return {"status": "success", "line_number": line_number, "new_text": new_text}
    return {"status": "error", "message": "line_number out of range"}
