# pair-diff

一个简单的目录结构比较工具，使用 uv 进行包管理。  
A simple directory structure comparison tool, using uv for package management.

## 安装 | Installation

使用 uv 安装：  
Install using uv:

```bash
cd dir_diff
uv sync
```

## 使用方法 | Usage

```bash
# 使用 uv 运行
uv run pair-diff <目录1路径> <目录2路径>

# 或者安装后直接使用
pair-diff <目录1路径> <目录2路径>
```

```bash
# Run with uv
uv run pair-diff <path-to-directory-1> <path-to-directory-2>

# Or use directly after installation
pair-diff <path-to-directory-1> <path-to-directory-2>
```

## 示例 | Examples

```bash
uv run pair-diff ./TensorRT-dir1 ./TensorRT-dir2
```

## 功能 | Features

- 比较两个目录的结构差异  
  Compare the structural differences between two directories
- 以表格形式显示差异  
  Display differences in table format
- 支持颜色输出  
  Support colored output
- 自动忽略常见文件（.git, *.log, tmp, __pycache__）  
  Automatically ignore common files (e.g., .git, *.log, tmp, __pycache__)
- 递归比较子目录  
  Recursively compare subdirectories
- 返回适当的退出码（0=无差异，1=有差异）  
  Return appropriate exit codes (0=no differences, 1=has differences)