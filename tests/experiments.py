s = '{{ asdasd{} }} {{ }}'


if __name__ == '__main__':

    import re

    pattern = re.compile(r'\{\{.*?\}\}', re.DOTALL)

    print(re.findall(pattern, s))