"""
Example 2: Async/Await Tracing

This example demonstrates how Breadcrumb traces async functions, maintains
context across await points, and handles concurrent execution.
"""

import sys
sys.path.insert(0, '../../src')

import asyncio
import random
import breadcrumb

# Initialize Breadcrumb tracing
breadcrumb.init()


async def fetch_user(user_id: int) -> dict:
    """Simulate fetching a user from a database."""
    print(f"  Fetching user {user_id}...")
    await asyncio.sleep(random.uniform(0.1, 0.3))  # Simulate I/O delay
    return {
        "id": user_id,
        "name": f"User_{user_id}",
        "email": f"user{user_id}@example.com"
    }


async def fetch_posts(user_id: int) -> list:
    """Simulate fetching posts for a user."""
    print(f"  Fetching posts for user {user_id}...")
    await asyncio.sleep(random.uniform(0.1, 0.4))  # Simulate I/O delay
    return [
        {"id": i, "user_id": user_id, "title": f"Post {i} by user {user_id}"}
        for i in range(random.randint(1, 3))
    ]


async def fetch_comments(post_id: int) -> list:
    """Simulate fetching comments for a post."""
    print(f"    Fetching comments for post {post_id}...")
    await asyncio.sleep(random.uniform(0.05, 0.15))  # Simulate I/O delay
    return [
        {"id": i, "post_id": post_id, "text": f"Comment {i} on post {post_id}"}
        for i in range(random.randint(0, 2))
    ]


async def get_user_profile(user_id: int) -> dict:
    """
    Fetch complete user profile with posts and comments.
    Demonstrates sequential async operations.
    """
    # Sequential async calls
    user = await fetch_user(user_id)
    posts = await fetch_posts(user_id)

    # Fetch comments for all posts concurrently
    comment_tasks = [fetch_comments(post["id"]) for post in posts]
    all_comments = await asyncio.gather(*comment_tasks)

    # Combine results
    for post, comments in zip(posts, all_comments):
        post["comments"] = comments

    user["posts"] = posts
    return user


async def parallel_example():
    """Demonstrate parallel async execution."""
    print("\n1. Parallel User Fetching:")
    print("-" * 60)

    # Fetch multiple users concurrently
    user_ids = [1, 2, 3]
    tasks = [fetch_user(user_id) for user_id in user_ids]
    users = await asyncio.gather(*tasks)

    print(f"  Fetched {len(users)} users in parallel")
    for user in users:
        print(f"    - {user['name']}: {user['email']}")


async def sequential_example():
    """Demonstrate sequential async execution."""
    print("\n2. Sequential Profile Building:")
    print("-" * 60)

    profile = await get_user_profile(user_id=10)

    print(f"  Profile for {profile['name']}:")
    print(f"    Email: {profile['email']}")
    print(f"    Posts: {len(profile['posts'])}")
    for post in profile['posts']:
        print(f"      - {post['title']} ({len(post['comments'])} comments)")


async def error_handling_example():
    """Demonstrate async exception tracing."""
    print("\n3. Async Error Handling:")
    print("-" * 60)

    async def failing_task():
        """A task that will fail."""
        await asyncio.sleep(0.1)
        raise ValueError("Simulated async error!")

    async def successful_task(n):
        """A task that succeeds."""
        await asyncio.sleep(0.05)
        return n * 2

    # Run multiple tasks, one will fail
    try:
        results = await asyncio.gather(
            successful_task(5),
            failing_task(),
            successful_task(10),
            return_exceptions=True  # Capture exceptions as results
        )

        print("  Task results:")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"    Task {i}: ERROR - {result}")
            else:
                print(f"    Task {i}: SUCCESS - {result}")
    except Exception as e:
        print(f"  Caught exception: {e}")


async def main():
    """Run all async examples."""
    print("=" * 60)
    print("Breadcrumb Example 2: Async/Await Tracing")
    print("=" * 60)

    # Run examples
    await parallel_example()
    await sequential_example()
    await error_handling_example()

    print("\n" + "=" * 60)
    print("Async execution complete! Traces captured.")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("  1. Run: breadcrumb list")
    print("  2. Run: breadcrumb query \"SELECT * FROM events WHERE function_name LIKE '%fetch%'\"")
    print("  3. Analyze async timing with performance tools")
    print("  4. See README.md for async-specific queries")
    print()


if __name__ == "__main__":
    asyncio.run(main())
