"""
Shared core prompt for No Ground Truth Simple metric.
"""

POSSIBLE_RESPONSES = ['incorrect', 'partially correct', 'correct']

CORE_PROMPT = """
You are given a task and a candidate response. Is this a correct and accurate response to the task?

					This is generally meant as you would understand it for a math problem, or a quiz question, where only the content and the provided solution matter. Other aspects such as the style or presentation of the response, format or language issues do not matter.

					Task: {prompt}
					Candidate Response: {prediction}
"""
