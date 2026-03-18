# 这是一个有bug的测试文件
# 用于演示代码代理的修复功能

def calculate_average(numbers):
    # 计算平均值
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def find_max(numbers):
    # 查找最大值
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

def process_data(data):
    # 处理数据
    result = []
    for item in data:
        processed = item * 2  # 简单的处理
        result.append(processed)
    return result

# 测试代码
if __name__ == "__main__":
    # 测试平均值计算
    test_numbers = [1, 2, 3, 4, 5]
    print(f"平均值: {calculate_average(test_numbers)}")
    
    # 测试最大值查找
    print(f"最大值: {find_max(test_numbers)}")
    
    # 测试数据处理
    print(f"处理结果: {process_data(test_numbers)}")