"""
core.py — Учебная библиотека алгоритмов (теория чисел + поиски)

Содержимое (максимально учебное, с docstring'ами, комментариями и типизацией):

1) Теория чисел
   - Проверка на простоту: is_prime_linear, is_prime_linear_optimized, is_prime_sqrt_optimized, miller_rabin
   - Решето Эратосфена: sieve_eratosthenes
   - Факторизация: factorize, factorize_optimized, factorize_with_primes
   - НОД/НОК: gcd_euclid, gcd_binary, lcm
   - Алгоритм Евклида (расширенный): extended_gcd

2) Поисковые алгоритмы
   - Бинарный поиск: binary_search (итеративный), recursive_binary_search (рекурсивный)
   - lower_bound, upper_bound
   - Вещественный бинарный поиск: binary_search_real
   - Тернарный поиск экстремума: ternary_search
   - Интерполяционный поиск: interpolation_search

В конце файла — учебные демонстрации в блоке if __name__ == "__main__":

Примечание:
Код ориентирован на понятность и учебные комментарии, а не на абсолютную оптимальность.
"""

from __future__ import annotations
from typing import Callable, List, Optional, Sequence, Tuple


# ===============================================================
#                       ТЕОРИЯ ЧИСЕЛ
# ===============================================================

def is_prime_linear(n: int) -> bool:
    """
    Самая простая линейная проверка на простоту: перебираем делители от 2 до n-1.

    ВРЕМЕННАЯ СЛОЖНОСТЬ: O(n)
    ПРИМЕЧАНИЕ: Очень неэффективно для больших n, но максимально наглядно.

    :param n: проверяемое число
    :return: True, если n простое; иначе False
    """
    if n <= 1:
        return False  # 1 и все числа <= 1 не являются простыми
    if n == 2:
        return True   # 2 — простое
    if n % 2 == 0:
        return False  # чётные > 2 — составные

    # Перебираем все нечётные делители от 3 до n-1
    for i in range(3, n, 2):
        if n % i == 0:
            return False
    return True


def is_prime_linear_optimized(n: int) -> bool:
    """
    Линейная проверка, но с пропуском чисел, кратных 2 и 3.
    Используем наблюдение: кандидаты на простоту > 3 имеют вид 6k ± 1.

    ВРЕМЕННАЯ СЛОЖНОСТЬ: O(n), но константа заметно меньше, чем у is_prime_linear.

    :param n: проверяемое число
    :return: True, если n простое; иначе False
    """
    if n <= 1:
        return False
    if n <= 3:
        return True  # 2 и 3 простые
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Проверяем только числа вида 6k±1: 5, 7, 11, 13, 17, 19, ...
    i = 5
    while i < n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def is_prime_sqrt_optimized(n: int) -> bool:
    """
    Проверка на простоту с ограничением делителей корнем из n и пропуском кратных 2 и 3.

    ИДЕЯ: если n = a*b, то как минимум один из множителей <= sqrt(n).
    Достаточно проверять делители до sqrt(n).

    ВРЕМЕННАЯ СЛОЖНОСТЬ: O(sqrt(n))

    :param n: проверяемое число
    :return: True, если n простое; иначе False
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def miller_rabin(n: int, k: int = 40) -> bool:
    """
    Вероятностный тест Миллера—Рабина.
    Для не очень больших n можно подобрать фиксированный набор оснований, чтобы сделать тест
    детерминированным. Здесь используем случайные основания через встроенный pow().

    ВРЕМЕННАЯ СЛОЖНОСТЬ: O(k * log^3 n) (грубая оценка)

    :param n: проверяемое число
    :param k: число раундов (чем больше, тем меньше вероятность ошибки)
    :return: True, если n вероятно простое; False, если точно составное
    """
    import random

    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Представляем n-1 как d * 2^s, где d — нечётно
    s, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        s += 1

    # Один раунд проверки для случайного основания a
    def check(a: int) -> bool:
        # x = a^d mod n
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        # Возводим в квадрат s-1 раз: ищем появление n-1
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True
            if x == 1:
                return False
        return False

    # Повторяем k раундов
    for _ in range(k):
        a = random.randrange(2, n - 1)
        if not check(a):
            return False  # точно составное
    return True  # вероятно простое


def sieve_eratosthenes(n: int) -> List[int]:
    """
    Классическое решето Эратосфена: возвращает список всех простых чисел <= n.

    ИДЕЯ: последовательно вычеркиваем кратные найденных простых.
    ВРЕМЕННАЯ СЛОЖНОСТЬ (практически): ~ O(n log log n)

    :param n: верхняя граница (включительно)
    :return: список простых чисел до n
    """
    if n < 2:
        return []

    # Изначально считаем все числа >=2 потенциально простыми
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False

    p = 2
    while p * p <= n:
        if is_prime[p]:
            # Начинаем вычёркивать с p*p (все меньшие кратные уже обработаны)
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
        p += 1

    return [i for i, ok in enumerate(is_prime) if ok]


def factorize(n: int) -> List[int]:
    """
    Базовая факторизация (пробное деление): ищем делители от 2 до sqrt(n),
    делим n на найденный делитель, пока делится.

    ВРЕМЕННАЯ СЛОЖНОСТЬ: O(sqrt(n))

    :param n: число для факторизации (n >= 2)
    :return: список простых множителей в неубывающем порядке
    """
    factors: List[int] = []
    i = 2
    while i * i <= n:
        while n % i == 0:
            n //= i
            factors.append(i)
        i += 1
    if n > 1:
        factors.append(n)
    return factors


def factorize_optimized(n: int) -> List[int]:
    """
    Оптимизированная факторизация:
    - отдельно делим на 2;
    - затем перебираем только нечётные делители.

    ВРЕМЕННАЯ СЛОЖНОСТЬ: O(sqrt(n)), но быстрее на практике.

    :param n: число для факторизации
    :return: список простых множителей
    """
    factors: List[int] = []

    # Выделяем все двойки
    while n % 2 == 0:
        factors.append(2)
        n //= 2

    # Проверяем только нечётные i
    i = 3
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 2

    if n > 1:
        factors.append(n)
    return factors


def factorize_with_primes(n: int, primes: Optional[Sequence[int]] = None) -> List[int]:
    """
    Факторизация с готовым списком простых чисел. Полезно, когда надо
    много раз факторизовать разные n: один раз строим решето, затем используем.

    :param n: число для факторизации
    :param primes: список простых (например, sieve_eratosthenes(limit))
    :return: список простых множителей
    """
    if primes is None:
        return factorize_optimized(n)

    factors: List[int] = []
    for p in primes:
        if p * p > n:
            break
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.append(n)
    return factors


def gcd_euclid(a: int, b: int) -> int:
    """
    Классический алгоритм Евклида по остаткам.
    Возвращает НОД(a, b).

    :param a: целое
    :param b: целое
    :return: наибольший общий делитель
    """
    while b != 0:
        a, b = b, a % b
    return abs(a)


def gcd_binary(a: int, b: int) -> int:
    """
    Двоичный алгоритм Евклида (алгоритм Штейна).
    Использует сдвиги и разности вместо деления.

    :param a: целое
    :param b: целое
    :return: НОД(a, b)
    """
    a, b = abs(a), abs(b)
    if a == 0:
        return b
    if b == 0:
        return a

    # k — общая степень двойки у (a, b)
    shift = 0
    while ((a | b) & 1) == 0:
        a >>= 1
        b >>= 1
        shift += 1

    # делаем a нечётным
    while (a & 1) == 0:
        a >>= 1

    while b != 0:
        # делаем b нечётным
        while (b & 1) == 0:
            b >>= 1
        # теперь оба нечётные — вычитаем меньшее из большего
        if a > b:
            a, b = b, a
        b -= a
    # возвращаем общую степень двойки
    return a << shift


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Расширенный алгоритм Евклида.
    Возвращает кортеж (g, x, y), такой что g = gcd(a, b) и a*x + b*y = g.

    Полезно для вычисления обратных по модулю, решения диофантовых уравнений.

    :param a: целое
    :param b: целое
    :return: (g, x, y)
    """
    if b == 0:
        # gcd(a, 0) = |a|; представим |a| = a*sign(a) + 0*0
        return (abs(a), 1 if a >= 0 else -1, 0)
    g, x1, y1 = extended_gcd(b, a % b)
    # Возвращаем x, y для исходных a, b
    x = y1
    y = x1 - (a // b) * y1
    return (g, x, y)


def lcm(a: int, b: int) -> int:
    """
    НОК(a, b) через НОД: lcm(a,b) = |a*b| / gcd(a,b).

    :param a: целое
    :param b: целое
    :return: наименьшее общее кратное
    """
    if a == 0 or b == 0:
        return 0
    return abs(a // gcd_euclid(a, b) * b)


# ===============================================================
#                    ПОИСКОВЫЕ АЛГОРИТМЫ
# ===============================================================

def binary_search(arr: Sequence[int], x: int) -> int:
    """
    Итеративный бинарный поиск в отсортированном массиве arr.
    Возвращает индекс x или -1, если элемент не найден.

    ВРЕМЕННАЯ СЛОЖНОСТЬ: O(log n)

    :param arr: отсортированная последовательность
    :param x: искомое значение
    :return: индекс найденного элемента или -1
    """
    left, right = 0, len(arr) - 1
    while left <= right:
        # безопасный способ вычисления середины без переполнения
        mid = left + (right - left) // 2
        if arr[mid] < x:
            left = mid + 1
        elif arr[mid] > x:
            right = mid - 1
        else:
            return mid
    return -1


def recursive_binary_search(arr: Sequence[int], left: int, right: int, x: int) -> int:
    """
    Рекурсивный бинарный поиск.
    Для удобства можно вызывать как recursive_binary_search(arr, 0, len(arr)-1, x).

    :return: индекс x или -1
    """
    if left > right:
        return -1
    mid = left + (right - left) // 2
    if arr[mid] < x:
        return recursive_binary_search(arr, mid + 1, right, x)
    elif arr[mid] > x:
        return recursive_binary_search(arr, left, mid - 1, x)
    else:
        return mid


def lower_bound(arr: Sequence[int], x: int) -> int:
    """
    Возвращает позицию первого элемента, который НЕ МЕНЬШЕ x (>= x).
    Если все элементы < x, возвращает len(arr).

    Это "левая граница" диапазона значений == x.

    :param arr: отсортированная последовательность
    :param x: значение
    :return: индекс
    """
    left, right = 0, len(arr)
    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] < x:
            left = mid + 1
        else:
            right = mid
    return left


def upper_bound(arr: Sequence[int], x: int) -> int:
    """
    Возвращает позицию первого элемента, который СТРОГО БОЛЬШЕ x (> x).
    Если все элементы <= x, возвращает len(arr).

    Это "правая граница" диапазона значений == x.

    :param arr: отсортированная последовательность
    :param x: значение
    :return: индекс
    """
    left, right = 0, len(arr)
    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] <= x:
            left = mid + 1
        else:
            right = mid
    return left


def binary_search_real(
    f: Callable[[float], float],
    a: float,
    b: float,
    epsilon: float = 1e-4,
    max_iterations: int = 100
) -> Optional[float]:
    """
    Вещественный бинарный поиск (бисекция) для нахождения корня f(x)=0 на [a,b].
    Требуется, чтобы f(a) и f(b) имели разные знаки.

    КРИТЕРИЙ ОСТАНОВА: либо интервал стал уже epsilon, либо достигнут max_iterations.

    :param f: функция одной переменной
    :param a: левая граница интервала
    :param b: правая граница интервала
    :param epsilon: точность
    :param max_iterations: ограничение итераций (на случай неподходящих входных данных)
    :return: приближение корня или None, если на [a,b] нет смены знака
    """
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        # Функция не меняет знак — метод неприменим
        return None

    left, right = a, b
    it = 0
    while (right - left) > epsilon and it < max_iterations:
        mid = (left + right) / 2.0
        fm = f(mid)

        # Если значение близко к нулю — можно остановиться раньше
        if abs(fm) < epsilon:
            return mid

        # Определяем, в какой половине есть корень (меняется знак)
        if fa * fm > 0:
            left = mid
            fa = fm
        else:
            right = mid
            fb = fm

        it += 1

    return (left + right) / 2.0


def ternary_search(
    f: Callable[[float], float],
    left: float,
    right: float,
    epsilon: float = 1e-4,
    find_max: bool = True,
    max_iterations: int = 200
) -> float:
    """
    Тернарный (троичный) поиск экстремума унимодальной функции на отрезке [left, right].
    Если find_max=True — ищем максимум, иначе — минимум.

    На каждой итерации берём две точки: m1 и m2, делящие отрезок на три части.
    Сравниваем f(m1) и f(m2) и сокращаем интервал поиска.

    :param f: функция одной переменной (предполагается унимодальность на [left, right])
    :param left: левая граница
    :param right: правая граница
    :param epsilon: точность по аргументу
    :param find_max: True — максимум; False — минимум
    :param max_iterations: защитное ограничение числа итераций
    :return: приближённая точка экстремума
    """
    it = 0
    while (right - left) > epsilon and it < max_iterations:
        m1 = left + (right - left) / 3.0
        m2 = right - (right - left) / 3.0
        f1, f2 = f(m1), f(m2)

        if find_max:
            # Максимум "сдвигается" в сторону большей функции
            if f1 < f2:
                left = m1
            else:
                right = m2
        else:
            # Минимум "сдвигается" в сторону меньшей функции
            if f1 > f2:
                left = m1
            else:
                right = m2
        it += 1

    return (left + right) / 2.0


def interpolation_search(arr: Sequence[int], x: int) -> int:
    """
    Интерполяционный поиск. Предполагает, что значения в массиве распределены "более-менее равномерно".
    Использует линейную интерполяцию для оценки позиции искомого значения.

    ХУДШИЙ СЛУЧАЙ: O(n) (если распределение плохое).
    СРЕДНИЙ СЛУЧАЙ (для "хороших" распределений): около O(log log n).

    :param arr: отсортированный массив (по возрастанию)
    :param x: искомое значение
    :return: индекс x или -1, если нет
    """
    if not arr:
        return -1

    left, right = 0, len(arr) - 1

    while left <= right and arr[left] <= x <= arr[right]:
        # Защита от деления на ноль при arr[left] == arr[right]
        if arr[left] == arr[right]:
            return left if arr[left] == x else -1

        # Оценка позиции по формуле интерполяции:
        # mid = left + (x - arr[left]) * (right - left) / (arr[right] - arr[left])
        mid = left + int((x - arr[left]) * (right - left) / (arr[right] - arr[left]))

        if arr[mid] == x:
            return mid
        elif arr[mid] < x:
            left = mid + 1
        else:
            right = mid - 1

    return -1

def binary_search_answer(
    check: Callable[[int], bool],
    left: int,
    right: int
) -> int:
    """
    Универсальный бинарный поиск по ответу (на целых числах).

    Идея:
        Ищем минимальное значение x в диапазоне [left, right],
        для которого check(x) == True.

    Требования:
        check(x) должно быть монотонным:
            если check(x) == True, то check(y) == True для всех y > x.

    :param check: функция-предикат, возвращающая True/False
    :param left: нижняя граница диапазона
    :param right: верхняя граница диапазона
    :return: минимальное x, удовлетворяющее check(x)
    """
    while left < right:
        mid = (left + right) // 2
        if check(mid):
            right = mid  # возможно, ответ — mid или левее
        else:
            left = mid + 1  # ответ правее
    return left


# ===============================================================
#                         ДЕМО-РАЗДЕЛ
# ===============================================================

def _demo_number_theory() -> None:
    print("=== Теория чисел ===")
    nums = [1, 2, 3, 4, 5, 17, 18, 97, 221]
    print("Проверка на простоту (sqrt-оптимизация):")
    for n in nums:
        print(f"  {n:>3} -> {is_prime_sqrt_optimized(n)}")

    print("\nMiller-Rabin (вероятностно):")
    for n in nums:
        print(f"  {n:>3} -> {miller_rabin(n)}")

    print("\nРешето Эратосфена до 50:")
    print(sieve_eratosthenes(50))

    print("\nФакторизация (оптимизированная):")
    to_factor = [30, 97, 143, 360, 1001]
    for n in to_factor:
        print(f"  {n:>4} -> {factorize_optimized(n)}")

    print("\nНОД/НОК:")
    pairs = [(18, 24), (101, 103), (360, 840)]
    for a, b in pairs:
        g = gcd_euclid(a, b)
        print(f"  gcd_euclid({a}, {b}) = {g}, lcm = {lcm(a, b)}")

    print("\nРасширенный Евклид:")
    a, b = 99, 78
    g, x, y = extended_gcd(a, b)
    print(f"  extended_gcd({a}, {b}) -> g={g}, x={x}, y={y} (проверка: {a}*{x} + {b}*{y} = {a*x + b*y})")


def _demo_search() -> None:
    print("\n=== Поисковые алгоритмы ===")
    arr = [1, 3, 5, 5, 5, 7, 9, 11]
    print("Массив:", arr)

    print("\nБинарный поиск (итеративный): ищем 7")
    idx = binary_search(arr, 7)
    print("  index =", idx)

    print("\nБинарный поиск (рекурсивный): ищем 9")
    idx = recursive_binary_search(arr, 0, len(arr) - 1, 9)
    print("  index =", idx)

    print("\nlower_bound / upper_bound для x=5")
    lb = lower_bound(arr, 5)
    ub = upper_bound(arr, 5)
    print(f"  lower_bound(5) = {lb}, upper_bound(5) = {ub} (подмассив равных 5: [{lb}:{ub}])")

    print("\nИнтерполяционный поиск: ищем 11")
    idx = interpolation_search(arr, 11)
    print("  index =", idx)

    print("\nВещественный бинарный поиск: корень x^2 - 2 на [1, 2]")
    f = lambda x: x*x - 2
    root = binary_search_real(f, 1.0, 2.0, epsilon=1e-6)
    print("  sqrt(2) ~", root)

    print("\nТернарный поиск максимума f(x) = -(x-2)^2 + 3 на [0, 4]")
    g = lambda x: -(x - 2.0) ** 2 + 3.0
    argmax = ternary_search(g, 0.0, 4.0, epsilon=1e-6, find_max=True)
    print("  максимум достигается примерно в x ~", argmax)


if __name__ == "__main__":
    _demo_number_theory()
    _demo_search()
