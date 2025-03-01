from app.services.verifier_service_interface import VerifierServiceInterface
from app.utils.solc_verify_utils import generate_merge
from app.utils.utils import Utils
import subprocess

class SolcVerifyService(VerifierServiceInterface):
    SOLC_VERIFY_CMD = "solc-verify.py"
    SOLC = "solc"
    SPEC_PATH = "temp/spec.sol_json.ast"

    def verify(self, solidity_spec_str: str, template_path: str, merge_output_path: str) -> (int, str):
        Utils.save_string_to_file('temp/spec.sol', solidity_spec_str)
        try:
            generate_merge('temp/spec.sol', template_path, merge_output_path)
        except Exception as e:
            # Optional: Log the error or perform other actions
            print(f"Error during merge generation: {e}")
            # Re-raise the exception to allow it to propagate
            raise

        print("NO ERRORS")
        return self.call_solc_verify(merge_output_path)

    def call_solc_verify(self, file_path) -> (int, str):
        process = subprocess.Popen(
            [self.SOLC_VERIFY_CMD, file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout.decode() + stderr.decode()
