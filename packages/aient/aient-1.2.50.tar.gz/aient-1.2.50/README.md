# aient

[English](./README.md) | [Chinese](./README_CN.md)

aient is a powerful library designed to simplify and unify the use of different large language models, including gpt-4.1/5, o3, DALL-E 3, claude4, gemini-2.5-pro/flash, Vertex AI (Claude, Gemini), and Groq. The library supports GPT format function calls and has built-in Google search and URL summarization features, greatly enhancing the practicality and flexibility of the models.

## ✨ Features

- **Multi-model support**: Integrate various latest large language models.
- **Real-time Interaction**: Supports real-time query streams, real-time model response retrieval.
- **Function Expansion**: With built-in function calling support, the model's functions can be easily expanded, currently supporting plugins such as DuckDuckGo and Google search, content summarization, Dalle-3 drawing, arXiv paper summaries, current time, code interpreter, and more.
- **Simple Interface**: Provides a concise and unified API interface, making it easy to call and manage the model.

## Quick Start

The following is a guide on how to quickly integrate and use aient in your Python project.

### Install

First, you need to install aient. It can be installed directly via pip:

```bash
pip install aient
```

### Usage example

The following is a simple example demonstrating how to use aient to request the GPT-4 model and handle the returned streaming data:

```python
from aient import chatgpt

# Initialize the model, set the API key and the selected model
bot = chatgpt(api_key="{YOUR_API_KEY}", engine="gpt-4o")

# Get response
result = bot.ask("python list use")

# Send request and get streaming response in real-time
for text in bot.ask_stream("python list use"):
    print(text, end="")

# Disable all plugins
bot = chatgpt(api_key="{YOUR_API_KEY}", engine="gpt-4o", use_plugins=False)
```

## 🍃 Environment Variables

The following is a list of environment variables related to plugin settings:

| Variable Name | Description | Required? |
|---------------|-------------|-----------|
| get_search_results | Enable search plugin. Default value is `False`. | No |
| get_url_content | Enable URL summary plugin. The default value is `False`. | No |
| download_read_arxiv_pdf | Whether to enable the arXiv paper abstract plugin. The default value is `False`. | No |
| run_python_script | Whether to enable the code interpreter plugin. The default value is `False`. | No |
| generate_image | Whether to enable the image generation plugin. The default value is `False`. | No |
| get_time | Whether to enable the date plugin. The default value is `False`. | No |

## Supported models

- gpt-4.1/5
- o3
- DALL-E 3
- claude4
- gemini-2.5-pro/flash
- Vertex AI (Claude, Gemini)
- Groq

## 🧩 Plugin

This project supports multiple plugins, including: DuckDuckGo and Google search, URL summary, ArXiv paper summary, DALLE-3 drawing, and code interpreter, etc. You can enable or disable these plugins by setting environment variables.

- How to develop a plugin?

The plugin-related code is all in the aient git submodule of this repository. aient is an independent repository I developed for handling API requests, conversation history management, and other functionality. When you clone this repository with the `--recurse-submodules` parameter, aient will be automatically downloaded. All plugin code is located in the relative path `aient/src/aient/plugins` in this repository. You can add your own plugin code in this directory. The plugin development process is as follows:

1. Create a new Python file in the `aient/src/aient/plugins` directory, for example, `myplugin.py`. Register the plugin by adding the `@register_tool()` decorator above the function. Import `register_tool` with `from .registry import register_tool`.

After completing the above steps, your plugin is ready to use. 🎉

## License

This project is licensed under the MIT License.

## Contribution

Welcome to contribute improvements by submitting issues or pull requests through GitHub.

## Contact Information

If you have any questions or need assistance, please contact us at [yym68686@outlook.com](mailto:yym68686@outlook.com).