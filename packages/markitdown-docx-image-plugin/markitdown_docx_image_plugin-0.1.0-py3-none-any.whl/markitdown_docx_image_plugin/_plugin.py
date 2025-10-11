"""
MarkItDown插件: DOCX图片提取器

使用mammoth自定义图片转换器，确保图片位置完全正确
"""
import io
import os
import sys
import uuid
from pathlib import Path
from typing import BinaryIO, Any
from warnings import warn

from markitdown import (
    MarkItDown,
    DocumentConverter,
    DocumentConverterResult,
    StreamInfo,
)

__plugin_interface_version__ = 1

# 尝试导入依赖
_dependency_exc_info = None
try:
    import mammoth
    from markdownify import markdownify
except ImportError:
    _dependency_exc_info = sys.exc_info()

ACCEPTED_MIME_TYPE_PREFIXES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

ACCEPTED_FILE_EXTENSIONS = [".docx"]


def register_converters(markitdown: MarkItDown, **kwargs):
    """
    注册图片提取的DOCX转换器
    """
    # 优先级设为-1.0，使其在标准DOCX转换器之前运行
    markitdown.register_converter(
        DocxImageExtractorConverter(),
        priority=-1.0
    )


class DocxImageExtractorConverter(DocumentConverter):
    """
    将DOCX文件转换为Markdown，同时提取图片到目录中
    使用mammoth的自定义图片转换器确保图片位置正确
    """

    def __init__(self):
        super().__init__()

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """检查是否是DOCX文件"""
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True

        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """转换DOCX文件并提取图片"""
        
        # 检查依赖
        if _dependency_exc_info is not None:
            raise ImportError(
                "缺少必需的依赖包。请安装: pip install mammoth markdownify"
            ) from _dependency_exc_info[1]

        # 获取配置
        image_dir = kwargs.get("image_output_dir", "docx_images")
        
        # 获取文件基础名称
        base_name = self._get_base_name(stream_info)
        
        # 创建图片输出目录
        image_output_path = Path(image_dir)
        image_output_path.mkdir(parents=True, exist_ok=True)
        
        # 图片计数器和保存列表
        image_counter = {'count': 0}
        saved_images = []
        
        def convert_image(image):
            """
            自定义图片转换函数
            mammoth会对每个图片调用这个函数
            """
            try:
                image_counter['count'] += 1
                img_index = image_counter['count']
                
                # 读取图片数据
                with image.open() as image_file:
                    image_bytes = image_file.read()
                
                # 跳过空图片
                if len(image_bytes) == 0:
                    warn(f"跳过空图片 (index {img_index})")
                    return {}
                
                # 确定文件扩展名
                content_type = image.content_type or 'image/png'
                ext_map = {
                    'image/png': '.png',
                    'image/jpeg': '.jpg',
                    'image/jpg': '.jpg',
                    'image/gif': '.gif',
                    'image/bmp': '.bmp',
                    'image/tiff': '.tiff',
                }
                ext = ext_map.get(content_type, '.png')
                
                # 生成唯一文件名（使用UUID确保唯一性）
                unique_id = uuid.uuid4().hex[:12]  # 使用12位UUID
                filename = f"{base_name}_image{img_index}_{unique_id}{ext}"
                filepath = image_output_path / filename
                
                # 保存图片
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                saved_images.append(filename)
                
                # 返回图片src（支持从环境变量读取图片服务器host）
                image_host = os.environ.get('IMAGE_SERVER_HOST', '').strip()
                if image_host:
                    # 确保host不以/结尾
                    image_host = image_host.rstrip('/')
                    src = f"{image_host}/{image_dir}/{filename}"
                else:
                    # 使用相对路径
                    src = f"{image_dir}/{filename}"
                
                return {
                    "src": src
                }
                
            except Exception as e:
                warn(f"图片 {img_index} 处理失败: {e}")
                # 返回空，但不中断处理
                return {}
        
        # 使用mammoth转换，指定自定义图片转换器
        # 注意：需要重置文件流位置
        file_stream.seek(0)
        result = mammoth.convert_to_html(
            file_stream,
            convert_image=mammoth.images.img_element(convert_image),
            # 不忽略空段落，保留更多结构
            ignore_empty_paragraphs=False
        )
        html_content = result.value
        
        # 打印警告信息到stderr（如果有）
        if result.messages:
            for msg in result.messages:
                if 'warning' in msg.type or 'error' in msg.type:
                    print(f"  ⚠️  Mammoth {msg.type}: {msg.message}", file=sys.stderr)
        
        # 预处理HTML：将只包含图片的表格转换为段落
        # 因为markdownify会丢弃表格中的图片
        html_content = self._extract_images_from_tables(html_content)
        
        # 转换HTML为Markdown
        markdown_content = markdownify(html_content)
        
        # 输出提示信息到stderr
        if image_counter['count'] > 0:
            print(f"✓ DOCX图片提取插件: 已提取 {image_counter['count']} 张图片到 {image_dir}/ 目录", file=sys.stderr)
        
        return DocumentConverterResult(
            markdown=markdown_content,
            title=None,
        )

    def _get_base_name(self, stream_info: StreamInfo) -> str:
        """获取文件的基础名称（不含扩展名）"""
        if stream_info.filename:
            return Path(stream_info.filename).stem
        elif stream_info.local_path:
            return Path(stream_info.local_path).stem
        else:
            return "document"
    
    def _extract_images_from_tables(self, html_content: str) -> str:
        """
        预处理HTML：将只包含图片的表格转换为段落
        因为markdownify会丢弃表格中的图片
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找所有表格
            for table in soup.find_all('table'):
                # 检查表格是否只包含一个单元格且只有图片
                rows = table.find_all('tr')
                if len(rows) == 1:
                    cells = rows[0].find_all(['td', 'th'])
                    if len(cells) == 1:
                        cell = cells[0]
                        # 获取单元格中的所有内容
                        imgs = cell.find_all('img')
                        # 如果单元格只包含图片（可能在p标签中）
                        if imgs:
                            # 检查是否只有图片和空白
                            text_content = cell.get_text(strip=True)
                            if not text_content:  # 只有图片，没有文字
                                # 将表格替换为段落包含的图片
                                new_p = soup.new_tag('p')
                                for img in imgs:
                                    new_p.append(img.extract())
                                table.replace_with(new_p)
            
            return str(soup)
        
        except Exception as e:
            warn(f"处理表格中的图片时出错: {e}")
            return html_content
