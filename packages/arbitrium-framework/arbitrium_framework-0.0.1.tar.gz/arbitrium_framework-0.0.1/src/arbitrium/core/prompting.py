"""Prompt building for Arbitrium Framework."""

from typing import Any

from arbitrium.core.prompt_templates import (
    EVALUATION_PROMPT_TEMPLATE,
    FEEDBACK_HEADER,
    FEEDBACK_PROMPT_TEMPLATE,
    FEEDBACK_WRAPPER,
    IMPROVEMENT_PROMPT_TEMPLATE,
    INITIAL_PROMPT_TEMPLATE,
    KNOWLEDGE_BANK_HEADER,
    OTHER_RESPONSES_HEADER,
    RESPONSE_WRAPPER,
)
from arbitrium.models.base import BaseModel


class PromptBuilder:
    """Builds prompts for the different phases of the tournament."""

    def __init__(self, prompts: dict[str, str]):
        """Initialize the prompt builder."""
        self.prompts = prompts

    def _format_prompt(self, prompt_type: str, context: dict[str, Any]) -> str:
        """Formats a prompt using a unified prompt type (initial, feedback, improvement, evaluate)."""
        prompt_template = self.prompts.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Prompt type '{prompt_type}' not found in config. Available: {list(self.prompts.keys())}")
        return prompt_template.format(**context)

    def _build_feedback_context(self, improvement_context: dict[str, dict[str, str]] | None, display_name: str) -> str:
        """Build feedback context text for improvement prompt."""
        if not improvement_context:
            return ""
        feedbacks = improvement_context.get(display_name, {})
        if not feedbacks:
            return ""
        return "\n\n".join(FEEDBACK_WRAPPER.format(reviewer=reviewer, text=text) for reviewer, text in feedbacks.items())

    def _build_other_responses_context(
        self,
        other_responses: dict[str, str] | None,
        display_name: str,
        model: BaseModel,
        own_answer: str,
        initial_question: str,
    ) -> str:
        """Build other responses context text for improvement prompt."""
        if not other_responses:
            return ""
        filtered = {k: v for k, v in other_responses.items() if k != display_name}
        if not filtered:
            return ""

        responses = []
        for name, resp in filtered.items():
            responses.append(RESPONSE_WRAPPER.format(name=name, response=resp))

        return "\n\n".join(responses)

    def _build_full_improvement_context(self, context_text: str, other_responses_text: str) -> str:
        """Combine feedback and other responses into full context."""
        full_context = ""
        if context_text:
            full_context += FEEDBACK_HEADER.format(feedback_text=context_text)
        if other_responses_text:
            if full_context:
                full_context += "\n\n"
            full_context += OTHER_RESPONSES_HEADER.format(responses_text=other_responses_text)
        return full_context

    def build_initial_prompt(self, initial_question: str) -> str:
        """Build the initial prompt for the first round."""
        base_prompt = self._format_prompt("initial", context={})
        return INITIAL_PROMPT_TEMPLATE.format(base_prompt=base_prompt, question=initial_question)

    def build_feedback_prompt(
        self,
        initial_question: str,
        target_answer: str,
        feedback_instruction: str,
    ) -> str:
        """Build the prompt for the feedback phase."""
        base_prompt = self._format_prompt("feedback", context={})
        return FEEDBACK_PROMPT_TEMPLATE.format(
            feedback_instruction=feedback_instruction,
            base_prompt=base_prompt,
            question=initial_question,
            answer=target_answer,
        )

    def build_improvement_prompt(
        self,
        initial_question: str,
        own_answer: str,
        improvement_instruction: str,
        kb_context: str,
        improvement_context: dict[str, dict[str, str]] | None,
        other_responses: dict[str, str] | None,
        model: BaseModel,
        display_name: str,
    ) -> str:
        """Build the prompt for the improvement phase."""
        context_text = self._build_feedback_context(improvement_context, display_name)
        other_responses_text = self._build_other_responses_context(other_responses, display_name, model, own_answer, initial_question)
        full_context = self._build_full_improvement_context(context_text, other_responses_text)

        base_prompt = self._format_prompt("improvement", context={})

        context_section = f"\n\n{full_context}" if full_context else ""
        knowledge_section = f"\n\n{KNOWLEDGE_BANK_HEADER.format(knowledge_text=kb_context)}" if kb_context else ""

        return IMPROVEMENT_PROMPT_TEMPLATE.format(
            improvement_instruction=improvement_instruction,
            base_prompt=base_prompt,
            question=initial_question,
            answer=own_answer,
            context_section=context_section,
            knowledge_section=knowledge_section,
        )

    def build_evaluation_prompt(
        self,
        initial_question: str,
        evaluation_template: str,
        formatted_responses: str,
        model_names: list[str] | None = None,
    ) -> str:
        """Builds the detailed prompt for the evaluation phase."""
        base_prompt = self._format_prompt("evaluate", context={})

        # Generate a list of models that need to be scored (for clarity)
        models_list = "\n".join([f"- {name}" for name in sorted(model_names)]) if model_names else "- LLM1\n- LLM2\n- LLM3"

        return EVALUATION_PROMPT_TEMPLATE.format(
            base_prompt=base_prompt,
            question=initial_question,
            responses=formatted_responses,
            model_name=models_list,  # This replaces {model_name} placeholder
        )
