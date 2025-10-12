# payman-zarinpal

**payman-zarinpal** is a plugin for **[Payman](https://pypi.org/project/payman/)** that enables integration with the **ZarinPal payment gateway**. This package requires Payman >= 3.0.0.

## Installation

```bash
pip install payman[zarinpal]
```

## Quick Example

```python
import asyncio

from payman import Payman
from zarinpal.models import PaymentRequest

pay = Payman("zarinpal", merchant_id="your-merchant-id")

async def main():
    req_params = PaymentRequest(
        amount=100_000,
        callback_url="https://example.com/callback",
        description="Test Payment",
        metadata={"email": "user@example.com", "mobile": "09123456789"},
    )

    response = await pay.initiate_payment(req_params)
    print(response.success, response.authority)

asyncio.run(main())
```

## Links

* [Payman GitHub Repository](https://github.com/irvaniamirali/payman)
* [Payman Documentation](https://irvaniamirali.github.io/payman)
* [Zarinpal API Reference](https://docs.zarinpal.com/paymentGateway/)
