import re
import json

from pyquery import PyQuery as pq

def main():
    with open('/tmp/pyspider_debug.html', encoding='utf-8') as f:
        content = f.read()
    if content.startswith("{"):
        content = json.loads(content)["comment"]
    dq = pq(content)
    import ipdb; ipdb.set_trace()
    pass

if __name__ == '__main__':
    main()