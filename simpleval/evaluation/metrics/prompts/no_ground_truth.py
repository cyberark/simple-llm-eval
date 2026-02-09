"""
Shared core prompt for No Ground Truth metric.
"""

POSSIBLE_RESPONSES = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']

CORE_PROMPT = """
You are an expert evaluator focusing specifically on assessing the completeness of responses.

					You will be presented with an Input (the original request/question) and an Output (the response to be evaluated). Your task is to determine whether an Output contains all the necessary information and detail to properly answer the Input.

					Rate the Output's completeness using only one of these five options:
					- Not at all: None of the necessary information/detail present; completely unusable
					- Not generally: Less than half of necessary information/detail present
					- Neutral/Mixed: About half of necessary information/detail present, or unclear
					- Generally yes: Most necessary information/detail present
					- Yes: All necessary information and detail present

					Key evaluation principles:
					1. Focus only on whether required information is present, not on:
					- Accuracy of information
					- Additional irrelevant information
					- Writing style or coherence

					2. Consider an Output incomplete if it:
					- Misses any explicitly requested items
					- Fails to address all parts of multi-part requests
					- Provides insufficient detail for the context
					- Misunderstands or ignores the Input

					3. For evasive responses:
					- If fully evasive ("I can't answer that"), rate as "Yes, completely"
					- If partially evasive with some information, evaluate the provided portion
					- If evasive when information was available, rate as incomplete

					4. For numbered requests (e.g., "list 10 items"):
					- Missing items lower the completeness rating
					- Exception: If Output explains why full count isn't possible

					Here is the actual task:
					Input: {prompt}
					Output: {prediction}
"""
