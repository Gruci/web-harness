"""픽스처: 중첩 def — 맨몸 하나와 탈출 주석 하나."""


def outer():
    def inner():
        return 1
    return inner()


def wrapped():
    def keeper():  # closure-ok: 픽스처 — 탈출 주석이 실제로 면제되는지 증명한다
        return 2
    return keeper()
