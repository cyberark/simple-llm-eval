"""
Core evaluation prompts shared between bedrock_claude_sonnet and litellm_structured_output metrics.

Each metric has:
- A core prompt containing the evaluation criteria and rubrics
- A list of possible responses for the metric
"""

from typing import List

# =============================================================================
# COHERENCE
# =============================================================================

COHERENCE_CORE_PROMPT = """
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

COHERENCE_POSSIBLE_RESPONSES: List[str] = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']


# =============================================================================
# COMPLETENESS
# =============================================================================

COMPLETENESS_CORE_PROMPT = """
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

COMPLETENESS_POSSIBLE_RESPONSES: List[str] = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']


# =============================================================================
# CORRECTNESS
# =============================================================================

CORRECTNESS_CORE_PROMPT = """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question, a candidate response from LLM and a reference response. Your task is to check if the candidate response is correct or not.

					A correct candidate response should contain the same semantic information as the reference response.

					Here is the actual task:
					Question: {prompt}
					Reference Response: {ground_truth}
					Candidate Response: {prediction}
"""

CORRECTNESS_POSSIBLE_RESPONSES: List[str] = ['incorrect', 'partially correct', 'correct']


# =============================================================================
# FAITHFULNESS
# =============================================================================

FAITHFULNESS_CORE_PROMPT = """
You are given a task in some context (Input), and a candidate answer. Is the candidate answer faithful to the task description and context?

					A response is unfaithful only when (1) it clearly contradicts the context, or (2) the task implies that the response must be based on the context, like in a summarization task. If the task does not ask to respond based on the context, the model is allowed to use its own knowledge to provide a response, even if its claims are not verifiable.

					Task: {prompt}

					Candidate Response: {prediction}

					Evaluate how much of the information in the answer is faithful to the available context.
"""

FAITHFULNESS_POSSIBLE_RESPONSES: List[str] = [
    'none is faithful',
    'some is faithful',
    'approximately half is faithful',
    'most is faithful',
    'all is faithful',
]


# =============================================================================
# FOLLOWING INSTRUCTIONS
# =============================================================================

FOLLOWING_INSTRUCTIONS_CORE_PROMPT = """
You are a helpful agent that can assess LLM response according to the given rubrics.

					You are given a question and a response from LLM. Your task is to determine whether the model's output respects all explicit parts of the instructions provided in the input, regardless of the overall quality or correctness of the response.

					The instructions provided in the input can be complex, containing specific, detailed parts. You can think of them as multiple constraints or requirements. Examples of explicit parts of instructions include:

					- Information that the model should use to answer the prompt (e.g., "Based on this text passage, give an overview about [...]")
					- Length of the output (e.g., "Summarize this text in one sentence")
					- Answer options (e.g., "Which of the following is the tallest mountain in Europe: K2, Mount Ararat, ...")
					- Target audience (e.g., "Write an explanation of value added tax for middle schoolers")
					- Genre (e.g., "Write an ad for a laundry service")
					- Style (e.g., "Write an ad for a sports car like it's an obituary.")
					- Type of content requested (e.g., "Write a body for this email based on the following subject line" vs "Write a subject line for this email")
					- And more...

					When evaluating, please limit yourself to considering only the explicit/visible parts of the instructions. The overall quality or correctness of the response is not relevant for this task. What matters is whether all parts of the instruction are addressed and generally respected.

					Additionally, keep in mind the following guidelines:

					- If the model gives a purely evasive response without even a partial answer or a related answer, rate this as "Yes" for following detailed instructions.
					- If the model gives a partially evasive response but does provide a partial answer or a related answer, then judge the partial answer as to whether it follows the detailed instructions.

					You should answer with one of the following options:

					- "Not applicable" if there are no explicit instructions in the input (i.e., the request is completely implicit, or there is no clear request).
					- "Yes" if all explicit requests in the input are satisfied in the output.
					- "No" if any of the explicit requests in the input are not satisfied in the output.


					Here is the actual task:
					Question: {prompt}
					Response: {prediction}
"""

FOLLOWING_INSTRUCTIONS_POSSIBLE_RESPONSES: List[str] = ['No', 'Not applicable', 'Yes']


# =============================================================================
# HELPFULNESS
# =============================================================================

HELPFULNESS_CORE_PROMPT = """
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
* when desirable, is the completion interesting? Is the completion likely to "catch someone's attention" or "arouse their curiosity", or is it unexpected in a positive way, witty or insightful? when not desirable, is the completion plain, sticking to a default or typical answer or format?
* for math, coding, and reasoning problems: is the solution simple, and efficient, or even elegant?
* for chat contexts: is the completion a single chatbot turn marked by an appropriate role label?


Task: {prompt}
Candidate Response: {prediction}
"""

HELPFULNESS_POSSIBLE_RESPONSES: List[str] = [
    'not helpful at all',
    'very unhelpful',
    'somewhat unhelpful',
    'neither helpful nor unhelpful',
    'somewhat helpful',
    'very helpful',
    'above and beyond',
]


# =============================================================================
# NO GROUND TRUTH
# =============================================================================

NO_GROUND_TRUTH_CORE_PROMPT = """
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

NO_GROUND_TRUTH_POSSIBLE_RESPONSES: List[str] = ['Not at all', 'Not generally', 'Neutral/Mixed', 'Generally yes', 'Yes']


# =============================================================================
# NO GROUND TRUTH SIMPLE
# =============================================================================

NO_GROUND_TRUTH_SIMPLE_CORE_PROMPT = """
You are given a task and a candidate response. Is this a correct and accurate response to the task?

					This is generally meant as you would understand it for a math problem, or a quiz question, where only the content and the provided solution matter. Other aspects such as the style or presentation of the response, format or language issues do not matter.

					Task: {prompt}
					Candidate Response: {prediction}
"""

NO_GROUND_TRUTH_SIMPLE_POSSIBLE_RESPONSES: List[str] = ['incorrect', 'partially correct', 'correct']


# =============================================================================
# PRO STYLE AND TONE
# =============================================================================

PRO_STYLE_AND_TONE_CORE_PROMPT = """
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

PRO_STYLE_AND_TONE_POSSIBLE_RESPONSES: List[str] = ['not at all', 'not generally', 'neutral/mixed', 'generally yes', 'completely yes']


# =============================================================================
# READABILITY
# =============================================================================

READABILITY_CORE_PROMPT = """
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

READABILITY_POSSIBLE_RESPONSES: List[str] = ['unreadable', 'poor readability', 'fair readability', 'good readability', 'excellent readability']


# =============================================================================
# RELEVANCE
# =============================================================================

RELEVANCE_CORE_PROMPT = """
You are a helpful agent that can assess LLM response according to the given rubrics.

You are given a question and a response from LLM. Your task is to assess the relevance of the LLM response to the question, in other words, how focused the LLM response is on the given question.

The output saying "I don't know" or "I can't answer" is relevant. Telling the user that the model is unable to respond to their query, or adding a simple caveat or condition to the response, should be considered relevant. However, the model may say "I don't know" and go on to say something irrelevant. In such a case, relevance should be penalized.

Please rate the relevance of the response based on the following scale:
- not at all: No part of the response is relevant to the question.
- slightly: An overwhelming amount of the response is irrelevant or the relevant information is not a direct answer.
- somewhat: Roughly half of the response is relevant to the question.
- mostly: An overwhelming amount of the response is relevant to the question.
- completely: Every piece of the response is relevant to the question.

Here is the actual task:
Question: {prompt}
Response: {prediction}
"""

RELEVANCE_POSSIBLE_RESPONSES: List[str] = ['not at all', 'slightly', 'somewhat', 'mostly', 'completely']
