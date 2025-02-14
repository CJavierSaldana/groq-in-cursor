# OpenAI API Proxy with Request Tracking

## Overview

This project is a FastAPI-based proxy for the OpenAI API. It forwards requests to the OpenAI API and logs the interactions for tracking purposes. The proxy also supports a custom model (`qwen-2.5-coder-32b`) which routes requests to a different API endpoint.

## Features

- **Proxy Requests**: Forwards requests to the OpenAI API and logs the interactions.
- **Custom Model Support**: Supports a custom model (`qwen-2.5-coder-32b`) that routes requests to a different API endpoint.
- **Logging**: Logs all requests and responses to the `logs` directory.
- **CORS Support**: Configured to handle CORS requests from any origin.
- **HTTPS Requirement**: The endpoint should be publicly accessible via HTTPS.

## Requirements

- Python 3.8 or higher
- Environment variables for API keys (`OPENAI_API_KEY` and `GROQ_API_KEY`)

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/openai-api-proxy.git
   cd openai-api-proxy
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**

   Create a `.env` file in the root directory with the following content:

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

4. **Run the Application**

   ```bash
   uvicorn main:app --reload
   ```

   The application will be available at `http://127.0.0.1:8000`.

## Usage

### Endpoints

- **GET /models**: Fetches available models from the OpenAI API and includes a custom model (`qwen-2.5-coder-32b`).
- **POST /{path:path}**: Proxies requests to the OpenAI API. Supports streaming responses for the `/chat/completions` endpoint.

### HTTPS Requirement

For production use, ensure that the endpoint is publicly accessible via HTTPS. You can use a service like [Let's Encrypt](https://letsencrypt.org/) to obtain a free SSL certificate and configure your server to use HTTPS.

## Logging

All requests and responses are logged in the `logs` directory. Each log file is named with the endpoint and timestamp.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.