def sign(x: int) -> int:
    sign_: int = int(x > 0) - int(x < 0)
    return sign_


def factorize(number: int) -> list[int]:
    factors: list[int] = [divisor
                          for divisor in range(1, number + 1)
                          if number % divisor == 0]
    return factors
