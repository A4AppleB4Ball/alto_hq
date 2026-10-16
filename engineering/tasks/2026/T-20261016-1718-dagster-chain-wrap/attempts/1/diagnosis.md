# Attempt 1 diagnosis (check 3, 20MICRONS side)

Tried: stance stage on 20MICRONS in a sandbox root with rewound links (rewind to 10-05, 08-07, 08-06) and the deepseek config. Failure: `DHAN_CLIENT_ID or DHAN_CLIENT_KEY not set for user 'scienceamit1'` at `price_feed/dhan_price_store.py:_build_client` via `lib/asof.py:daily_price_series`; default model fails with Bedrock `ExpiredTokenException` (502). Cause: the sandbox workspace holds no Dhan secrets and none were copied (credentials are the owner's call). Not a code defect; no third attempt started.
