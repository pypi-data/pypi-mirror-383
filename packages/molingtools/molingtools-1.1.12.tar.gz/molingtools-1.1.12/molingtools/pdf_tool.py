try:
    import fitz 
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install PyMuPDF')
import os
import hashlib


def extract_pdf(pdf_path, img_folder: str | None = None) -> tuple[str, list[str]]:
    """
    Returns:
        tuple[str, list[str]]: 文本内容+图片路径列表
    """
    pdf_document = fitz.open(pdf_path)
    # 创建输出文件夹（如果不存在）
    if img_folder and not os.path.exists(img_folder): os.makedirs(img_folder)
    full_text, imgs = "",[]
    # 遍历 PDF 中的每一页
    for page in pdf_document:
        # 提取文本（使用dict模式获取位置信息）
        page_dict = page.get_text("dict")
        # 提取图片并保存，同时记录位置信息
        image_list = page.get_images(full=True)
        page_images_with_pos = []
        if img_folder:
            for img in image_list:
                try:
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    # 生成图片文件名
                    md5 = hashlib.md5()
                    md5.update(image_bytes)
                    img_name = md5.hexdigest() + f'.{image_ext}'
                    image_path = os.path.join(img_folder, img_name)
                    # 保存图片
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    # 获取图片在页面中的位置
                    img_bbox = page.get_image_bbox(img)  # 获取图片边界框
                    page_images_with_pos.append({
                        'path': image_path,
                        'bbox': img_bbox,
                        'y_pos': img_bbox.y0,  # 使用顶部Y坐标排序
                        'x_pos': img_bbox.x0   # X坐标用于同一行图片排序
                    })                    
                    imgs.append(image_path)
                except Exception as e:
                    print(f"处理图片时出错: {e}")
        # 按Y坐标排序图片（从上到下）
        page_images_with_pos.sort(key=lambda x: (x['y_pos'], x['x_pos']))
        # 收集所有文本块和图片块，按位置排序
        content_blocks = []
        # 添加文本块
        for block in page_dict["blocks"]:
            if "lines" in block:
                # 计算文本块的大致位置
                if block["lines"]:
                    first_line = block["lines"][0]
                    # last_line = block["lines"][-1]
                    y_pos = first_line["spans"][0]["origin"][1] if first_line["spans"] else 0
                else:
                    y_pos = 0
                text_content = ""
                for line in block["lines"]:
                    text_content += "".join(span["text"] for span in line["spans"]) + "\n"
                content_blocks.append({
                    'type': 'text',
                    'content': text_content,
                    'y_pos': y_pos
                })
        # 添加图片块
        for img_info in page_images_with_pos:
            content_blocks.append({
                'type': 'image',
                'content': img_info['path'],
                'y_pos': img_info['y_pos']
            })
        # 按Y坐标排序所有内容块
        content_blocks.sort(key=lambda x: x['y_pos'])
        # 按顺序输出内容
        for block in content_blocks:
            if block['type'] == 'text':
                full_text += block['content']
            elif block['type'] == 'image':
                full_text += f"![img]({block['content']})\n"
    pdf_document.close()
    return full_text.strip(), imgs

