import fitz
import numpy as np

from collections import Counter


class PDF:
    def __init__(self):
        pass

    @staticmethod  # 静态方法，不需要实例化类即可调用。通过类名.方法名() 直接调用。
    def clear_page_blk(page: fitz.Page, input_rect: tuple):
        """
        清除页面中的一个文本块
        :param page: fitz.Page 对象
        :param input_rect: 需要清除的矩形去、区，格式为 (x0, y0, x1, y1)
        :return: None
        """
        # 创建一个白色矩形覆盖文本块
        rect = fitz.Rect(input_rect)
        # page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1)) # 直接绘制白色矩形覆盖

        page.add_redact_annot(rect, fill=(1, 1, 1))  # 添加遮盖注释
        page.apply_redactions(
            images=fitz.PDF_REDACT_IMAGE_NONE,  # 不删除图像
            graphics=fitz.PDF_REDACT_LINE_ART_NONE  # 不删除线条艺术
        )  # 应用遮盖注释
        # 保存更改
        # page.saveIncr()  # 如果需要保存增量更改，可以使用这个方法

    @staticmethod
    def is_table(page: fitz.Page) -> bool:
        """
        判断页面是否包含表格
        :param page:
        :return: True or False
        """
        blocks = page.get_text("blocks")
        x_pos = [round(b[0], 1) for b in blocks]
        freq = Counter(x_pos)

        num_beyond_threshold = (np.array(list(freq.values())) >= 6).sum().item()
        if num_beyond_threshold > 2:
            return True
        return False
