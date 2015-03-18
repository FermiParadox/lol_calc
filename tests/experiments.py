import re

name = "an4_v20g02p75vmst____4"

print(re.findall(r'_\w+?(g\w+)_', name))