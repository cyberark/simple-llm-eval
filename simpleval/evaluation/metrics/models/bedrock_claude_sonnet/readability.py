from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


class ReadabilityMetric(BaseBedrockSonnetMetric):
    """
    Readability - Looks at the model's responses and evaluates the terminological and linguistic complexity of the response.
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

You are given a question and a response from LLM. Your task is to assess the readability of the LLM response to the question, in other words, how easy it is for a typical reading audience to comprehend the response at a normal reading rate.

Please rate the readability of the response based on the following scale:
- unreadable: The response contains gibberish or could not be comprehended by any normal audience.
- poor readability: The response is comprehensible, but it is full of poor readability factors that make comprehension very challenging.
- fair readability: The response is comprehensible, but there is a mix of poor readability and good readability factors, so the average reader would need to spend some time processing the text in order to understand it.
- good readability: Very few poor readability factors. Mostly clear, well-structured sentences. Standard vocabulary with clear context for any challenging words. Clear organization with topic sentences and supporting details. The average reader could comprehend by reading through quickly one time.
- excellent readability: No poor readability factors. Consistently clear, concise, and varied sentence structures. Simple, widely understood vocabulary. Logical organization with smooth transitions between ideas. The average reader may be able to skim the text and understand all necessary points.

Here is the actual task:
Question: {prompt}
Response: {prediction}

Firstly explain your response, followed by your final answer. You should follow the format
Explanation: [Explanation], Answer: [Answer],
where '[Answer]' can be one of the following:
```
unreadable
poor readability
fair readability
good readability
excellent readability
```
        """

    @property
    def possible_responses(self) -> List[str]:
        return ['unreadable', 'poor readability', 'fair readability', 'good readability', 'excellent readability']

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
