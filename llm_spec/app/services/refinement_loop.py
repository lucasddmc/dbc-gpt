import time
import logging
from typing import List, Optional
from app.services.llm_service_interface import LLMServiceInterface
from app.services.verifier_service_interface import VerifierServiceInterface
from app.utils.utils import Utils
from app.services.llm_factory import LLMFactory
from app.services.verifier_factory import VerifierFactory

logger = logging.getLogger(__name__)

def loop(
    llm_service: LLMServiceInterface,
    verifier_service: VerifierServiceInterface,
    prompt: str,
    initial_prompt: str,
    interaction_counter: int,
    verification_status: List[str],
    max_iterations: int = 10
) -> Optional[str]:
    interaction_counter += 1
    if interaction_counter > max_iterations:
        print("Maximum iterations reached, terminating loop.")
        return None
    
    print(f"Interaction {interaction_counter}: Sending message to assistant.")
    
    response = llm_service.send_message(prompt)
    solidity_code = Utils.extract_solidity_code(response)
    
    print("##################### SOLIDITY #####################")
    print(solidity_code)
    print("####################################################")
    
    if not solidity_code:
        print("No Solidity code found, generating reinforcement message.")
        response += "\n\nNo Solidity code found. Please try again.\n\n"
        reinforcement_message = prepare_reinforcement_message(response, initial_prompt)
        return loop(llm_service, verifier_service, reinforcement_message, initial_prompt, interaction_counter, verification_status, max_iterations)

    try:
        print("SENDING TO VERIFY")
        status, output = verifier_service.verify(
            solidity_code,
            'app/templates/imp_spec_merge.template',
            'temp/merged_contract.sol'
        )
    except ValueError as e:
        print("Format incorrect, refining prompt and retrying")
        verification_status.append(f'Iteration {interaction_counter}:\n{str(e)}\n')
        response += "\n\nIncorrect format. Please try again.\n\n"
        reinforcement_message = prepare_reinforcement_message(solidity_code, initial_prompt)
        return loop(llm_service, verifier_service, reinforcement_message, initial_prompt, interaction_counter, verification_status, max_iterations)

    except SyntaxError as e:
        print("No annotations, state variables and functions found, refining prompt and retrying.")
        verification_status.append(f'Iteration {interaction_counter}:\n{str(e)}\n')
        response += "\n\nNo annotations, state variables and functions found in the contract. Please try again.\n\n"
        reinforcement_message = prepare_reinforcement_message(solidity_code, initial_prompt)
        return loop(llm_service, verifier_service, reinforcement_message, initial_prompt, interaction_counter, verification_status, max_iterations)

    except RuntimeError as e:
        print("Runtime error, refining prompt and retrying.")
        verification_status.append(f'Iteration {interaction_counter}:\n{str(e)}\n')
        response += "\n\nSomething has gone wrong compiling the solidity code. Please try again.\n\n"
        reinforcement_message = prepare_reinforcement_message(solidity_code, initial_prompt)
        return loop(llm_service, verifier_service, reinforcement_message, initial_prompt, interaction_counter, verification_status, max_iterations)

    except Exception as e:
        logger.error(f"Verification error: {e}")
        reinforcement_message = prepare_reinforcement_message(solidity_code, initial_prompt)
        return loop(llm_service, verifier_service, reinforcement_message, initial_prompt, interaction_counter, verification_status, max_iterations)
        
    if status != 0:
        print("Verification failed, refining prompt and retrying.")
        verification_status.append(f'Iteration {interaction_counter}:\n{output}\n')
        reinforcement_message = prepare_reinforcement_message(solidity_code, initial_prompt)
        return loop(llm_service, verifier_service, reinforcement_message, initial_prompt, interaction_counter, verification_status, max_iterations)
    else:
        print("Verification successful.")
        return solidity_code

def prepare_reinforcement_message(response: str, initial_prompt: str):
    # Create a short summary of key instructions from the initial prompt.
    key_instructions = "Remember: Return the contract in the exact specified Solidity format with all required annotations and structure."
    
    reinforcement_message = (
        "The assistant did not return the desired contract format. Please try again.\n\n"
        "Ensure the output matches the following example format:\n\n"
        "```solidity\n"
        "pragma solidity >=0.5.0;\n\n"
        "contract ERCX {\n\n"
        "    mapping (address => uint) variable1;\n"
        "    mapping (address => mapping (address => uint)) variable2;\n"
        "    uint public variable3;\n\n"
        "    /// @notice postcondition ...\n"
        "    function example1(address exampleParameter1, uint exampleParameter2) public view returns (uint256 returnValue);\n\n"
        "    /// @notice postcondition ...\n"
        "    function example2(address exampleParameter1, uint exampleParameter2) public view returns (uint256 returnValue);\n"
        "}\n"
        "```\n\n"
    )
    
    prompt = (
        reinforcement_message
        + "\nPrevious attempt:\n\n" + response
        + "\n\nReminder of key instructions:\n" + key_instructions
    )
    return prompt

def run_verification_process(
    prompt: str,
    llm_model: str,
    verifier_option: str,
    task_id: str
): 
    """
    Run the verification process 10 times in a row, saving results of each run.
    """
    all_results = []

    for run_index in range(10):
        print(f"--- Starting experiment run {run_index+1}/10 ---")
        interaction_counter = 0
        verification_status = []
        start_time = time.time()

        # Create fresh LLM & Verifier services for each experiment run
        llm_service = LLMFactory.create_llm_service(llm_model)
        verifier_service = VerifierFactory.create_verifier_service(verifier_option)

        # Perform the verification loop
        initial_prompt = prompt
        result = loop(llm_service, verifier_service, prompt, initial_prompt, interaction_counter, verification_status)

        end_time = time.time()
        duration = end_time - start_time
        annotated_contract = result if result else ""

        # Store results of this run
        run_result = {
            "run_number": run_index + 1,
            "time_taken": duration,
            "iterations": len(verification_status) + (1 if result else 0),
            "verified": result is not None,
            "annotated_contract": annotated_contract,
            "status": verification_status
        }
        all_results.append(run_result)

        # Optionally, you can save each run's contract or errors to a file
        if annotated_contract:
            Utils.save_string_to_file(f"results/{task_id}_spec_run_{run_index+1}.sol", annotated_contract)
        else:
            Utils.save_string_to_file(f"results/{task_id}_errors_run_{run_index+1}.txt", "\n".join(verification_status))
    
    # After all runs, save the aggregated results into one CSV
    Utils.save_results_to_csv(f"results/{task_id}_results.csv", all_results)
    print("All 10 experiments completed.")
