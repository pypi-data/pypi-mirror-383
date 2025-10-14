from kubemind_common.http.client import create_http_client, http_request
import asyncio


async def main():
    async with create_http_client() as client:
        resp = await http_request(client, "GET", "https://httpbin.org/get")
        print(resp.status_code)


if __name__ == "__main__":
    asyncio.run(main())
