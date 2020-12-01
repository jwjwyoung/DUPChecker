import sys


def find_median(array):
    n = len(array)
    array.sort()
    if n == 0:
        return None
    if n % 2 == 0:
        med1 = array[n / 2]
        med2 = array[n / 2 - 1]
        median = (med1 + med2) / 2
    else:
        median = array[n / 2]
    return median


app_name = "cassandra"
if len(sys.argv) >= 2:
    app_name = sys.argv[1]
log_name = app_name + "exceptions.log"
f = open(log_name)
output = f.readlines()
results = []
if "size:" not in output[-1]:
    output = output[0:-1]
for line in output:
    values = line.split("size:")
    if values[-1] != "":
        size = int(values[-1])
    else:
        size = 0
    vv = values[0].split(",")
    result = []
    for v in vv:
        cv = v.split(": ")[-1]
        result.append(int(cv))
    result.append(size)
    results.append(result)
exception_size = [row[4] for row in results]

print("max, min, average, median, #changed_v, #total_v")
print(
    max(exception_size),
    min(exception_size),
    sum(exception_size) * 1.0 / len(exception_size),
    find_median(exception_size),
    len([i for i in exception_size if i > 0]),
    len(exception_size),
)
