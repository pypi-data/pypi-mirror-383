from TwoCaptcha import AsyncTwoCaptcha, TwoCaptchaError
import asyncio


async def auto_solve_captcha():
    """
    Auto solve captcha using 2captcha api.
    """
    client = AsyncTwoCaptcha(api_key="c6f1762af830ed150e6dce59d3a7814c")
    try:
        task = {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
            "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        }
        balance = await client.balance()
        print(f"Balance: {balance}")
        result = await client.solve_captcha(task)
        print(f"Result: {result}")

    except TwoCaptchaError as e:
        print(f"TwoCaptcha Error: {e}")

    finally:
        await client.close()


async def manual_solve_captcha():
    """
    Manual solve captcha using 2captcha api.
    """
    client = AsyncTwoCaptcha(api_key="c6f1762af830ed150e6dce59d3a7814c")
    try:
        task = {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
            "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        }

        create_result = await client.create_task(task)
        task_id = create_result["taskId"]
        print(f"Created task with ID: {task_id}")

        task_result = await client.get_task_result(task_id)
        print(f"Task result: {task_result}")

    except TwoCaptchaError as e:
        print(f"TwoCaptcha Error: {e}")
    finally:
        await client.close()


async def context_manager_example():
    """
    Context manager example.
    """
    async with AsyncTwoCaptcha(api_key="c6f1762af830ed150e6dce59d3a7814c") as client:
        balance = await client.balance()
        print(f"Context manager balance: {balance}")


async def multiple_tasks_example():
    """
    Multiple tasks example.
    """
    client = AsyncTwoCaptcha(api_key="c6f1762af830ed150e6dce59d3a7814c")
    try:
        tasks = [
            {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
                "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
            },
            {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
                "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
            },
        ]

        print("Solving multiple captchas concurrently...")
        results = await asyncio.gather(
            *[client.solve_captcha(task) for task in tasks], return_exceptions=True
        )

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Task {i+1} failed: {result}")
            else:
                print(
                    f"Task {i+1} solved: {result['solution']['gRecaptchaResponse'][:30]}..."
                )

    except Exception as e:
        print(f"Error in multiple tasks: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    # auto_solve_captcha()
    # print("--------------------------------")
    # asyncio.run(manual_solve_captcha())
    # print("--------------------------------")
    # asyncio.run(context_manager_example())
    print("--------------------------------")
    asyncio.run(multiple_tasks_example())
