my_string = """asdasd
==See also==
*[[ALGOL]]
*[[Lua (programming language)]]
*[[Squirrel (programming language)]]

==References==
*[http://www.caida.org/home/seniorstaff/nevil.xml Nevil Brownlee]

[[Category:Algol programming language family]]
[[Category:Systems programming languages]]
[[Category:Procedural programming languages]]
[[Category:Object-oriented programming languages]]
[[Category:Programming languages created in the 1980s]]
"""

import re

# Sliced_string will only contain the characters between '==See also==' and '==References=='
sliced_string = re.findall(r'==See also==(.*?)==References==', my_string, re.DOTALL)[-1]

# Removes stars and brackets
for unwanted_char in '[]*':
    sliced_string = sliced_string.replace(unwanted_char, '')

# Creates a list of strings (also removes empty strings)
final_list = sliced_string.split('\n')
final_list = [elem for elem in final_list if elem != '']

print(final_list)