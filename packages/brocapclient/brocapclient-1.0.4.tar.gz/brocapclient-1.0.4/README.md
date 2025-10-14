## BroCapClient
Official python client library for [brocapgpt](https://docs.brocapgpt.com/) captcha recognition service

## Installation
```bash
python3 -m pip install brocapclient
```

## Usage

```python
import asyncio

from brocapclient.requests import HcaptchaRequest, FuncaptchaRequest, FoxcaptchaRequest
from brocapclient import BroCapGptClient, ClientOptions

client_options = ClientOptions(api_key=<YOUR_API_KEY>)
brocap_client = BroCapGptClient(options=client_options)

async def solve_captcha(request):
    return await brocap_client.solve_captcha(request)

# Hcaptcha request example
hcaptcha_request = HcaptchaRequest(
    websiteUrl="https://example.com/",
    websiteKey="d391ffb1-bc91-4ef8-a45a-2e2213af091b",
    userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
)

responses = asyncio.run(solve_captcha(hcaptcha_request))

# Funcaptcha request example
funcaptcha_request = FuncaptchaRequest(
    websiteUrl="http://mywebsite.com/",
    websiteKey="69A21A01-CC7B-B9C6-0F9A-E7FA06677FFC",
    userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
)

responses = asyncio.run(solve_captcha(funcaptcha_request))

# Foxcaptcha request example
foxcaptcha_request = FoxcaptchaRequest(
    websiteUrl="https://example.com/",
    websiteKey="sk_bo5o532TDv2Jey4fibTVChVS8z-cRdCE",
    userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
)

responses = asyncio.run(solve_captcha(foxcaptcha_request))
```

### Supported captcha recognition requests:
- [FunCaptcha](https://docs.brocapgpt.com/docs/captchas/funcaptcha-task/)
- [HCaptcha](https://docs.brocapgpt.com/docs/captchas/hcaptcha-task)
- [CaptchaFox](https://docs.brocapgpt.com/docs/captchas/captchafox-task)

