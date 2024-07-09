import subprocess
def exec_code(code: str):
    # 执行 pyhon 代码，返回其中 print 函数输出的结果
    # code: 所要执行的 python 代码，只有执行 print 函数才会得到相应的输出
    result = subprocess.run(['python', '-c', code], capture_output=True, text=True)
    if result.stderr:
        return result.stderr
    if result.stdout:
        return result.stdout