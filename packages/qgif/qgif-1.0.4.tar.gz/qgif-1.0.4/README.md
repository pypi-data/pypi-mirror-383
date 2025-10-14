## QGIF 简介

将 gif 图转换为国芯微自研的 qgif 动画格式，用于在国芯微芯片上显示。
qgif 可以降低 Flash 占用，并提升动画帧率。

## 使用帮助

    python -m qgif --help
    python -m qgif convert --help

## 使用例子

    python -m qgif convert -i test.gif -o test.qgif -f gx64
