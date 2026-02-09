"""
Shared core prompt for Completeness metric.
"""

POSSIBLE_RESPONSES = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']

CORE_PROMPT = """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question, a candidate response from LLM and a reference response. Your task is to check if the candidate response contain the necessary amount of information and details for answering the question.

					When evaluating the completeness of the response, consider the following rubrics:

					1. Compare the candidate response and the reference response.
					- Identify any crucial information or key points that are present in the reference response but missing from the candidate response.
					- Focus on the main ideas and concepts that directly address the question, rather than minor details.
					- If a specific number of items or examples is requested, check that the candidate response provides the same number as the reference response.

					2. Does the candidate response provide sufficient detail and information for the task, compared to the reference response? For example,
					- For summaries, check if the main points covered in the candidate response match the core ideas in the reference response.
					- For step-by-step solutions or instructions, ensure that the candidate response doesn't miss any critical steps present in the reference response.
					- In customer service interactions, verify that all essential information provided in the reference response is also present in the candidate response.
					- For stories, emails, or other written tasks, ensure that the candidate response includes the key elements and main ideas as the reference response.
					- In rewriting or editing tasks, check that critical information has not been removed from the reference response.
					- For multiple-choice questions, if the reference response selects "all of the above" or a combination of options, the candidate response should do the same.

					3. Consider the implicit assumptions and requirements for the task, based on the reference response.
					- Different audiences or lengths may require different levels of detail in summaries, as demonstrated by the reference response. Focus on whether the candidate response meets the core requirements.

					Please rate the completeness of the candidate response based on the following scale:

					- Not at all: None of the necessary information and detail is present.
					- Not generally: Less than half of the necessary information and detail is present.
					- Neutral/Mixed: About half of the necessary information and detail is present, or it's unclear what the right amount of information is.
					- Generally yes: Most of the necessary information and detail is present.
					- Yes: All necessary information and detail is present.


					Here is the actual task:
					Question: {prompt}
					Reference response: {ground_truth}
					Candidate response: {prediction}
"""
