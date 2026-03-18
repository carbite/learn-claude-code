# 这个文件有几个常见的bug

def divide_numbers(a, b):
    # Bug: 没有处理除零错误
    return a / b

def process_list(items=[]):  # Bug: 可变默认参数
    items.append("processed")
    return items

def read_file(filename):
    # Bug: 文件没有正确关闭
    f = open(filename, 'r')
    data = f.read()
    return data

def find_duplicates(items):
    # 可能的问题：对于空列表的处理
    duplicates = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# 测试
if __name__ == "__main__":
    print("测试1:", divide_numbers(10, 2))
    print("测试2:", process_list())
    print("测试3:", process_list())  # 第二次调用会有问题