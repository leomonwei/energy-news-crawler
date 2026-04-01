# utils/storage_handler.py
"""
数据存储处理器
支持 CSV、Excel 格式
版本：2.0 - 增强编码处理和错误处理
"""
import csv
import os
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Optional

class StorageHandler(ABC):
    """存储抽象基类"""
    
    @abstractmethod
    def save(self, data: List[Dict], **kwargs):
        """
        保存数据
        
        Args:
            data: 数据列表
            **kwargs: 其他参数
        """
        pass


class CSVStorage(StorageHandler):
    """CSV 存储实现"""
    
    def save(self, data: List[Dict], file_path: str, encoding: str = 'utf-8-sig', delimiter: str = ','):
        """
        保存数据到 CSV 文件
        
        Args:
            data: 数据列表
            file_path: 输出文件路径
            encoding: 文件编码（默认 utf-8-sig，兼容 Excel）
            delimiter: 分隔符（默认逗号）
        """
        if not data:
            print("⚠️  无数据可保存")
            return
        
        try:
            # 自动创建目录
            output_dir = os.path.dirname(file_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 获取所有字段名（处理不同文章可能有不同字段的情况）
            fieldnames = []
            for item in data:
                for key in item.keys():
                    if key not in fieldnames:
                        fieldnames.append(key)
            
            # 写入 CSV
            with open(file_path, 'w', newline='', encoding=encoding, errors='replace') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=fieldnames,
                    delimiter=delimiter,
                    quoting=csv.QUOTE_MINIMAL  # 只在必要时引用
                )
                writer.writeheader()
                
                for row in data:
                    # 确保所有字段都存在
                    complete_row = {field: row.get(field, '') for field in fieldnames}
                    writer.writerow(complete_row)
            
            print(f"✅ 数据已保存至 CSV 文件：{file_path}")
            print(f"   编码：{encoding}，记录数：{len(data)}")
            
        except PermissionError:
            print(f"❌ 权限错误：无法写入文件 {file_path}")
            raise
        except Exception as e:
            print(f"❌ CSV 保存失败：{e}")
            raise


class ExcelStorage(StorageHandler):
    """Excel 存储实现"""
    
    def save(self, data: List[Dict], file_path: str, sheet_name: str = 'Sheet1'):
        """
        保存数据到 Excel 文件
        
        Args:
            data: 数据列表
            file_path: 输出文件路径
            sheet_name: 工作表名称
        """
        if not data:
            print("⚠️  无数据可保存")
            return
        
        try:
            # 自动创建目录
            output_dir = os.path.dirname(file_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 转换为 DataFrame
            df = pd.DataFrame(data)
            
            # 清理数据（处理 None 和特殊字符）
            df = df.fillna('')
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(
                        lambda x: ''.join(
                            char for char in str(x) 
                            if ord(char) >= 32 or char in '\n\r\t'
                        ).strip() if isinstance(x, str) else x
                    )
            
            # 保存为 Excel
            df.to_excel(file_path, index=False, sheet_name=sheet_name)
            
            print(f"✅ 数据已保存至 Excel 文件：{file_path}")
            print(f"   记录数：{len(data)}")
            
        except PermissionError:
            print(f"❌ 权限错误：无法写入文件 {file_path}")
            raise
        except Exception as e:
            print(f"❌ Excel 保存失败：{e}")
            raise


class MySQLStorage(StorageHandler):
    """MySQL 存储实现（可选）"""
    
    def __init__(self, connection_string: str):
        """
        初始化 MySQL 连接
        
        Args:
            connection_string: 数据库连接字符串
        """
        self.connection_string = connection_string
        self.connection = None
    
    def save(self, data: List[Dict], table_name: str, batch_size: int = 100):
        """
        保存数据到 MySQL 数据库
        
        Args:
            data: 数据列表
            table_name: 表名
            batch_size: 批次大小
        """
        if not data:
            print("⚠️  无数据可保存")
            return
        
        try:
            import pymysql
            
            # 连接数据库
            self.connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='news_crawler',
                charset='utf8mb4'
            )
            
            cursor = self.connection.cursor()
            
            # 批量插入
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                for item in batch:
                    if not item.get('title'):
                        continue
                    
                    # 构建 SQL
                    columns = ', '.join(item.keys())
                    placeholders = ', '.join(['%s'] * len(item))
                    sql = f"""
                        INSERT INTO {table_name} ({columns})
                        VALUES ({placeholders})
                        ON DUPLICATE KEY UPDATE
                        title = VALUES(title)
                    """
                    
                    cursor.execute(sql, list(item.values()))
                
                self.connection.commit()
            
            cursor.close()
            print(f"✅ 数据已保存至 MySQL：{table_name}，记录数：{len(data)}")
            
        except ImportError:
            print("❌ 需要安装 pymysql: pip install pymysql")
            raise
        except Exception as e:
            print(f"❌ MySQL 保存失败：{e}")
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            if self.connection:
                self.connection.close()
