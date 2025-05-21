from typing import Callable, List

from simpleval.evaluation.metrics.models.bedrock_claude_sonnet.base.base_metric import BaseBedrockSonnetMetric
from simpleval.evaluation.metrics.parsers.output_parsing import parse_explanation_answer_output


class HelpfulnessMetric(BaseBedrockSonnetMetric):
    """
    Helpfullness - Looks at how helpful the generator model's responses are in the context of several factors.
    These factors include X, Y, and Z. Responses are graded a 7-point lickert scale,
    and then normalized in the output and the job's report card.
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
You are given a task and a candidate completion. Provide a holistic evaluation of how helpful the completion is taking the below factors into consideration.


Helpfulness can be seen as 'eager and thoughtful cooperation': an completion is helpful when it satisfied explicit and implicit expectations in the user's request. Often this will mean that the completion helps the user achieve the task.
When the request is not clearly a task, like a random text continuation, or an answer directly to the model, consider what the user's general motifs are for making the request.
Not all factors will be applicable for every kind of request. For the factors applicable, the more you would answer with yes, the more helpful the completion.
* is the completion sensible, coherent, and clear given the current context, and/or what was said previously?
* if the goal is to solve a task, does the completion solve the task?
* does the completion follow instructions, if provided?
* does the completion respond with an appropriate genre, style, modality (text/image/code/etc)?
* does the completion respond in a way that is appropriate for the target audience?
* is the completion as specific or general as necessary?
* is the completion as concise as possible or as elaborate as necessary?
* does the completion avoid unnecessary content and formatting that would make it harder for the user to extract the information they are looking for?
* does the completion anticipate the user's needs and implicit expectations? e.g. how to deal with toxic content, dubious facts; being sensitive to internationality
* when desirable, is the completion interesting? Is the completion likely to “catch someone's attention” or “arouse their curiosity”, or is it unexpected in a positive way, witty or insightful? when not desirable, is the completion plain, sticking to a default or typical answer or format?
* for math, coding, and reasoning problems: is the solution simple, and efficient, or even elegant?
* for chat contexts: is the completion a single chatbot turn marked by an appropriate role label?


Task: {prompt}
Candidate Response: {prediction}

Firstly explain your response, followed by your final answer. You should follow the format
Explanation: [Explanation], Answer: [Answer],
where '[Answer]' can be one of the following:
```
above and beyond
very helpful
somewhat helpful
neither helpful nor unhelpful
somewhat unhelpful
very unhelpful
not helpful at all
```
        """

    @property
    def possible_responses(self) -> List[str]:
        return [
            'not helpful at all',
            'very unhelpful',
            'somewhat unhelpful',
            'neither helpful nor unhelpful',
            'somewhat helpful',
            'very helpful',
            'above and beyond',
        ]

    @property
    def parser(self) -> Callable:
        """
        The parser that converts the model's output into a structured format.
        """
        return parse_explanation_answer_output
