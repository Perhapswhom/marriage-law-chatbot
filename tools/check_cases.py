import re, sys

REQUIRED = ["来源", "发布单位", "发布日期", "原文链接", "效力层级", "审理依据"]
OFFICIAL = re.compile(r"^https://([a-z0-9-]+\.)*(court\.gov\.cn|chinacourt\.org|gov\.cn)(/|$)")
ROLE = re.compile(r"(原告|被告|上诉人|被上诉人|申请人|被申请人|再审申请人|第三人)[：:]?\s*([一-龥]{2,3})(?=[（(，,、与系于向称。])")
SURNAMES = set("王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤颜包洪")
MARK = re.compile(r"【案例\s*([A-Za-z]+-\d+)】")
MAX_CHARS = 1200   # 每行都带【案例 编号】时可以超过（页面会按编号拼回），只提示

text = open(sys.argv[1], encoding="utf-8").read()
parts = re.split(r"(?m)^(?=【案例\s*[A-Za-z]+-\d+】)", text)
head, parts = parts[0], parts[1:]
problems, notes, order, cases = [], [], [], {}
if head.strip():
    problems.append("文件开头有不属于任何案例的文字（每个案例都要以【案例 编号】开头）")
last = None
for p in parts:
    cid = MARK.match(p).group(1)
    if cid in cases and cid != last:
        problems.append(f"案例 {cid}：编号重复（同一个编号出现在两个不相邻的地方）")
    if cid not in cases:
        cases[cid] = []; order.append(cid)
    cases[cid].append(p)
    last = cid
per_line = sum(len(v) > 1 for v in cases.values())
for cid in order:
    raw = "".join(cases[cid])
    b = MARK.sub("", raw) if len(cases[cid]) > 1 else raw   # 每行都带编号的写法：去掉行首编号再检查
    say = lambda msg: problems.append(f"案例 {cid}：{msg}")
    for f in REQUIRED:
        if not re.search(rf"(?m)^{f}[：:]\s*\S", b): say(f"缺少“{f}：”一行")
    link = re.search(r"(?m)^原文链接[：:]\s*(\S+)", b)
    if link and not OFFICIAL.match(link.group(1)):
        say(f"原文链接不是法院或政府网站（{link.group(1)}）。地方法院独立域名、官方公众号文章请人工确认是法院官方发布")
    if len(b) > MAX_CHARS:
        msg = f"有 {len(b)} 字，超过 {MAX_CHARS} 字"
        if len(cases[cid]) > 1: notes.append(f"案例 {cid}：{msg}（每行都带编号，被切开也能拼回，可以保留）")
        else: say(msg + "，可能被切成几段；请只保留官方原文的必要部分并标“（节选）”，或者每行开头都加上【案例 编号】")
    if re.search(r"(?<!\d)\d{17}[\dXx](?!\d)", b): say("疑似身份证号，必须删除")
    if re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", b): say("疑似手机号，必须删除")
    for role, name in sorted(set(ROLE.findall(b))):
        if name[0] in SURNAMES and not re.search(r"[某×*Ｘ]", name): notes.append(f"案例 {cid}：“{role}{name}”可能是真实姓名，请人工核对是否已匿名")
print("案例数:", len(order), "（每行带编号的写法：%d 个）" % per_line)
if notes: print("提示（需要人工看一眼）:\n  " + "\n  ".join(notes))
print("\n".join(problems) if problems else "必查项全部通过")
sys.exit(1 if problems else 0)
