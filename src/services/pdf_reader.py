import pdfplumber
import re
from decimal import Decimal

def extract_info_from_pdf(pdf_path):
    """
    从发票PDF中提取物品信息、规格型号和金额
    返回: [(物品名称, 规格型号, 金额), ...]
    """
    items = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                # 先找到价税合计金额
                total_amount = None
                for table in tables:
                    for row in table:
                        if not row or not isinstance(row[0], str):
                            continue
                        text = ' '.join(str(cell) for cell in row if cell)
                        match = re.search(r'价税合计.*?[（(]小写[）)].*?¥(\d+\.\d+)', text)
                        if match:
                            total_amount = Decimal(match.group(1))
                            break
                    if total_amount:
                        break
                
                # 再找商品名称和规格型号
                if total_amount:
                    for table in tables:
                        for row in table:
                            if not row or not isinstance(row[0], str):
                                continue
                            text = ' '.join(str(cell) for cell in row if cell)
                            
                            # 匹配包含*号的行，这通常是商品信息行
                            if '*' in text:
                                # 分割单元格以获取更精确的信息
                                parts = text.split()
                                
                                # 查找商品名称（带*号的部分）
                                for part in parts:
                                    if '*' in part:
                                        name = part
                                        # 获取商品名称后面的部分作为规格型号
                                        name_index = parts.index(part)
                                        if name_index + 1 < len(parts):
                                            # 获取下一个部分作为规格型号
                                            spec = parts[name_index + 1]
                                            items.append((name, spec, total_amount))
                                            return items
                        
    except Exception as e:
        print(f"处理PDF时出错: {str(e)}")
        return []
        
    return items

if __name__ == "__main__":
    pdf_paths = [
        r"E:\Document\BIT\发票\2024年11月-2025年1月\{}.pdf".format(i)
        for i in range(1, 11)
    ]
    
    print("开始测试PDF信息提取...\n")
    for i, pdf_path in enumerate(pdf_paths, 1):
        print(f"=== 处理第 {i} 个文件 ===")
        print(f"文件路径: {pdf_path}")
        results = extract_info_from_pdf(pdf_path)
        
        if not results:
            print("未找到商品信息")
        else:
            for name, spec, amount in results:
                print(f"物品: {name}")
                print(f"规格型号: {spec}")
                print(f"金额: {amount}")
        print()  # 空行分隔 