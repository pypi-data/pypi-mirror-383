from typing import List, Optional
from enum import Enum
from pydantic import model_validator
from deepeval.test_case import LLMTestCase, Turn


class RTTurn(Turn):
    turn_level_attack: Optional[str] = None


class RTTestCase(LLMTestCase):
    vulnerability: str
    input: Optional[str] = None
    actual_output: Optional[str] = None
    turns: Optional[List[RTTurn]] = None
    metadata: Optional[dict] = None
    vulnerability_type: Enum = None
    attack_method: Optional[str] = None
    risk_category: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None
    error: Optional[str] = None

    # @model_validator(mode="before")
    # def validate_input(cls, data):
    #     vulnerability = data.get("vulnerability")
    #     input = data.get("input")
    #     actual_output = data.get("actual_output")
    #     turns = data.get("turns")
    #     vulnerability_type = data.get("vulnerability_type")
    #     metadata = data.get("metadata")
    #     attack_method = data.get("attack_method")
    #     risk_category = data.get("risk_category")
    #     score = data.get("score")
    #     reason = data.get("reason")
    #     error = data.get("error")

    #     if input is not None:
    #         if not isinstance(input, str):
    #             raise TypeError("'input' must be a string")

    #     if actual_output is not None:
    #         if not isinstance(actual_output, str):
    #             raise TypeError("'actual_output' must be a string")

    #     if turns is not None:
    #         if not isinstance(turns, list) or not all(
    #             isinstance(turn, RTTurn) for turn in turns
    #         ):
    #             raise TypeError("'turns' must be a list of 'RTTurn'")

    #     if actual_output is not None and turns is not None:
    #         raise ValueError(
    #             "An 'RTTestCase' cannot contain both 'actual_output' and 'turns' at the same time."
    #         )

    #     if vulnerability is not None:
    #         if not isinstance(vulnerability, str):
    #             raise TypeError("'vulnerability' must be a string")

    #     if vulnerability_type is not None:
    #         if not isinstance(vulnerability, str):
    #             raise TypeError("'vulnerability_type' must be an Enum")

    #     if metadata is not None:
    #         if not isinstance(metadata, dict):
    #             raise TypeError("'metadata' must be a dictionary")

    #     if attack_method is not None:
    #         if not isinstance(attack_method, str):
    #             raise TypeError("'attack_method' must be a string")

    #     if risk_category is not None:
    #         if not isinstance(risk_category, str):
    #             raise TypeError("'risk_category' must be a string")

    #     if score is not None:
    #         if not isinstance(score, float):
    #             raise TypeError("'score' must be a float")

    #     if reason is not None:
    #         if not isinstance(reason, str):
    #             raise TypeError("'reason' must be a string")

    #     if error is not None:
    #         if not isinstance(error, str):
    #             raise TypeError("'error' must be a string")

    #     return data
