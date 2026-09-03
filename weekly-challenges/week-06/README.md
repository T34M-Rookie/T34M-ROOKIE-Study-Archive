# T34M ROOKIE — Week 6

| Challenge | Original | Type | Local URL |
| --- | --- | --- | --- |
| SSRF101 | WolvCTF 2022 | SSRF | http://localhost:1360 |
| difference-check | idekCTF 2021 | SSRF Filter Bypass | http://localhost:1361 |
| graphql-101 | LINE CTF 2024 | GraphQL / Rate Limit | http://localhost:1362 |

Each directory preserves the original challenge source and adds a separate T34M local deployment wrapper.

Run a challenge from its directory with:

```bash
docker compose up --build
```

Stop it with:

```bash
docker compose down
```

All published ports are bound to `127.0.0.1`.
