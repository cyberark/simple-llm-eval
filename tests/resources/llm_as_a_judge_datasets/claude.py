import json
import logging

import boto3

from simpleval.consts import LOGGER_NAME

bedrock = boto3.client(service_name='bedrock-runtime')

model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
accept = 'application/json'
content_type = 'application/json'

logger = logging.getLogger(LOGGER_NAME)


def call_claude_completion(role: str, system_prompt: str, user_prompt: str, prefill: str = '', temperature: int = 0,
                           max_tokens_to_sample: int = 50):
    body_dict = _get_claude_body_dict(role=role, system_prompt=system_prompt, user_prompt=user_prompt, prefill=prefill,
                                      temperature=temperature, max_tokens_to_sample=max_tokens_to_sample)
    body = json.dumps(body_dict)

    response = bedrock.invoke_model(body=body, modelId=model_id, accept=accept, contentType=content_type)

    result = json.loads(response.get('body').read())
    input_tokens = result.get('usage', {}).get('input_tokens', '')
    output_tokens = result.get('usage', {}).get('output_tokens', '')
    output_list = result.get('content', [])

    # print(f'{input_tokens=}, {output_tokens=}')

    # if not output_list:
    #     print('empty response')
    # else:
    #     output = output_list[0].get('text', '')

    logger.info(f'Claude completion response: {output_list}, {input_tokens=}, {output_tokens=}')
    output = output_list[0].get('text', '')

    # Note that if you include the { as the prefill, it will not be included in the response so we need it ourselves, see cookbook link:
    # https://github.com/anthropics/anthropic-cookbook/blob/main/misc/how_to_enable_json_mode.ipynb
    output = prefill + output
    return output.strip()


def _get_claude_body_dict(role: str, system_prompt: str, user_prompt: str, prefill: str, temperature: int,
                          max_tokens_to_sample: int) -> dict:
    body_dict = {
        'anthropic_version':
            'bedrock-2023-05-31',
        'system':
            system_prompt.strip(),
        'max_tokens':
            max_tokens_to_sample,
        'messages': [
            {
                'role': 'user',
                'content': [{
                    'type': 'text',
                    'text': user_prompt.strip()
                }],
            },
            # {
            #     'role':
            #         'assistant',
            #     'content': [{
            #         'type': 'text',
            #         'text':
            #             f'[{role}]{prefill} {{'  # see https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response
            #     }],
            # }
        ],
    }

    body_dict['temperature'] = temperature
    # body_dict['stop_sequences'] =
    # body_dict['top_k'] = top_k # using default
    # body_dict['top_p'] = top_p  # using default

    return body_dict
