# Bookkeeping 🔢

By default the number of input/output tokens and the model used is logged using `logs/tokens-bookkeeping.log`
It is called in each judge implementation and if other judges are created, you should also log their token usage.

If you're using simpleval and implementing your own handlers, then it is advised to also log the token usage,
as shown in `simpleval/eval_sets/empty/testcases/empty/task_handler.py`

The log format include the time, source (eval, handler etc), input and output tokens


| time                  | source | model                | input_tokens | output_tokens |
| --------------------- | -------| ---------------------|------------- | --------------|
| `2025-03-19 16:11:04` | `eval` | `gpt-4.1-2025-04-14` | 267          | 127           |

`source` is determined by the caller of the `log_bookkeeping_data` function.

!!! tip
    When implementing a new testcase handler (plugin) or a new judge, you should also log the token usage.
    <br>
    This is done by calling `log_bookkeeping_data` after your call to the model.

## Bookkeeping summary
You can use the `dev_utils/bookkeeping.py` to summarize the bookkeeping data. 
This includes hard-coded pricing.
Update as needed.

<br>
