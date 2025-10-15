import math
from typing import List

# -------------------------------
# ?? ?sas dörd ?m?liyyat
# -------------------------------
def add(a, b): return a + b
def subtract(a, b): return a - b
def multiply(a, b): return a * b
def divide(a, b):
    if b == 0: raise ValueError("Division by zero is not allowed")
    return a / b

# -------------------------------
# ?? ?lav? riyazi funksiyalar
# -------------------------------
def power(a, b): return a ** b
def sqrt(a):
    if a < 0: raise ValueError("Cannot take square root of negative number")
    return math.sqrt(a)
def factorial(n):
    if n < 0: raise ValueError("Factorial of negative number is undefined")
    return math.factorial(n)
def modulus(a, b): return a % b
def average(numbers: List[float]):
    if not numbers: raise ValueError("List is empty")
    return sum(numbers)/len(numbers)
def percentage(part, whole):
    return (part/whole)*100

# -------------------------------
# ?? Trigonometriya
# -------------------------------
def sin(x): return math.sin(math.radians(x))
def cos(x): return math.cos(math.radians(x))
def tan(x): return math.tan(math.radians(x))
def cot(x):
    t = math.tan(math.radians(x))
    if t == 0: raise ValueError("Cotangent undefined for this angle")
    return 1/t

# -------------------------------
# ?? Statistik funksiyalar
# -------------------------------
def minimum(numbers: List[float]): return min(numbers)
def maximum(numbers: List[float]): return max(numbers)
def range_of(numbers: List[float]): return max(numbers)-min(numbers)
def median(numbers: List[float]):
    s = sorted(numbers)
    n = len(s)
    if n == 0: raise ValueError("List is empty")
    mid = n//2
    if n%2==0: return (s[mid-1]+s[mid])/2
    return s[mid]

# -------------------------------
# ?? D?yirmil?m? v? dig?r
# -------------------------------
def round_number(a, decimals=2): return round(a, decimals)
def abs_value(a): return abs(a)

# -------------------------------
# ?? H?nd?si hesablamalar
# -------------------------------
def area_of_circle(r): return math.pi * r**2
def circumference(r): return 2*math.pi*r
def area_of_rectangle(l, w): return l*w
def area_of_triangle(b, h): return 0.5*b*h
