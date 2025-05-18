from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


class RelevanceMetric(BaseBedrockSonnetMetric):
    """
    Relevance - Looks at the model's responses and evaluates how relevant the answer is to question from the prompt.
    Responses are graded a 5-point lickert scale, and then normalized in the output and the job's report card.
    The {prompt} will contain the prompt sent to the generator from your dataset, and the {prediction} is the generator model's responses.
    """

    def __init__(self):
        super().__init__()

    @property
    def prefill(self) -> str:
        return 'Explanation:'

    @property
    def eval_prompt(self) -> str:
        return """
You are a helpful agent that can assess LLM response according to the given rubrics.

You are given a question and a response from LLM. Your task is to assess the relevance of the LLM response to the question, in other words, how focused the LLM response is on the given question.

The output saying “I don’t know” or “I can’t answer” is relevant. Telling the user that the model is unable to respond to their query, or adding a simple caveat or condition to the response, should be considered relevant. However, the model may say “I don’t know” and go on to say something irrelevant. In such a case, relevance should be penalized.

Please rate the relevance of the response based on the following scale:
- not at all: No part of the response is relevant to the question.
- slightly: An overwhelming amount of the response is irrelevant or the relevant information is not a direct answer.
- somewhat: Roughly half of the response is relevant to the question.
- mostly: An overwhelming amount of the response is relevant to the question.
- completely: Every piece of the response is relevant to the question.

Here is the actual task:
Question: {prompt}
Response: {prediction}

Firstly explain your response, followed by your final answer. You should follow the format
Explanation: [Explanation], Answer: [Answer],
where '[Answer]' can be one of the following:
```
not at all
slightly
somewhat
mostly
completely
```
        """

    @property
    def possible_responses(self) -> List[str]:
        return ['not at all', 'slightly', 'somewhat', 'mostly', 'completely']

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
