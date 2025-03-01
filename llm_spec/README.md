# LLM Specification Generator

Application that generates annotated ERC contract specifications using various Large Language Models (LLMs) and verification tools. The application allows users to select an ERC standard, an LLM model, and a verifier to produce annotated Solidity contracts compliant with the chosen standard.

## Table of Contents

- [LLM Specification Generator](#llm-specification-generator)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Directory Structure](#directory-structure)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Configuration](#configuration)
    - [Set Up Environment Variables](#set-up-environment-variables)
  - [Running the Application](#running-the-application)
  - [API Endpoints](#api-endpoints)
    - [Generate Specification](#generate-specification)
    - [Request Parameters](#request-parameters)

## Features

- Supports multiple ERC standards: ERC20, ERC721, ERC1155.
- Utilizes various LLM models: OpenAI's GPT, LLaMA, Claude.
- Integrates with different verifiers: `solc-verify`, `smtchecker`.
- Modular design using the Abstract Factory pattern.
- Extensible architecture for adding new LLMs, verifiers, and ERC standards.
- Provides a RESTful API for integration with other services.

## Directory Structure

```plaintext
llm_spec/
├── README.md
├── app
│   ├── api
│   │   ├── generate_specification.py
│   │   └── status.py
│   ├── main.py
│   ├── models
│   │   └── models.py
│   ├── services
│   │   ├── claude_service.py
│   │   ├── llama_service.py
│   │   ├── llm_factory.py
│   │   ├── llm_service_interface.py
│   │   ├── openai_service.py
│   │   ├── refinement_loop.py
│   │   ├── smtchecker_service.py
│   │   ├── solc_verify_service.py
│   │   ├── verifier_factory.py
│   │   └── verifier_service_interface.py
│   ├── templates
│   │   ├── contracts
│   │   │   ├── ERC1155_contract_template.sol
│   │   │   ├── ERC20_contract_template.sol
│   │   │   └── ERC721_contract_template.sol
│   │   ├── eips
│   │   │   ├── ERC1155_eip.md
│   │   │   ├── ERC20_eip.md
│   │   │   ├── ERC3156_eip.md
│   │   │   └── ERC721_eip.md
│   │   ├── examples
│   │   │   ├── ERC1155_example.sol
│   │   │   ├── ERC20_example.sol
│   │   │   └── ERC721_example.sol
│   │   └── instructions
│   │       ├── smtchecker_instructions.txt
│   │       └── solc_verify_instructions.txt
│   └── utils
│       ├── logger.py
│       └── utils.py
├── requirements.txt
├── results
└── temp
```

## Installation

### Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8 or higher**: Check your Python version using `python --version` or `python3 --version`.
- **pip**: Python package manager should be installed. Verify using `pip --version` or `pip3 --version`.
- **virtualenv** (optional but recommended): Allows you to create isolated Python environments.
- **Solidity Compiler (`solc`)**: Install the Solidity compiler for compiling smart contracts.
- **solc-verify**: Tool for formal verification of Solidity smart contracts.
- **OpenAI API Key**: Required if you're using OpenAI models. Sign up at [OpenAI](https://openai.com/) to obtain an API key.

### Steps

Follow these steps to set up the project on your local machine:

1. **Create a Virtual Environment**
    It’s recommended to use a virtual environment to manage project dependencies:
    ```bash
    # Create a virtual environment named 'venv'
    python3 -m venv venv

    # Activate the virtual environment
    source venv/bin/activate
    ```
2. **Install Python Dependencies**
    Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### Set Up Environment Variables
Create a .env file in the root directory and add your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key
```

This is how to load a new model into ollama

```
ollama create <your-model-name-here> -f Modelfile
```

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be accessible at http://localhost:8000.

## API Endpoints

### Generate Specification

- Endpoint: /api/v1/generate_specification
- Method: POST
- Description: Initiates the process of generating an annotated ERC contract specification.

### Request Parameters

- Content-Type: application/json
- Body Parameters:

  - **llm_model** (string): The LLM model to use ("openai", "llama", "claude").
  - **verifier** (string): The verifier to use ("solc_verify", "smtchecker").
  - **erc_standard** (string): The ERC standard ("erc20", "erc721", "erc1155").
