from notifier import Notifier

if __name__ == "__main__":
    n = Notifier(
        title="🧑‍🍳 Test Notification",
        message="This is a test",
        button="⚡ Click me!",
        beep=True
    )
    n.show()
