# book_transform

将 `raw_book` 文件夹中的电子书（`.pdf`、`.epub`）转换为纯文本 `.txt`，并输出到 `txt_book`。  
如果目标 `.txt` 已存在，会自动跳过，避免重复转换。

## 目录结构

```text
book_transform/
├── raw_book/            # 放原始电子书
├── txt_book/            # 输出的 txt 文件
├── transform_books.py   # 转换脚本
└── environment.yml      # conda 环境配置
```

## 功能说明

- 支持格式：`.pdf`、`.epub`
- 递归扫描：会扫描 `raw_book` 下所有子目录
- 跳过已转换：若 `txt_book` 中对应 `.txt` 已存在则跳过
- 保留目录结构：输出时保持与 `raw_book` 相同的相对路径

## 环境配置（conda）

### 方式 1：直接使用已有环境

```bash
conda activate book_transform
```

### 方式 2：从 `environment.yml` 创建

```bash
conda env create -f environment.yml
conda activate book_transform
```

## 使用方法

1. 把需要转换的书放入 `raw_book/`
2. 运行脚本：

```bash
python transform_books.py
```

脚本默认使用：
- 输入目录：`raw_book`
- 输出目录：`txt_book`

你也可以自定义目录：

```bash
python transform_books.py --raw-dir raw_book --txt-dir txt_book
```

## 运行结果示例

```text
INFO: Converted: raw_book/demo.pdf -> txt_book/demo.txt
INFO: Skip (already exists): txt_book/demo.txt
INFO: Done. converted=1 skipped=1 failed=0
```

## 注意事项

- PDF 文本提取效果取决于原文件质量（扫描版 PDF 可能提取不到文字）。
- EPUB 转换会提取正文中的文本内容，排版信息不会保留。
