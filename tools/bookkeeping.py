import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd
from colorama import Fore

prices = {
    'anthropic.claude-3-5-sonnet-20240620-v1:0': {
        'MInputTokens': 0.003 * 1000,
        'MOutputTokens': 0.015 * 1000,
    },
    'anthropic.claude-3-5-sonnet-20241022-v2:0': {
        'MInputTokens': 0.003 * 1000,
        'MOutputTokens': 0.015 * 1000,
    },
    'amazon.nova-pro-v1:0': {
        'MInputTokens': 0.0008 * 1000,
        'MOutputTokens': 0.0032 * 1000,
    },
    'amazon.nova-lite-v1:0': {
        'MInputTokens': 0.00006 * 1000,
        'MOutputTokens': 0.00024 * 1000,
    },
    'gpt-4.1-mini-2025-04-14': {
        'MInputTokens': 0.40,
        'MOutputTokens': 1.60,
    },
    'azure/gpt-4.1-mini': {
        'MInputTokens': 0.40,
        'MOutputTokens': 1.60,
    },
    'gpt-4.1-2025-04-14': {
        'MInputTokens': 2.00,
        'MOutputTokens': 8.00,
    },
    'claude-3-5-haiku-latest': {
        'MInputTokens': 0.80,
        'MOutputTokens': 4,
    },
}


def parse_log_file_with_pandas(log_file_path, token_sums):
    try:
        df = pd.read_csv(log_file_path)
        for _, row in df.iterrows():
            key = f"{row['source'].strip()}-{row['model'].strip()}"
            token_sums[key]['inputTokens'] += int(row['input_tokens'])
            token_sums[key]['outputTokens'] += int(row['output_tokens'])
            token_sums[key]['model'] = row['model'].strip()
    except pd.errors.ParserError:
        print(f"{Fore.RED}Error: File '{log_file_path}' is not a valid CSV file.{Fore.RESET}")
        return False
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to process '{log_file_path}': {str(e)}{Fore.RESET}")
        return False
    return True


def print_costs(token_sums, prices):
    total_cost = 0
    for key, tokens in token_sums.items():
        if tokens['model'] in prices:
            price = prices[tokens['model']]
            input_cost = tokens['inputTokens'] / 1_000_000 * price['MInputTokens']
            output_cost = tokens['outputTokens'] / 1_000_000 * price['MOutputTokens']
            total_cost += input_cost + output_cost
            print(
                f"{key}, Input Tokens: {tokens['inputTokens']}, Output Tokens: {tokens['outputTokens']}, Input Cost: ${input_cost}, Output Cost: ${output_cost}"
            )
        else:
            print(f"{key}, Input Tokens: {tokens['inputTokens']}, Output Tokens: {tokens['outputTokens']}")

    print(f'Total cost: ${total_cost}')


def sum_tokens(log_file_path):
    token_sums = defaultdict(lambda: {'inputTokens': 0, 'outputTokens': 0})
    if not parse_log_file_with_pandas(log_file_path, token_sums):
        return
    print_costs(token_sums, prices)


def main():
    print(f'{Fore.YELLOW}WARNING! Costs are hard coded and should be verified.{Fore.RESET}')

    parser = argparse.ArgumentParser(description='Process token usage and calculate costs.')
    parser.add_argument('filename', help='Path to the log file to process')

    args = parser.parse_args()

    # Use the provided filename for log_file_path
    log_file_path = Path(args.filename)
    sum_tokens(log_file_path=log_file_path)


if __name__ == '__main__':
    main()
