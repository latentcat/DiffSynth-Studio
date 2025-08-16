#!/bin/bash
# -*- coding: utf-8 -*-
# 解压分卷7z文件到traindatas目录

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查7z命令是否存在
check_7z() {
    if ! command -v 7z &> /dev/null; then
        print_error "7z命令未找到，请先安装p7zip-full"
        print_info "Ubuntu/Debian: sudo apt-get install p7zip-full"
        print_info "CentOS/RHEL: sudo yum install p7zip p7zip-plugins"
        print_info "macOS: brew install p7zip"
        exit 1
    fi
}

# 检查分卷文件是否存在
check_archive_files() {
    local base_file="datas.7z.001"
    
    if [ ! -f "$base_file" ]; then
        print_error "未找到分卷文件 $base_file"
        print_info "请确保当前目录下存在 datas.7z.001, datas.7z.002 等分卷文件"
        exit 1
    fi
    
    # 统计分卷文件数量
    local count=$(ls datas.7z.* 2>/dev/null | wc -l)
    print_info "找到 $count 个分卷文件"
    
    # 列出所有分卷文件
    print_info "分卷文件列表:"
    ls -la datas.7z.* | while read line; do
        echo "  $line"
    done
}

# 创建目标目录
create_target_dir() {
    local target_dir="./traindatas"
    
    if [ -d "$target_dir" ]; then
        print_warning "目标目录 $target_dir 已存在"
        read -p "是否要清空现有目录？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "清空目录 $target_dir"
            rm -rf "$target_dir"/*
        fi
    else
        print_info "创建目标目录 $target_dir"
        mkdir -p "$target_dir"
    fi
}

# 解压分卷文件
extract_archives() {
    local base_file="datas.7z.001"
    local target_dir="./traindatas"
    
    print_info "开始解压分卷文件..."
    print_info "源文件: $base_file"
    print_info "目标目录: $target_dir"
    
    # 使用7z解压第一个分卷文件，会自动处理所有分卷
    if 7z x "$base_file" -o"$target_dir" -y; then
        print_success "解压完成！"
        
        # 显示解压后的文件信息
        print_info "解压后的文件结构:"
        if command -v tree &> /dev/null; then
            tree "$target_dir" -L 2
        else
            find "$target_dir" -type f | head -20
            local total_files=$(find "$target_dir" -type f | wc -l)
            if [ $total_files -gt 20 ]; then
                print_info "... 还有 $((total_files - 20)) 个文件"
            fi
        fi
        
        # 显示目录大小
        local dir_size=$(du -sh "$target_dir" | cut -f1)
        print_success "解压完成，总大小: $dir_size"
        
    else
        print_error "解压失败！"
        exit 1
    fi
}

# 清理函数（可选）
cleanup_archives() {
    read -p "是否要删除原始分卷文件？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "删除原始分卷文件..."
        rm -f datas.7z.*
        print_success "原始分卷文件已删除"
    else
        print_info "保留原始分卷文件"
    fi
}

# 主函数
main() {
    print_info "=== 7z分卷文件解压工具 ==="
    print_info "当前工作目录: $(pwd)"
    
    # 检查依赖
    check_7z
    
    # 检查分卷文件
    check_archive_files
    
    # 创建目标目录
    create_target_dir
    
    # 解压文件
    extract_archives
    
    # 可选清理
    cleanup_archives
    
    print_success "所有操作完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi