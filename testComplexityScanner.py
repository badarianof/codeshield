from complexityScanner import calculate_complexity

def test_no_decisions():
    code = """
def say_hello():
    print("hello")
"""
    results = calculate_complexity(code)
    assert results[0]["complexity"] == 1

def test_one_if():
    code = """
def check(x):
    if x > 0:
        return x
    return -x
"""
    results = calculate_complexity(code)
    assert results[0]["complexity"] == 2

def test_for_loop():
    code = """
def add_up(numbers):
    total = 0
    for n in numbers:
        total += n
    return total
"""
    results = calculate_complexity(code)
    assert results[0]["complexity"] == 2

def test_if_and_for():
    code = """
def add_positives(numbers):
    total = 0
    for n in numbers:
        if n > 0:
            total += n
    return total
"""
    results = calculate_complexity(code)
    assert results[0]["complexity"] == 3

test_no_decisions()
print("test_no_decisions passed!")

test_one_if()
print("test_one_if passed!")

test_for_loop()
print("test_for_loop passed!")

test_if_and_for()
print("test_if_and_for passed!")