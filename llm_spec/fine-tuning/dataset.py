import os
from dataclasses import dataclass
from itertools import product


def get_text_file_paths(root_folder):
    """Returns a dictionary with subfolders as keys and a list of file paths (without the extension) for each subfolder."""
    subfolder_files = {}
    for subdir, _, files in os.walk(root_folder):
        if str(subdir) == str(root_folder):
            continue
        md_files = [file for file in files if file.endswith(".md")]
        files_no_ext = []
        for file in md_files:
            filepath = os.path.join(subdir, file)
            no_ext_path = filepath[:-3]
            sol_file = no_ext_path + ".sol"
            assert os.path.isfile(sol_file)
            files_no_ext.append(no_ext_path)

        subfolder_files[subdir] = files_no_ext
    return subfolder_files


@dataclass(frozen=True)
class Combination:
    markdown_content: str
    solidity_content: str


class CombinationTemplate:

    def __init__(self, root_folder, extension) -> None:
        self._text = self._read_template(root_folder, extension)

    def _read_template(self, root_folder, extension):
        with open(
            os.path.join(root_folder, "template" + extension), "r", encoding="utf-8"
        ) as f:
            return f.read()

    def render(self, content_to_be_inseted) -> str:
        return self._text.replace("//replace//", content_to_be_inseted)


def concat_from_combinations(file_combinations):
    """Combine the content of the files for each combination."""
    combinations = []
    for file_set in file_combinations:
        concat_md = ""
        concat_sol = ""
        for file_path in file_set:
            with open(file_path + ".md", "r", encoding="utf-8") as f:
                concat_md += f.read() + "\n\n"
            with open(file_path + ".sol", "r", encoding="utf-8") as f:
                concat_sol += f.read() + "\n\n"
        combinations.append(Combination(concat_md, concat_sol))
    return combinations


def generate_combinations(root_folder: str) -> list[Combination]:
    # Get all files (with no extension) from each subfolder
    subfolder_files = get_text_file_paths(root_folder)

    # Create a Cartesian product of all files (one from each subfolder)
    file_combinations = list(product(*subfolder_files.values()))

    # Generate combined strings for each combination
    return concat_from_combinations(file_combinations)


@dataclass(frozen=True)
class TrainingElement:
    markdown_output: str
    solidity_output: str

    @property
    def json(self) -> str:
        import json

        markdown_content = "\n".join(
            [line.strip() for line in self.markdown_output.splitlines()]
        )
        solidity_content = "\n".join(
            [line.strip() for line in self.solidity_output.splitlines()]
        )
        return json.dumps(
            {
                "messages": [
                    {"role": "system", "content": markdown_content},
                    {"role": "user", "content": solidity_content},
                ]
            }
        )


def main(args):
    root_folder_path = args.folder
    combinations = generate_combinations(root_folder_path)
    md_template = CombinationTemplate(root_folder_path, ".md")
    sol_template = CombinationTemplate(root_folder_path, ".sol")

    jsonl_str = ""
    for combination in combinations:
        training_row = TrainingElement(
            md_template.render(combination.markdown_content),
            sol_template.render(combination.solidity_content),
        )
        jsonl_str += training_row.json + "\n"

    with open(args.output, "w+") as f:
        f.write(jsonl_str)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="dataset generator",
        epilog="Example: python dataset.py llm_spec/app/assets/corpus/erc20/ test.jsonl",
    )
    parser.add_argument("folder", help="Folder where the corpus is")
    parser.add_argument("output", help="output file name")
    args = parser.parse_args()
    main(args)
