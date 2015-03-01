import re




l = """
VCM1b_00048 ACY66696.1 40.18 112 67 0 25 136 24 135 4e-16 71.2 VCM1b-phage Klebsiella-phage-KP32
"""





m = re.search(r'(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)\s(\S*)', l)


print(m.group(0))
print(m.group(1))
print(m.group(2))
print(m.group(3))