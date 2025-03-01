import json, subprocess, os, re, string, argparse
from typing import Tuple, Dict

SOLC = "solc"
SPEC_PATH = os.path.join("temp", "spec.sol_json.ast")

def call_solc(file_path):
    if os.path.isfile(SPEC_PATH):
        os.remove(SPEC_PATH)
    from subprocess import PIPE, run
    command = [SOLC, file_path, "--ast-compact-json", "-o", "temp"]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return result

def process_annotations(annotations, state_variables):
    for key, value in annotations.items():
        try:
            processed_annotation = value
            annotations[key] = add_triple_bars(processed_annotation)
        except ValueError as e:
            raise e


def add_prefix(annotation: str, state_variables: Dict[str, dict], prefix: str) -> str:
    for state_variable_name in state_variables.keys():
        annotation = annotation.replace(state_variable_name, prefix + "." + state_variable_name)
    return annotation


def remove_old_ref(annotation: str, prefix: str) -> str:
    pattern = r'__verifier_old_uint\s*\(\s*(con.*?)\s*\)'
    replacement = lambda match: match.group(1).replace(prefix, f'{prefix}_old')
    return re.sub(pattern, replacement, annotation)

def replace_postcondition_by_precondition(annotation: str) -> str:
    return annotation.replace("postcondition", "precondition")

def add_triple_bars(value: str) -> str:
    if not value:
        raise ValueError("Annotation is missing for a function.")
    lines = value.splitlines()
    new_annotation = ""
    for line in lines:
        new_annotation += "///" + line + "\n"
    return new_annotation

def generate_merge(spec: str, imp_template: str, merge_file_path: str):
    result = call_solc(spec)
    if result.returncode:
        # Something has gone wrong compiling the solidity code
        print("Something has gone wrong compiling the solidity code")
        raise RuntimeError(result.returncode, result.stdout + result.stderr)
    annotations, state_variables = parse_ast()
    
    # Verify if there's at least one annotation and one state variable
    if not annotations:
        raise SyntaxError("No annotations found in the specification file.")
    if not state_variables:
        raise SyntaxError("No state variables found in the specification file.")
    
    process_annotations(annotations, state_variables)

    with open(imp_template, 'r') as impl_template_file:
        template_str = impl_template_file.read()
    template = string.Template(template_str)
    merge_contract = template.substitute(annotations)
    with open(merge_file_path, 'w') as merge_file:
        merge_file.write(merge_contract)



def parse_ast() -> Tuple[Dict[str, dict], Dict[str, dict]]:
    # Fixing this for simplicity for the time being
    annotations, state_variables = dict({}), dict({})
    with open(SPEC_PATH, 'r') as spec_file:
        spec_dict = json.load(spec_file)
        for node in spec_dict["nodes"]:
            if node["nodeType"] == "ContractDefinition":
                parse_contract(node, annotations, state_variables)

    return annotations, state_variables


def parse_contract(contract_json, annotations, state_variables):
    for node in contract_json["nodes"]:
        if node["nodeType"] == "FunctionDefinition":
            parse_function(node, annotations)
        if node["nodeType"] == "VariableDeclaration":
            parse_state_variable(node, state_variables)


def parse_state_variable(node_json, state_variables):
    name = node_json["name"]
    state_variables[name] = node_json


def parse_function(function_json, annotations):
    name = function_json.get("name", "")
    parameters_size = len(function_json.get("parameters", {}).get("parameters", []))
    annotation = function_json.get("documentation", "")
    if annotation:
        # Use a regular expression to match "@notice" followed by any whitespace and "postcondition"
        if not re.search(r"@notice\s*postcondition", annotation):
            raise ValueError(f"Function '{name}' is missing required '@notice postcondition' annotation.")
        annotations[name] = annotation
        annotations[f"{name}{parameters_size}"] = annotation
    else:
        # If no annotation, raise error
        raise ValueError(f"Function '{name}' is missing documentation annotation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("solc-verify contract generation")
    parser.add_argument("spec_file_path", help="The path to the specification file.", type=str)
    parser.add_argument("--prefix", help="The prefix to be added to each variable name in a spec annotation",
                        default=None, type=str)
    parser.add_argument("merge_template_file_path", help="The path to the merge template file.", type=str)
    parser.add_argument("merge_output_file_path", help="The path to the merge output file.", type=str)
    args = parser.parse_args()

    generate_merge(args.spec_file_path, args.merge_template_file_path, args.merge_output_file_path, prefix=args.prefix)
