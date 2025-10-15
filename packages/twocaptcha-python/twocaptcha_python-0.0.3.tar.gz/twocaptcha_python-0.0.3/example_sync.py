from TwoCaptcha import SyncTwoCaptcha, TwoCaptchaError
from rich import print

client = SyncTwoCaptcha(api_key="c6f1762af830ed150e6dce59d3a7814c")


def auto_solve_captcha():
    """
    Auto solve captcha using 2captcha api.
    """
    try:
        task = {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
            "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        }
        balance = client.balance()
        print(f"Balance: {balance}")
        result = client.solve_captcha(task)
        print(f"Result: {result}")

    except TwoCaptchaError as e:
        print(f"TwoCaptcha Error: {e}")


def manual_solve_captcha(task_id=None):
    """
    Manual solve captcha using 2captcha api.
    """
    try:
        task = {
            "type": "RecaptchaV2TaskProxyless",
            "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
            "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        }

        create_result = client.create_task(task)
        task_id = create_result["taskId"]
        print(f"Created task with ID: {task_id}")

        task_result = client.get_task_result(task_id)
        print(f"Task result: {task_result}")

    except TwoCaptchaError as e:
        print(f"TwoCaptcha Error: {e}")


def context_manager_example():
    """
    Context manager example - shows when explicit cleanup is useful.
    """
    with SyncTwoCaptcha(api_key="c6f1762af830ed150e6dce59d3a7814c") as client:
        balance = client.balance()
        print(f"Context manager balance: {balance}")


def multiple_operations_example():
    """
    Multiple operations example - shows when close() is useful.
    """
    client = SyncTwoCaptcha(api_key="c6f1762af830ed150e6dce59d3a7814c")
    try:
        # Multiple operations
        balance = client.balance()
        print(f"Balance: {balance}")

        # Solve multiple captchas
        for i in range(2):
            task = {
                "type": "RecaptchaV2TaskProxyless",
                "websiteURL": f"https://2captcha.com/demo/recaptcha-v2",
                "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
            }
            result = client.solve_captcha(task)
            print(
                f"Captcha {i+1} solved: {result['solution']['gRecaptchaResponse'][:30]}..."
            )

    except TwoCaptchaError as e:
        print(f"TwoCaptcha Error: {e}")


if __name__ == "__main__":
    # auto_solve_captcha()
    print("--------------------------------")
    manual_solve_captcha()
    print("--------------------------------")
    context_manager_example()
    print("--------------------------------")
    multiple_operations_example()
