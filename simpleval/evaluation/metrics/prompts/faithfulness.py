"""
Shared core prompt for Faithfulness metric.
"""

POSSIBLE_RESPONSES = [
    'none is faithful',
    'some is faithful',
    'approximately half is faithful',
    'most is faithful',
    'all is faithful',
]

CORE_PROMPT = """
You are given a task in some context (Input), and a candidate answer. Is the candidate answer faithful to the task description and context?

					A response is unfaithful only when (1) it clearly contradicts the context, or (2) the task implies that the response must be based on the context, like in a summarization task. If the task does not ask to respond based on the context, the model is allowed to use its own knowledge to provide a response, even if its claims are not verifiable.

					Task: {prompt}

					Candidate Response: {prediction}

					Evaluate how much of the information in the answer is faithful to the available context.
"""
