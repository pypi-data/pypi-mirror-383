# Example.com Python SDK

## Overview

This is an **example** API to demonstrate features of the OpenAPI specification. # Introduction This API definition is intended to to be a good starting point for describing your API in [OpenAPI/Swagger format](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md). It also demonstrates features of the [create-openapi-repo](https://github.com/Redocly/create-openapi-repo) tool and the [Redoc](https://github.com/Redocly/Redoc) documentation engine. Beyond the standard OpenAPI syntax, we use a few  [vendor extensions](https://github.com/Redocly/Redoc/blob/master/docs/redoc-vendor-extensions.md). # OpenAPI Specification The goal of The OpenAPI Specification is to define a standard, language-agnostic interface to REST APIs which allows both humans and computers to discover and understand the capabilities of the service without access to source code, documentation, or through network traffic inspection. When properly defined via OpenAPI, a consumer can  understand and interact with the remote service with a minimal amount of implementation logic. Similar to what interfaces have done for lower-level programming, OpenAPI removes the guesswork in calling the service. 

## Installation

```bash
pip install test123test234
```

## Configuration

```python
import test123test234
from test123test234.rest import ApiException

# Create configuration with API key
configuration = test123test234.Configuration()
configuration.api_key['api-key'] = 'your_api_key_here'

# Create API client
api_client = test123test234.ApiClient(configuration)
api_instance = test123test234.BrandsApi(api_client)
```

## Example Request

```python
# Get brand data by domain
try:
    domain_request = test123test234.DomainRequest(domain="example.com")
    response = api_instance.by_domain(domain_request)
    
    # Access brand data
    print(f"Brand: {response.brand.name}")
    print(f"Logo: {response.images.logos[0].url}")
    print(f"Primary Color: {response.colors.primary[0].hex}")
except ApiException as e:
    print(f"Exception: {e}")
```

## API Endpoints

Class | Method | Description
------------ | ------------- | -------------
*EchoApi* | **echo** | Echo test


## Models

List of available API Models

[Example.com Models](http://localhost:4321/docs/api-docs/models)

## Authentication

Authentication schemes defined for the API:

[Example.com Authentication Documentation](http://localhost:4321/docs/authentication)


### api_key

- **Type**: API key
- **API key parameter name**: api_key
- **Location**: HTTP header

