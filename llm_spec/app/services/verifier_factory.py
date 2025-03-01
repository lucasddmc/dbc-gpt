from app.services.verifier_service_interface import VerifierServiceInterface
from app.services.solc_verify_service import SolcVerifyService
# from app.services.smtchecker_service import SMTCheckerService

class VerifierFactory:
    @staticmethod
    def create_verifier_service(verifier_option: str) -> VerifierServiceInterface:
        if verifier_option.lower() == "solc_verify":
            return SolcVerifyService()
        # elif verifier_option.lower() == "smtchecker":
        #     return SMTCheckerService()
        else:
            raise ValueError(f"Unsupported verifier: {verifier_option}")