import re, os, json, logging
import pandas as pd

logger = logging.getLogger(__name__)

class Utils:
    @staticmethod
    def extract_solidity_code(markdown_text):
        pattern = r'```solidity\n(.*?)```'
        if (matches := re.findall(pattern, markdown_text, re.DOTALL)):
            return matches[0]
        else:
            pattern = r'```\n(.*?)```'
            if (matches := re.findall(pattern, markdown_text, re.DOTALL)):
                return matches[0]
            else:
                return None

    @staticmethod
    def save_string_to_file(file_name: str, content: str):
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_name)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_name, 'w') as file:
                file.write(content)
            logger.info(f"Content successfully saved to {file_name}")
        except IOError as e:
            logger.error(f"An error occurred while writing to the file {file_name}: {e}")

    @staticmethod
    def save_specification(task_id: str, content: str):
        path = os.path.join("results", f"{task_id}_spec.sol")
        try:
            with open(path, 'w') as f:
                f.write(content)
            logger.info(f"Specification successfully saved to {path}")
        except IOError as e:
            logger.error(f"An error occurred while writing to the file {path}: {e}")

    @staticmethod
    def save_status(task_id: str, status_messages: list):
        path = os.path.join("results", f"{task_id}_status.json")
        try:
            with open(path, 'w') as f:
                json.dump(status_messages, f)
            logger.info(f"Status messages successfully saved to {path}")
        except IOError as e:
            logger.error(f"An error occurred while writing to the file {path}: {e}")

    @staticmethod
    def build_initial_prompt(requested_type: str, context_types: list, verifier: str) -> str:
        # Load default instructions based on the verifier
        instructions_path = os.path.join('app', 'assets', 'instructions', f'{verifier}_instructions.txt')
        with open(instructions_path, 'r') as f:
            instructions = f.read()

        # Load the contract template for the requested ERC standard
        contract_template_path = os.path.join('app', 'assets', 'contracts', f'{requested_type.upper()}_contract_template.sol')
        with open(contract_template_path, 'r') as f:
            contract_template = f.read()

        # Load the EIP markdown for the requested ERC standard
        eip_path = os.path.join('app', 'assets', 'eips', f'{requested_type.upper()}_eip.md')
        with open(eip_path, 'r') as f:
            eip = f.read()

        # Build examples section from context types
        examples_text = ""
        
        # First include the requested type as an example if it's also in the context types
        if requested_type in context_types:
            example_path = os.path.join('app', 'assets', 'examples', f'{requested_type.upper()}_example.sol')
            with open(example_path, 'r') as f:
                examples_text += f"""
                Example {requested_type.upper()}:
                ```solidity
                    {f.read()}
                ```
                """
                
        # Then include other context types as examples
        for ctx_type in context_types:
            if ctx_type != requested_type:  # Skip if it's the same as requested_type (already included)
                example_path = os.path.join('app', 'assets', 'examples', f'{ctx_type.upper()}_example.sol')
                try:
                    with open(example_path, 'r') as f:
                        examples_text += f"""
                        Example {ctx_type.upper()}:
                        ```solidity
                            {f.read()}
                        ```
                        """
                except FileNotFoundError:
                    logger.warning(f"Example file for {ctx_type} not found")

        prompt = f"""
            ### Task: ###
            
            {instructions}

            ### Examples: ###
            {examples_text}
            
            ### ERC Interface to Annotate: ###
            
            ```solidity
                {contract_template}
            ```
            
            ### EIP Markdown Specification: ###
            
            <eip>
                {eip}
            </eip>
            """
        return prompt

    @staticmethod
    def build_reinforcement_message(output: str) -> str:
        reinforcement_message = """
            Instructions:
            - Function Bodies: The specification must not contain function implementations.
            - Postconditions Limit: Each function must have at most 4 postcondition (/// @notice postcondition) annotations above the function signature. Do not exceed this limit under any circumstances.
            - Position: add the solc-verify annotation above the related function, example:
                /// @notice postcondition supply == _totalSupply
                function totalSupply() public view returns (uint256 supply);
            - Output format: return the annotated interface inside code fence (```) to show the code block. RETURN JUST THE CONTRACT ANNOTATED, NOTHING MORE.\n\n
        """ 
        # Append the verifier's output to the reinforcement message
        reinforcement_message += f"Verifier Output:\n{output}\n"
        return reinforcement_message
        
    @staticmethod
    def save_results_to_csv(file_name: str, results: list):
        df = pd.DataFrame(results)
        try:
            df.to_csv(file_name, index=False)
            print(f"Results successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")