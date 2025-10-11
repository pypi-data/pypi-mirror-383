"""HTTP example - demonstrates making HTTP POST requests."""

import asyncio
from openworkflows import Workflow


async def main():
    # Create workflow
    workflow = Workflow("HTTP Example")

    # Add HTTP POST node
    workflow.add_node(
        "post",
        "http_post",
        {
            "url_template": "https://jsonplaceholder.typicode.com/posts",
            "body_template": '{"title": "{title}", "userId": 1}',
            "headers": {"Content-Type": "application/json"},
        },
    )

    # Run workflow
    result = await workflow.run(inputs={"title": "My Post"})
    print(f"Status: {result['post']['status_code']}")
    print(f"Body: {result['post']['body']}")


if __name__ == "__main__":
    asyncio.run(main())
