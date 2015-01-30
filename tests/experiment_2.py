import re

my_str = """

**1**,**A**,**United Kingdom**,**"62 RRR"de AAA, Paris, France 10929A5"**

**2**,**IN**,**IN Airways**,**'1 Col Blv, Pitts, PA 057'**

"""

pattern = re.compile(r'\*\*\.*?\*\*')
result = re.findall(pattern, my_str)


s = """
‘**1**’,’**A**’,’ **United Kingdom**’,’ **62 RRR"de AAA, Paris, France 10929A5**’

‘**2**’,’**IN**’,’**IN Airways**’,'**1 Col Blv, Pitts, PA 057**'"""


print(result)
print(s)