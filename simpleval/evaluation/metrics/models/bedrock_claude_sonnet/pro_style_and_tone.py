from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


class ProStyleToneMetric(BaseBedrockSonnetMetric):
    """
    Professional style and tone metric evaluates the appropriateness of the style, formatting,
    and tone of a response for professional genres.
    Responses are graded on a 5-point Likert scale, then normalized in the output and the job's report card.
    The {prompt} contains the prompt sent to the generator from your dataset, and the {prediction} is the generator model's response.
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

You are given a question and a response from LLM. Your task is to assess the quality of the LLM response as to professional style and tone. In other words, you should assess whether the LLM response is written with a professional style and tone, like something people might see in a company-wide memo at a corporate office. Please assess by strictly following the specified evaluation criteria and rubrics.

Focus only on style and tone: This question is about the language, not the correctness of the answer. So a patently incorrect or irrelevant answer would still get a “Yes, no editing is needed“-rating if it is the right genre of text, with correct spelling and punctuation.

Don’t focus on naturalness and fluency: A typical business setting includes people who speak different variants of English. Don’t penalize the output for using word choice or constructions that you don’t agree with, as long as the professionalism isn’t affected.

For evasive and I don’t know responses, consider the same principles. Most of the time when a model provides a simple evasion, it will get a “yes” for this dimension. But if the model evades in a way that does not embody a professional style and tone, it should be penalized in this regard.

Please rate the professional style and tone of the response based on the following scale:
- not at all: The response has major elements of style and/or tone that do not fit a professional setting. Almost none of it is professional.
- not generally: The response has some elements that would fit a professional setting, but most of it does not.
- neutral/mixed: The response is a roughly even mix of professional and unprofessional elements.
- generally yes: The response almost entirely fits a professional setting.
- completely yes: The response absolutely fits a professional setting. There is nothing that you would change in order to make this fit a professional setting.

Here is the actual task:
Question: {prompt}
Response: {prediction}

Firstly explain your response, followed by your final answer. You should follow the format
Explanation: [Explanation], Answer: [Answer],
where '[Answer]' can be one of the following:
```
not at all
not generally
neutral/mixed
generally yes
completely yes
```
        """

    @property
    def possible_responses(self) -> List[str]:
        return ['not at all', 'not generally', 'neutral/mixed', 'generally yes', 'completely yes']

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
