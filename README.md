# Codex Desktop & Browser Skills

一组面向 Windows 的 Codex skills，用于后台操作桌面和浏览器、处理学习通网页作业，以及验证 C 语言作业的精确输出。

目标是让自动化更稳定、更快，同时保留明确的安全边界：优先使用 DOM/UI Automation，不抢用户焦点、不读取或保存登录凭证、不自动提交作业。

## Skills

| Skill | 用途 |
| --- | --- |
| `desktop-operator` | 通过常驻的本地 Desktop Operator 操作浏览器、原生窗口、窗口截图和 OCR |
| `chaoxing-coursework` | 使用已有的 Edge 登录态和无头 CDP 读取、填写、运行并暂时保存学习通作业 |
| `c-coursework-verify` | 编译 C 作业，按样例和边界用例逐字节比较输出 |

`desktop-operator` 的运行时位于独立的 MIT 开源仓库：
[gz2008/desktop-operator](https://github.com/gz2008/desktop-operator)。

## 安装 Skills

```powershell
git clone https://github.com/gz2008/codex-desktop-browser-skills.git
cd codex-desktop-browser-skills
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

默认安装到 `$env:CODEX_HOME\skills`；未设置 `CODEX_HOME` 时使用
`$HOME\.codex\skills`。指定其他位置：

```powershell
.\install.ps1 -CodexHome "$HOME\.codex"
```

如果目标目录已经存在，脚本会停止。确认要覆盖旧版本时使用 `-Force`。

## 安装 Desktop Operator

`desktop-operator` skill 需要对应的运行时。推荐安装到 Codex 工作目录：

```powershell
$operatorHome = Join-Path $HOME '.codex\tools\desktop-operator'
git clone https://github.com/gz2008/desktop-operator.git $operatorHome
cd $operatorHome
.\setup.ps1
.\op.ps1 system.info
```

如果运行时不在默认位置，在启动 Codex 前设置：

```powershell
$env:DESKTOP_OPERATOR_HOME = 'D:\path\to\desktop-operator'
```

要求 Windows 10/11、PowerShell 5.1+、Python 3.11-3.13 和 Microsoft Edge。
`chaoxing-coursework` 还需要 Playwright Python 包。

## 安全边界

- 只操作当前用户明确指定的本地页面、窗口和作业。
- 仅在课程平台规则允许且用户有权操作的环境中自动化；不绕过登录、验证码或平台限制。
- 优先使用后台 CDP/DOM 和 UI Automation，不主动置顶或抢焦点。
- 不请求、输出、复制或保存密码、Cookie、Token 和会话值。
- 需要登录时由用户在本地完成；学习通扫码图中的二维码不长期保留。
- 网页作业默认只暂时保存，未经用户明确要求不点击提交。
- Desktop Operator 只监听 `127.0.0.1`，不用于远程控制或凭据提取。

## 验证

```powershell
python -m pip install pyyaml
python .\scripts\validate_skills.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 `
  -CodexHome "$env:TEMP\skill-install-test"
```

CI 会对每个 skill 的 frontmatter、名称、相对链接和占位内容做检查。

## License

[MIT](LICENSE)
