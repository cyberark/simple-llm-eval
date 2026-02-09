"""
Shared core prompt for Readability metric.
"""

POSSIBLE_RESPONSES = ['unreadable', 'poor readability', 'fair readability', 'good readability', 'excellent readability']

CORE_PROMPT = """
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
"""
