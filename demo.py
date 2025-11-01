def add(a,b):
  return a+b

print("sum=" + str(add(1,2)))
cat >> demo.py <<'PY'

# TODO: refactor this function
def dump_lines(path):
    f = open(path, "r")  # intentionally no context manager
    data = f.read()
    f.close()
    return data

def print_status(url):
    import requests
    r = requests.get(url)  # intentionally no timeout
    print("status=" + str(r.status_code))  # prefer f-string

items = ["a", "b", "c"]
for i in range(len(items)):  # prefer enumerate
    print(items[i])

try:
    risky = 1 / 0
except:
    print("oops")  # bare except on purpose
PY
