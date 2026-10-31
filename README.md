# 基督使人纷争——甚至在教会中也是如此 · 讲章学习站

## 🔗 三个链接

| | 链接 |
|---|---|
| 🌐 **GitHub Pages** | **<https://08-ser-grok-je-personal-20261003.github.io/christ-divides-mt10-20261031-v1-GROKser/>** |
| 🌐 **Surge** | **<https://christ-divides-mt10-20261031-v1-grokser.surge.sh>** |
| 📦 **GitHub 仓库** | **<https://github.com/08-Ser-Grok-Je-Personal-20261003/christ-divides-mt10-20261031-v1-GROKser>** |

> 诗歌：圣诗 4 首；韵诗 3 篇、韵诗 2 篇；诗篇 23 篇（仅列编号，不含歌词）
> 读经：**马太福音 10:5–39**　证经：**约翰福音 7:40–44**
> 主题：**基督使人纷争——甚至在教会中也是如此**
> 一、基督带来的是什么样的纷争？　二、基督怎样带来这种纷争？　三、基督为什么带来这种纷争？

这是一个多页静态讲章学习站，全部用简体中文，按欧陆改革宗传统编写：三项联合信条（海德堡要理问答、比利时信条、多特信经）加三大普世信经。
- 站点是纯静态的，不用 CDN，使用系统中文字体栈。
- 支持亮色/深色主题、玻璃拟态、可折叠目录和响应式布局。
- 主线：基督自己是分界线，他藉他的道把人分开，为要招聚一个在真道上合一的教会。站内分辨「因着耶稣」的纷争（约7:43）与属肉体的分党（林前1:10，同一个字 *schisma*），驳斥假和平、好斗主义与分离主义。

版本：**v1（2026-10-31）**，变更见 [CHANGELOG.md](CHANGELOG.md)。

## 页面一览

**核心页面（顶部导航）**

| 文件 | 内容 |
|---|---|
| `sermon.html` | **讲章**（全站中心）：先整体后局部；三点每点都有主旨、释经、难点、七个角度；两种 *schisma* 对照；四重闭环；与信经信条的一致 |
| `background.html` | 背景·地图：作者、受众、年代（不同观点并陈）、住棚节背景、加利利—犹太示意地图、差遣的处境、在全本圣经中的位置、平行经文 |
| `discussion.html` | 13 道讨论题与答案分析 |
| `memory.html` | 记忆·总结：思维导图、太10五段流程、「分·剑·合·安」口诀、SWORD 藏头、数字诀、总表、闪卡 |
| `creeds.html` | 三大信经干净阅读版：逐句遮盖、首字提示、随机挖空、朗读 |
| `compare.html` | 三大信经深度对比 |
| `index.html` | 首页：一分钟记住本讲、动画、学习路径 |
| `worship.html` | 诗歌（只列编号）、诗3/2/23篇和合本经文、敬拜次序建议 |

**参考资料（菜单「页面」中）**

| 文件 | 内容 |
|---|---|
| `tfu.html` | 三项联合信条精选：HC 1、20–21、31–32、54、84–86；BC 27–29、37；CD I.6、15，III/IV.9–10，V.9、11 |
| `extension.html` | 延伸专题（两种后裔之线、真假合一、教会纪律、宗派与分离、信主家庭、不要怕人）与辩正清单 |
| `hc.html` `bc.html` `cd.html` | 海德堡要理问答、比利时信条、多特信经全文（逐字，仅作参考） |
| `sources.html` | 资料来源与**逐字核对报告** |

## 目录结构

```
├── *.html                 # 生成结果（直接部署这些文件 + assets/）
├── assets/style.css       # 设计系统：亮/暗主题、玻璃拟态、响应式、动画
├── assets/app.js          # 主题切换、可折叠目录、进度条、背诵引擎、翻转卡片等
├── content/*.html         # 页面源文件：front-matter + HTML + {{宏}}
├── data/
│   ├── bop.json           # 从 ccifellowship.org 抓取并解析的信经/信条文本
│   ├── cuv_used.json      # 本站用到的和合本章节（来自 getbible.net 的 cus 译本）
│   ├── maps/*.json        # 由 Natural Earth 公有领域数据简化得到的地图路径
│   └── source_pages/      # 其他被引用页面的存档（引句核对用）
├── tools/
│   ├── build.py           # 生成器（内容宏 + 逐字断言）
│   ├── maps.py mapgen.py  # SVG 图示与地图
│   ├── verify.py          # 在线重抓并逐字比对
│   ├── qa.py linkcheck.py # 浏览器 QA（375/768/1280）与站内链接检查
│   ├── fetch/             # 抓取脚本（crawl_bop / extract_bop / fetch_cuv）
│   └── deploy_surge.sh    # 部署到 surge（使用本机已登录账号，不存任何密码）
└── reports/               # verify.json/txt、qa.json（截图不入库）
```

## 如何修改内容

1. 编辑 `content/*.html`。文件开头是 front-matter（`title` `h1` `lead` `badges`，以 `---` 结束），其后是普通 HTML。
2. **信经与信条文字不要手打**，用宏注入，构建时会断言「引句必须是来源原文的子串」：

| 宏 | 作用 |
|---|---|
| `{{bible:太10:34-39\|hl=34}}` / `{{bq:约7:43}}` | 和合本经文块 / 行内引句 |
| `{{hc:1}}` `{{hc:26-28}}` `{{hcm:60}}` `{{hcq:44\|片段}}` | 海德堡问答（完整 / 迷你 / 引句） |
| `{{bc:13}}` `{{bcq:13\|片段}}` | 比利时信条 |
| `{{cd:5.10-11}}` `{{cdq:5.5\|片段}}` | 多特信经（`1` `2` `34` `5` 为四项教义） |
| `{{crq:apostles\|片段}}` | 三大信经引句（`apostles` `nicene` `athanasian`） |
| `{{creed:key}}` `{{creedintro:key}}` `{{intro:hc}}` | 信经全文 / 简介 |
| `{{ccq:源键\|片段}}` | 其他已抓取页面的引句 |
| `{{map:galilee}}` 等 | `galilee` `loop-redemptive` `triad` `mindmap` `sword` `church` |

3. 重新生成：`python3 tools/build.py`（依赖：Python 3.10+，`beautifulsoup4`；重新生成地图另需 `shapely`）。
4. 检查：
   ```bash
   python3 tools/verify.py      # 在线重抓 ccifellowship.org 等并逐字比对 → reports/verify.json
   python3 tools/build.py       # 再构建一次，把核对报告写进 sources.html
   python3 tools/linkcheck.py   # 站内链接与锚点
   python3 tools/qa.py --shots  # 需 playwright + Chrome；检查横向溢出/重叠/锚点/JS 错误
   ```
5. 重新抓取源文本（可选）：`cd _src && python3 ../tools/fetch/crawl_bop.py && python3 ../tools/fetch/extract_bop.py && cp bop.json ../data/bop.json`；和合本：`python3 ../tools/fetch/fetch_cuv.py`。

## 部署

**GitHub Pages**（分支部署，已含 `.nojekyll`）：

```bash
gh api -X POST repos/08-Ser-Grok-Je-Personal-20261003/christ-divides-mt10-20261031-v1-GROKser/pages \
  -f 'source[branch]=main' -f 'source[path]=/'
```

**Surge**：使用本机已登录的 surge 账号，任何文件里都不写密码。

```bash
npx surge whoami                    # 确认已登录
tools/deploy_surge.sh               # 默认域名 christ-divides-mt10-20261031-v1-grokser.surge.sh
```

## 资料来源与诚实说明

- 三大信经、海德堡要理问答、比利时信条、多特信经的**中文文本全部来自 [ccifellowship.org](https://ccifellowship.org)**。页面逐字注入，并用 `tools/verify.py` 在线核对（见 `sources.html`）。
- 讲章中的叙述性引句（创3:15、创4、林前1–4 证道，海德堡主日21、48 证道，《我属于主》，《灯台声明》等）同样来自 ccifellowship.org，已逐字核对。
- 经文：和合本（getbible.net `cus`），上线前在线逐节核对。
- 地图底图：Natural Earth（公有领域）。加利利海轮廓、区域范围、路线与地点位置是**示意**。
- **未抓取、只作转述或背景**的内容在页面与 `sources.html` 中都有标明，不含伪引文。这包括：威斯敏斯特标准（只作意译）、马太/约翰福音的成书年代、住棚节礼仪（《密西拿》）、约瑟夫的记载、希腊文观察、注释家观点、教会历史事件。
- 诗歌只列编号，不含歌名和歌词。

## 许可

站点自写内容仅供教会与个人学习使用。信经和信条文本的版权与使用条件以 ccifellowship.org 为准；和合本为公有领域。
