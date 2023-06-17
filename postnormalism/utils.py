import os


def generate_project_structure(root: str, exclude_dirs: set = None, indent: str = "|   ") -> str:
    if exclude_dirs is None:
        exclude_dirs = {'.idea', '__pycache__', '.git', 'build', 'dist', 'postnormalism.egg-info'}

    def walk(path: str, level: int = 0) -> str:
        output = ""
        for entry in sorted(os.listdir(path)):
            if entry in exclude_dirs:
                continue

            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                output += f"{indent * level}|-- {entry}/\n"
                output += walk(entry_path, level + 1)
            else:
                output += f"{indent * level}|-- {entry}\n"
        return output

    return walk(root)
