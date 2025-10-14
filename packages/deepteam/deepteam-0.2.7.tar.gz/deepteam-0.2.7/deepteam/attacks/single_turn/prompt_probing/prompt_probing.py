from tqdm import tqdm  # Sync version
from tqdm.asyncio import tqdm as async_tqdm_bar  # Async version
from typing import Optional, Union

from deepeval.metrics.utils import initialize_model
from deepeval.models import DeepEvalBaseLLM

from deepteam.attacks.single_turn import BaseSingleTurnAttack
from deepteam.attacks.single_turn.prompt_probing.template import (
    PromptProbingTemplate,
)
from deepteam.attacks.single_turn.prompt_probing.schema import (
    EnhancedAttack,
    ComplianceData,
    IsPromptProbing,
)
from deepteam.attacks.attack_simulator.utils import (
    generate,
    a_generate,
)


class PromptProbing(BaseSingleTurnAttack):

    def __init__(self, weight: int = 1, max_retries: int = 3):
        self.weight = weight
        self.max_retries = max_retries

    def enhance(
        self,
        attack: str,
        simulator_model: Optional[Union[DeepEvalBaseLLM, str]] = None,
    ) -> str:
        self.simulator_model, _ = initialize_model(simulator_model)
        prompt = PromptProbingTemplate.enhance(attack)

        # Progress bar for retries (total count is double the retries: 1 for generation, 1 for compliance check)
        with tqdm(
            total=self.max_retries * 3,
            desc="...... 🔎 Prompt Probing",
            unit="step",
            leave=False,
        ) as pbar:

            for _ in range(self.max_retries):
                # Generate the enhanced attack
                res: EnhancedAttack = generate(
                    prompt, EnhancedAttack, self.simulator_model
                )
                enhanced_attack = res.input
                pbar.update(1)  # Update the progress bar for generation

                # Check for compliance using a compliance template
                compliance_prompt = PromptProbingTemplate.non_compliant(
                    res.model_dump()
                )
                compliance_res: ComplianceData = generate(
                    compliance_prompt, ComplianceData, self.simulator_model
                )
                pbar.update(1)  # Update the progress bar for compliance

                # Check if rewritten prompt is a prompt probing attack
                is_prompt_probing_prompt = (
                    PromptProbingTemplate.is_prompt_probing(res.model_dump())
                )
                is_prompt_probing_res: IsPromptProbing = generate(
                    is_prompt_probing_prompt,
                    IsPromptProbing,
                    self.simulator_model,
                )
                pbar.update(1)  # Update the progress bar

                if (
                    not compliance_res.non_compliant
                    and is_prompt_probing_res.is_prompt_probing
                ):
                    # If it's compliant and is a prompt probing attack, return the enhanced prompt
                    return enhanced_attack

        # If all retries fail, return the original attack
        return attack

    async def a_enhance(
        self,
        attack: str,
        simulator_model: Optional[Union[DeepEvalBaseLLM, str]] = None,
    ) -> str:
        self.simulator_model, _ = initialize_model(simulator_model)
        prompt = PromptProbingTemplate.enhance(attack)

        # Async progress bar for retries (double the count to cover both generation and compliance check)
        pbar = async_tqdm_bar(
            total=self.max_retries * 3,
            desc="...... 🔎 Prompt Probing",
            unit="step",
            leave=False,
        )

        try:
            for _ in range(self.max_retries):
                # Generate the enhanced attack asynchronously
                res: EnhancedAttack = await a_generate(
                    prompt, EnhancedAttack, self.simulator_model
                )
                enhanced_attack = res.input
                pbar.update(1)  # Update the progress bar for generation

                # Check for compliance using a compliance template
                compliance_prompt = PromptProbingTemplate.non_compliant(
                    res.model_dump()
                )
                compliance_res: ComplianceData = await a_generate(
                    compliance_prompt, ComplianceData, self.simulator_model
                )
                pbar.update(1)  # Update the progress bar for compliance

                # Check if rewritten prompt is a prompt probing attack
                is_prompt_probing_prompt = (
                    PromptProbingTemplate.is_prompt_probing(res.model_dump())
                )
                is_prompt_probing_res: IsPromptProbing = await a_generate(
                    is_prompt_probing_prompt,
                    IsPromptProbing,
                    self.simulator_model,
                )
                pbar.update(1)  # Update the progress bar

                if (
                    not compliance_res.non_compliant
                    and is_prompt_probing_res.is_prompt_probing
                ):
                    # If it's compliant and is a prompt probing attack, return the enhanced prompt
                    return enhanced_attack

        finally:
            # Close the progress bar after the loop
            pbar.close()

        # If all retries fail, return the original attack
        return attack

    def get_name(self) -> str:
        return "Prompt Probing"
