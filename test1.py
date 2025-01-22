import math

list = []
list_tan = []

for i in range(1, 100):
    list.append(math.pi / 99 * i - math.pi / 2)
    list_tan.append(math.tan(math.pi / 99 * i - math.pi / 2))

# print(f"Liste des angles en radians: {list}")
# print(f"Liste des tangentes: {list_tan}")

print(f"angle max: {max(list)}")
print(f"angle min: {min(list)}")
print(f"angle max degrees: {max(list)*180/math.pi}")

print(f"angle min degrees: {min(list)*180/math.pi}")

print(f"tan max: {max(list_tan)}")
print(f"tan min: {min(list_tan)}")
