from PIL import Image
import PyPDF2
import io

class FileMerger:
    @staticmethod
    def merge_files(payment_paths, invoice_paths, output_path, existing_pdf_path=None):
        pdf_merger = PyPDF2.PdfMerger()
        
        try:
            if existing_pdf_path:
                with open(existing_pdf_path, 'rb') as existing_pdf:
                    pdf_merger.append(existing_pdf)
            
            for payment_path, invoice_path in zip(payment_paths, invoice_paths):
                # 转换支付记录图片为PDF
                image = Image.open(payment_path)
                pdf_buffer = io.BytesIO()
                image.save(pdf_buffer, format='PDF', resolution=200.0)
                
                # 添加发票
                with open(invoice_path, 'rb') as invoice_file:
                    pdf_merger.append(invoice_file)
                
                # 添加支付记录
                pdf_buffer.seek(0)
                pdf_merger.append(pdf_buffer)
            
            with open(output_path, 'wb') as output_file:
                pdf_merger.write(output_file)
                
            return True, None
            
        except Exception as e:
            return False, str(e)
        finally:
            pdf_merger.close() 