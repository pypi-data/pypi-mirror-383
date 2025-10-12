import pickle
import random
import shutil
from pathlib import Path

import randomname
from typer import Typer
from pydantic import BaseModel

app = Typer(name="blindfile")

working_dir = Path.cwd()
out_dir = working_dir / "__blindfile__"
config_file = out_dir / ".config.pkl"


class Config(BaseModel):
    mapping: dict[str, str]
    out_dir: Path


def get_covered_file_name(original_filename: str) -> str:
    covered_name = randomname.get_name(
        adj=(
            "shape",
            "colors",
            "size",
            "character",
            "age",
            "temperature",
            "appearance",
            "geometry",
        ),
        noun=("fruit", "plants"),
    )
    return f"{covered_name}{Path(original_filename).suffix}"


@app.command()
def cover(pattern: str) -> None:
    config = Config(
        mapping={},
        out_dir=out_dir,
    )

    paths = list(working_dir.glob(pattern))
    random.shuffle(paths)

    if not paths:
        print(f"No files found matching pattern: {pattern}")
        return

    out_dir.mkdir(exist_ok=True)

    for path in paths:
        covered_file_name = get_covered_file_name(path.name)
        covered_path = config.out_dir / covered_file_name

        while covered_path.exists():
            covered_file_name = get_covered_file_name(path.name)
            covered_path = config.out_dir / covered_file_name

        config.mapping[path.name] = covered_file_name

        shutil.copy(path, covered_path)

        print(covered_path.relative_to(working_dir))

    with open(config_file, "wb") as f:
        pickle.dump(config, f)


@app.command()
def uncover() -> None:
    try:
        with open(config_file, "rb") as f:
            config = pickle.load(f)
    except FileNotFoundError:
        print("Nothing to uncover. Please run the 'cover' command first.")
        return

    for original_name, covered_name in config.mapping.items():
        print(
            (config.out_dir / covered_name).relative_to(working_dir),
            "->",
            original_name,
        )


def main() -> None:
    app()
