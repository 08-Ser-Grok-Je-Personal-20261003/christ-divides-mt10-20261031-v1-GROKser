#!/usr/bin/env bash
# 把站点（只含 HTML 与 assets）复制到临时目录后部署到 surge.sh。
# 使用本机已登录的 surge 账号（`npx surge login` 或 `npx surge whoami` 查看）；
# 也可设置环境变量 SURGE_LOGIN / SURGE_TOKEN。脚本与仓库中不保存任何密码或令牌。
# 用法： tools/deploy_surge.sh [域名]
set -euo pipefail
cd "$(dirname "$0")/.."
DOMAIN="${1:-christ-divides-mt10-20261031-v1-grokser.surge.sh}"
python3 tools/build.py
STAGE="$(mktemp -d)"
cp -r assets "$STAGE/assets"
cp ./*.html "$STAGE/"
npx --yes surge "$STAGE" "$DOMAIN"
rm -rf "$STAGE"
echo "已部署：https://$DOMAIN"
