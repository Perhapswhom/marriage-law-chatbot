import re, sys

DIGIT = dict(zip("零一二三四五六七八九", range(10)))
UNIT = {"十": 10, "百": 100, "千": 1000}

def cn2int(s):
    total = cur = 0
    for ch in s:
        if ch in DIGIT:
            cur = DIGIT[ch]
        elif ch in UNIT:
            total += (cur or 1) * UNIT[ch]
            cur = 0
    return total + cur

if len(sys.argv) != 4:
    sys.exit("用法：python check_articles.py 文件.txt 起始条号 结束条号   例：python check_articles.py minfadian-hunyin.txt 1040 1118")
path, LOW, HIGH = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
text = open(path, encoding="utf-8").read()
nums = [cn2int(m) for m in re.findall(r"(?m)^第([零一二三四五六七八九十百千]+)条", text)]
missing = sorted(set(range(LOW, HIGH + 1)) - set(nums))
dup = sorted({n for n in nums if nums.count(n) > 1})
extra = sorted({n for n in nums if not LOW <= n <= HIGH})
print("文件:", path)
print("找到条数:", len(nums), "（应为", HIGH - LOW + 1, "）")
print("缺少的条号:", missing or "无")
print("重复的条号:", dup or "无")
print("范围之外的条号:", extra or "无")
print("顺序是否递增:", nums == sorted(nums))
ok = not missing and not dup and not extra and nums == sorted(nums) and len(nums) == HIGH - LOW + 1
print("结论:", "通过" if ok else "不通过，请对照官方文本修正后再上传")
sys.exit(0 if ok else 1)
