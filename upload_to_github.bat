@echo off
echo 请先在GitHub上创建名为 crypto-price-checker 的仓库
echo 然后将下面的YOUR_USERNAME替换为你的GitHub用户名
echo.
pause

REM 替换YOUR_USERNAME为你的实际GitHub用户名
git remote add origin https://github.com/Aci1998/crypto-price-checker.git
git push -u origin main

echo.
echo 上传完成！
pause