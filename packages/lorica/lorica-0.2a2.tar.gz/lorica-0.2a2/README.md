# Lorica Package

## Introduction
This package provides functionality for interacting with Lorica Cybersecurity products. The following capabilities are currently offered:
- Attestation and OHTTP Public Key verification for Lorica AI deployment.
- OHTTP encapsulation for secure interaction with Lorica AI deployment.

## Lorica AI Interaction using Requests Session
To interact with a Lorica AI deployment through a `requests.Session`, simply replace the object construction with `lorica.Session`:
```python
import lorica
import json

# Create lorica.Session that inherits from requests.Session.
session = lorica.Session()

deployment_url = "DEPLOYMENT_URL"
lorica_api_key = "LORICA_API_KEY"

# Use session like a request.Session including response streaming support.
stream = True
resp = session.post(
    f"{deployment_url}/v1/chat/completions",
    headers={"Authorization": f"Bearer {lorica_api_key}"},
    json={
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "where does the sun rise from?"},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": stream,
    },
    stream=stream
)
resp.raise_for_status()
if stream:
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue

        data = line[len("data: "):].strip()
        if data == "[DONE]":
            break

        chunk = json.loads(data)
        print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
else:
    print(resp.json()["choices"][0]["message"]["content"])
```

## Lorica AI Interaction using HTTPX Transport
To interact with a Lorica AI deployment through a `httpx.Transport`, simply replace the object construction with `lorica.Transport`:
```python
import lorica
import httpx
import json

# Initialize httpx client with the lorica.Transport that inherits from httpx.Transport
httpx_client = httpx.Client(transport=lorica.Transport())

deployment_url = "DEPLOYMENT_URL"
lorica_api_key = "LORICA_API_KEY"

# Use client as normal including chunked-encoding response support.
method = "POST"
url = deployment_url + "/v1/chat/completions"
stream = True
data = {
    "model": "meta-llama/Llama-3.2-3B-Instruct",
    "messages": [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "where does the sun rise from?"},
    ],
    "temperature": 0.7,
    "max_tokens": 1024,
    "stream": stream,
}
headers = {"Authorization": f"Bearer {lorica_api_key}"}
if stream:
    with httpx_client.stream(method, url, json=data, headers=headers) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line or not line.startswith("data: "):
                continue

            data = line[len("data: "):].strip()
            if data == "[DONE]":
                break

            chunk = json.loads(data)
            print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
else:
    resp = httpx_client.post(url, json=data, headers=headers, timeout=30)
    resp.raise_for_status()
    print(resp.json()["choices"][0]["message"]["content"])
```

## Lorica AI Interaction using OpenAI Client
This is also applicable to clients that utilize `httpx` for their HTTP communication, for example `openai` client:
```python
import lorica
import httpx
import openai

# Initialize httpx client with lorica.Transport that inherits from httpx.Transport
httpx_client = httpx.Client(transport=lorica.Transport())
deployment_url = "DEPLOYMENT_URL"
lorica_api_key = "LORICA_API_KEY"

# Configure OpenAI client with httpx client
client = openai.OpenAI(
    api_key=lorica_api_key,
    http_client=httpx_client,
    base_url=deployment_url + "/v1")

# Use OpenAI SDK as normal for example llama chat (including stream capability)
stream = True
completion = client.chat.completions.create(
    model="meta-llama/Llama-3.2-3B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "where does the sun rise from?"},
    ],
    temperature=0.7,
    max_tokens=1024,
    stream=stream,
)
if stream:
    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
else:
    print(completion.choices[0].message.content)
```

## Optional Parameter Configurability
The `lorica.Transport` and `lorica.Session` class constructors take in optional parameters:
- **trustee_url**: In our attestation flow, a Trustee service acts as the Verifier according to the [RATS attestion procedure RFC9334](https://www.ietf.org/rfc/rfc9334.html). The classes default to use the Trustee deployed by Lorica but this parameter can be use to override the URL to point to any other Trustee instance.
- **attest**: This parameter can be used to disable the attestation flow in the absence of a Trustee service. We recommend keeping attestation ON unless the network route to the deployment is trusted.

## Fetching the Attested Deployment Report
The `lorica.Transport` and `lorica.Session` classes provide a `get_attested_deployment_report()` method that takes in a deployment's URL to output the deployment's attestation report which features attested measurements of the deployment's hardware and software. This method only outputs a report if the deployment passes all Trustee and client-side checks as part of the attestation flow. The full JSON Web Token (JWT) issued by Trustee can also be accessed via the `get_attestation_token()` method.

