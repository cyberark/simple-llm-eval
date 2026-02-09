"""
Shared core prompt for Correctness metric.
"""

POSSIBLE_RESPONSES = ['incorrect', 'partially correct', 'correct']

CORE_PROMPT = """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question, a candidate response from LLM and a reference response. Your task is to check if the candidate response is correct or not.

					A correct candidate response should contain the same semantic information as the reference response.

					Here is the actual task:
					Question: {prompt}
					Reference Response: {ground_truth}
					Candidate Response: {prediction}
"""
