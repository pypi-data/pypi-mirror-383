import fitz


def clear_page_blk(page:fitz.Page, input_rect:tuple):
    """
    清除页面中的一个文本块
    :param page: fitz.Page 对象
    :param input_rect: 需要清除的矩形去、区，格式为 (x0, y0, x1, y1)
    :return: None
    """
    # 创建一个白色矩形覆盖文本块
    rect = fitz.Rect(input_rect)
    # page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

    page.add_redact_annot(rect, fill=(1, 1, 1))  # 添加遮盖注释
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,  # 不删除图像
        graphics=fitz.PDF_REDACT_LINE_ART_NONE  # 不删除线条艺术
    )  # 应用遮盖注释
    # 保存更改
    # page.saveIncr()  # 如果需要保存增量更改，可以使用这个方法

