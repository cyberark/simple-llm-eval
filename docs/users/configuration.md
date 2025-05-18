# Configuration ⚙️

## Eval Set Configuration ⛭

The eval set configuration file allows you to set:

* `name` - display name
* `max_concurrent_judge_tasks`: how many judge tasks to run concurrently
* `max_concurrent_llm_tasks`: how many llm tasks to run concurrently
* `eval_metrics`: list of metrics to evaluate. to learn about the available metrics, run `simpleval metrics-explorer`
* `llm_as_a_judge_name`: the model to use for the llm as a judge. Run `simpleval list-models` to see available judges.
* `llm_as_a_judge_model_id` (optional) - The model id to use for the `llm_as_a_judge_name` provider. Each judge comes with a default model-id, but you can set your own. Run `simpleval litellm-models-explorer` to see available models for Lite LLM judges.

### Override Eval Set Configuration ⛭

If you want to override the configuration for the testcase level, you can do this for `max_concurrent_judge_tasks` and/or `max_concurrent_llm_tasks` by setting the `override` config element with the testcase name you want to override.

For example:

```json
{
  "name": "detect_user_action",
  "max_concurrent_judge_tasks": 10,
  "max_concurrent_llm_tasks": 10,
  "eval_metrics": ["correctness", "relevance", "completeness"],
  "llm_as_a_judge_name": "open_ai",
  "override": {
    "nova_lite1": {
      "max_concurrent_judge_tasks": 5,
      "max_concurrent_llm_tasks": 5
    }
  }
}
```

## Global Configuration ⛭
The global configuration file allows you to override certain global settings.

Currently it supports setting the retry behavior for different models.

> Create a `global_config.json` in your working directory and populate it as you wish.
> You should see an indication in the terminal that the global configuration file was loaded.

### Retries Configuration ⛭

!!! warning
    This is an experimental feature and is not yet fully supported.

You can override the behavior of the retry mechanism for family of models.

This is useful if you keep hitting rate limits.

Supported models:

✅ `bedrock_claude_sonnet` (will work for any bedrock model)

Retries are using tenacity's `wait_random_exponential` function.
To learn more about the available options, see the [function documentation](https://tenacity.readthedocs.io/en/latest/api.html#tenacity.wait.wait_random_exponential)

The default values are:

```json
{
  "retry_configs": {
    "bedrock": {
      "stop_after_attempt": 5,
      "multiplier": 2,
      "min": 10,
      "max": 30,
      "exp_base": 2
    }
  }
}
```

>This means that it will stop after 5 attempts, has an initial window of 2s, will increase the wait time exponentially by a factor of 2, with a minimum of 10 seconds and up to a maximum of 30 seconds.

Update the values and paste into your global config file.

The global config schema is implemented in: `simpleval/global_config/retries.py`

<br>
