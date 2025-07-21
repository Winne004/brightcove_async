# brightcove_async

`brightcove_async` is an asynchronous Python client library for interacting with the [Brightcove](https://www.brightcove.com/) video platform APIs. This library is designed to provide easy, non-blocking access to Brightcove's RESTful endpoints, making it ideal for use in modern async Python applications.

## Features

- Fully asynchronous API using `asyncio` 
- Simple authentication with OAuth2 client credentials
- Support for core Brightcove API endpoints (Videos, Analytics, etc.)
- Strong typing and data validation powered by Pydantic for reliable development and rich IDE autocompletion

## Installation

```bash
pip install brightcove_async
```

## Quick Start

```python
import asyncio

import brightcove_async
from brightcove_async.schemas.cms_model import (
    CreateVideoRequestBodyFields,
    State,
)

async def main() -> None:
    client = brightcove_async.initialise_brightcove_client()
    async with client as client_instance:
        result = await client_instance.cms.create_video(
            account_id="12345",
            video_data=CreateVideoRequestBodyFields(
                name="test",
                State=State.ACTIVE,
            ),
        )
        print(result.model_dump())


if __name__ == "__main__":
    asyncio.run(main())
```

## Usage

### Authentication

`brightcove_async` handles OAuth2 token management automatically. The easiest way to do this is to set the following environmental variables: 
```bash
export CLIENT_ID="your_client_id"
export CLIENT_SECRET="your_client_secret"
```

## API Coverage

- [x] Videos - In progress 
- [x] Analytics - In progress 
- [x] Syndication - In progress 

## Documentation

- [Brightcove API Documentation](https://apis.support.brightcove.com/)

## Requirements

- Python 3.13+

## Contributing

Pull requests are welcome! Please open an issue to discuss your feature or bugfix before submitting a PR.

## License

MIT License

## Disclaimer

This project is not affiliated with or endorsed by Brightcove Inc.