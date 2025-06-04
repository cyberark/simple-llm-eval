# Judge Models and Authentication  👩‍⚖️🔑

Simpleval supports several judges, each one with its own authentication method.
The way to authenticate with each judge is usually via environment variables or similar implicit methods.
There might also be judge-specific details found below.

You can see how each judge type is authenticated below, but in short, most judges are based on Lite LLM,
so you can always also refer to its documentation.

!!! tip
    You can view supported model ids for Lite LLM judges by running:

    ```bash
    simpleval litellm-models-explorer
    ```

???- note "Anthropic Judge"

    **Required environment variable:**

    ```
    ANTHROPIC_API_KEY
    ```

    Example:

    ```
    ANTHROPIC_API_KEY=<your-key>
    ```

    See the [Anthropic docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api) for more details.

???- note "Azure Judge"

    **Required environment variables:**

    ```
    AZURE_OPENAI_API_KEY
    AZURE_API_VERSION
    AZURE_API_BASE
    ```

    Example:

    ```
    AZURE_OPENAI_API_KEY=<your-key>
    AZURE_API_VERSION=2024-04-01-preview
    AZURE_API_BASE=https://<your_resource_name>.openai.azure.com/
    ```

    **Available Versions**

    You can see available versions in the [Azure docs](https://github.com/Azure/azure-rest-api-specs/tree/main/specification/cognitiveservices/resource-manager/Microsoft.CognitiveServices)

???- note "Bedrock Claude Sonnet Judge"

    This judge is **NOT** based on Lite LLM, it is implemented natively with boto3 calling Bedrock. 

    **Required credentials:**

    AWS credentials must be available, either via environment variables or in a `~/.aws/credentials` file.
    
    You can learn more about using AWS credentials in the [AWS docs](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html)
    
???- note "Gemini Judge"

    **Required environment variable:**

    ```
    GEMINI_API_KEY
    ```

    See the [Gemini API docs](https://ai.google.dev/gemini-api/docs/api-key) for more details.

???- note "OpenAI Judge"

    **Required environment variable:**

    ```
    OPENAI_API_KEY
    ```

    See the [OpenAI API docs](https://platform.openai.com/docs/api-reference/authentication) for more details.

???- note "Vertex AI Judge"

    **Required environment variable:**

    ```
    GOOGLE_APPLICATION_CREDENTIALS
    VERTEXAI_LOCATION
    VERTEXAI_PROJECT
    ```

    Example:

    ```
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
    VERTEXAI_LOCATION=us-central1
    VERTEXAI_PROJECT=your-project-id
    ```

    See the [Vertex AI docs](https://cloud.google.com/vertex-ai/docs/start/client-libraries#client-libraries-install-python) for more details.

???- note "Generic Bedrock Judge"

    **Required credentials:**

    AWS credentials must be available, either via environment variables or in a `~/.aws/credentials` file.

    You can learn more about using AWS credentials in the [AWS docs](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html)

???- note "LiteLLM Structured Output Judge"

    **Required authentication:**

    Depends on the provider you use with LiteLLM.

    You can learn about the available providers in the [LiteLLM documentation](https://docs.litellm.ai/docs/providers).

    And about structured output in LiteLLM [here](https://docs.litellm.ai/docs/completion/json_mode)
