"""sanitize() 自检：沙箱跑 scripts/update.py 里的过滤函数，不发网络请求。"""
import sys, types, os, json, tempfile

sys.modules['requests'] = types.SimpleNamespace(exceptions=types.SimpleNamespace(
    Timeout=Exception, ConnectionError=Exception, HTTPError=Exception), get=lambda *a, **k: None)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
import update  # noqa: E402

tmp = tempfile.mkdtemp()
update.BLOCKLIST_FILE = os.path.join(tmp, 'blocklist.txt')
open(update.BLOCKLIST_FILE, 'w', encoding='utf-8').write('成人\n麻豆\nAV\n盘搜\nPanSou\n')

data = {'sites': [
    {'key': 'douban', 'name': '豆瓣'},
    {'key': 'madou', 'name': '麻豆影视'},
    {'key': 'av1', 'name': 'AV精选'},
    {'key': 'seedhub', 'name': 'SEEDHUB 影库'},
    {'key': 'PanSou', 'name': '盘搜', 'api': 'csp_PanSou'},
    {'key': 'Quark', 'name': '夸克 • 网盘', 'api': 'csp_Quark'},
], 'lives': [
    {'name': '央视一套', 'urls': ['http://x.m3u8']},
    {'name': '成人频道', 'urls': ['http://y.m3u8']},
], 'spider': 'keep-me.jar'}

out = update.sanitize(data)
assert [s['key'] for s in out['sites']] == ['douban', 'seedhub', 'Quark'], out['sites']
assert [l['name'] for l in out['lives']] == ['央视一套'], out['lives']
assert out['spider'] == 'keep-me.jar'
# 原对象不被就地修改
assert len(data['sites']) == 6
# 文件缺失时退回内置表（内置表含“香蕉”）
update.BLOCKLIST_FILE = os.path.join(tmp, 'nope.txt')
assert update.load_blocklist()[0] in ('成人', '18+', '情色')
assert update.sanitize({'sites': [{'key': 'a', 'name': '香蕉TV'}]})['sites'] == []
print('sanitize self-check OK: 6 站/2 直播 -> 3 站/1 直播，关键词表加载与回退正常')
