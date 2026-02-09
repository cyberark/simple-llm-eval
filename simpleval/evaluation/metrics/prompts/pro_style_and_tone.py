"""
Shared core prompt for Professional Style and Tone metric.
"""

POSSIBLE_RESPONSES = ['not at all', 'not generally', 'neutral/mixed', 'generally yes', 'completely yes']

CORE_PROMPT = """
You are a helpful agent that can assess LLM response according to the given rubrics.

You are given a question and a response from LLM. Your task is to assess the quality of the LLM response as to professional style and tone. In other words, you should assess whether the LLM response is written with a professional style and tone, like something people might see in a company-wide memo at a corporate office. Please assess by strictly following the specified evaluation criteria and rubrics.

Focus only on style and tone: This question is about the language, not the correctness of the answer. So a patently incorrect or irrelevant answer would still get a "Yes, no editing is needed"-rating if it is the right genre of text, with correct spelling and punctuation.

Don't focus on naturalness and fluency: A typical business setting includes people who speak different variants of English. Don't penalize the output for using word choice or constructions that you don't agree with, as long as the professionalism isn't affected.

For evasive and I don't know responses, consider the same principles. Most of the time when a model provides a simple evasion, it will get a "yes" for this dimension. But if the model evades in a way that does not embody a professional style and tone, it should be penalized in this regard.

Please rate the professional style and tone of the response based on the following scale:
- not at all: The response has major elements of style and/or tone that do not fit a professional setting. Almost none of it is professional.
- not generally: The response has some elements that would fit a professional setting, but most of it does not.
- neutral/mixed: The response is a roughly even mix of professional and unprofessional elements.
- generally yes: The response almost entirely fits a professional setting.
- completely yes: The response absolutely fits a professional setting. There is nothing that you would change in order to make this fit a professional setting.

Here is the actual task:
Question: {prompt}
Response: {prediction}
"""
