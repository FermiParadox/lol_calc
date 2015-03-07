with open('my_text_file.txt', 'r') as f:

    lst_of_nums = f.read().split()

    sorted_lst = sorted(lst_of_nums)

    reversed_lst = sorted(lst_of_nums, reverse=True)

print(lst_of_nums)
print(sorted_lst)
print(reversed_lst)