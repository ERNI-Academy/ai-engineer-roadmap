# ERNI AI Engineering Training

Small, shareable examples for calling the team's LiteLLM proxy.

## Setup

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

   ```bash
   # macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Clone this repository and install the pinned dependencies:

   ```bash
   uv sync
   ```

3. Create a local `.env` file (it is ignored by Git) with your LiteLLM virtual key and the proxy URL:

   ```dotenv
   LITELLM_BASE_URL=https://your-litellm-proxy.example.com
   LITELLM_API_KEY=your-virtual-key
   ```

   Ask the training administrators for a virtual key if you do not have one. Never commit or share this file.

## LiteLLM examples

Open [litellm_model_examples.ipynb](litellm_model_examples.ipynb) in VS Code and select the project's `.venv` Python kernel. Run the setup cell, then run any example you want:

- `gpt-5.6-luna` for text generation
- `text-embedding-3-small` for embeddings and cosine similarity
- `gpt-image-2` for image generation

Each call uses your LiteLLM virtual key and consumes its configured budget.
