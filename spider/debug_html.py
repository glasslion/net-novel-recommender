import re
from pyquery import PyQuery as pq

def main():
    with open('/tmp/pyspider_debug.html', encoding='utf-8') as f:
        content = f.read()
    dq = pq(content)
    import ipdb; ipdb.set_trace()
    pass

if __name__ == '__main__':
    main()