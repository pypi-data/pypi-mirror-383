# FuzzyTri

Noravshan mantiq nazariyasi va amaliyoti uchun Python kutubxonasi.

## O'rnatish

```bash
pip install fuzzytri
```

## Yoki manba koddan o'rnatish:

* git clone https://github.com/username/fuzzytri.git
* cd fuzzytri
* pip install -e .

## Tezkor Boshlash

```
from fuzzytri import FuzzyTriangular, FuzzyOperations

# Vektorlar yaratish
v1 = FuzzyTriangular(3.0, 2.0, 1.0)
v2 = FuzzyTriangular(2.0, 1.0, 3.0)

# Asosiy operatsiyalar
qoshish = v1 + v2
ayirish = v1 - v2
kopaytirish = v1 * v2
bolish = v1 / v2

print(f"Qo'shish: {qoshish}")
print(f"Ko'paytirish: {kopaytirish}")
```

## Loyihani Ishga Tushirish

```
# Kutubxonani o'rnatish
pip install -e .

# Testlarni ishga tushirish
pytest

# Misollarni ishga tushirish
python examples/basic_usage.py
python examples/advanced_operations.py
```

#� �f�u�z�z�y�t�r�i�
�
�
