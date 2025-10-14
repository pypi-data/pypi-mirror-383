import random

from deepteam.attacks.single_turn import BaseSingleTurnAttack
from deepteam.attacks.single_turn.system_override.template import (
    SystemOverrideTemplate,
)


class SystemOverride(BaseSingleTurnAttack):
    def __init__(self, weight: int = 1, max_retries: int = 3):
        self.weight = weight
        self.max_retries = max_retries

    def enhance(self, attack: str) -> str:
        """
        Enhance the given attack with authority spoofing techniques.
        Uses max_retries to attempt different spoofing methods if enhancement fails.
        """
        enhancement_methods = [
            SystemOverrideTemplate.enhance_system_override,
            SystemOverrideTemplate.enhance_api_admin_call,
            SystemOverrideTemplate.enhance_machine_identity,
            SystemOverrideTemplate.enhance_emergency_protocol,
            SystemOverrideTemplate.enhance_maintenance_mode,
            SystemOverrideTemplate.enhance_trusted_integration,
        ]

        for _ in range(self.max_retries):
            try:
                # Randomly select an enhancement method
                method = random.choice(enhancement_methods)
                enhanced_attack = method(attack)

                # Basic validation - ensure the enhancement actually modified the attack
                if enhanced_attack and len(enhanced_attack.strip()) > len(
                    attack.strip()
                ):
                    return enhanced_attack

            except Exception:
                # If enhancement fails, try again with a different method
                continue

        # If all retries fail, return the original attack
        return attack

    async def a_enhance(self, attack: str) -> str:
        return self.enhance(attack)

    def get_name(self) -> str:
        return "System Override"
