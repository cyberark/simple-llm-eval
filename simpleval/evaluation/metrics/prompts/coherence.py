"""
Shared core prompt for Coherence metric.
"""

POSSIBLE_RESPONSES = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']

CORE_PROMPT = """
You are a helpful agent that can assess LLM response according to the given rubrics.

        You are given a question and a response from LLM. Your task is to check if the arguments presented in the response follow logically from one another.

        When evaluating the logical cohesion of the response, consider the following rubrics:

        1. Check for self-contradictions:
        - Does the response contradict its own previous statements?
        - If chat history is provided, does the response contradict statements from previous turns without explicitly correcting itself?

        2. Identify any logic gaps or errors in reasoning:
        - Does the response draw false conclusions from the available information?
        - Does it make "logical leaps" by skipping steps in an argument?
        - Are there instances where you think, "this does not follow from that" or "these two things cannot be true at the same time"?

        3. Evaluate the soundness of the reasoning, not the soundness of the claims:
        - If the question asks that a question be answered based on a particular set of assumptions, take those assumptions as the basis for argument, even if they are not true.
        - Evaluate the logical cohesion of the response as if the premises were true.

        4. Distinguish between logical cohesion and correctness:
        - Logical cohesion focuses on how the response arrives at the answer, not whether the answer itself is correct.
        - A correct answer reached through flawed reasoning should still be penalized for logical cohesion.

        5. Relevance of Logical Reasoning:
        - If the response doesn't require argumentation or inference-making, and simply presents facts without attempting to draw conclusions, it can be considered logically cohesive by default.
        - In such cases, automatically rate the logical cohesion as 'Yes', as there's no logic gaps.

        Please rate the logical cohesion of the response based on the following scale:

        - Not at all: The response contains too many errors of reasoning to be usable, such as contradicting itself, major gaps in reasoning, or failing to present any reasoning where it is required.
        - Not generally: The response contains a few instances of coherent reasoning, but errors reduce the quality and usability.
        - Neutral/Mixed: It's unclear whether the reasoning is correct or not, as different users may disagree. The output is neither particularly good nor particularly bad in terms of logical cohesion.
        - Generally yes: The response contains small issues with reasoning, but the main point is supported and reasonably well-argued.
        - Yes: There are no issues with logical cohesion at all. The output does not contradict itself, and all reasoning is sound.


        Here is the actual task:
        Question: {prompt}
        Response: {prediction}
"""
