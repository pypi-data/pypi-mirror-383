from pydantic import BaseModel, Field
from typing import List, Any, Tuple, Optional


class Line(BaseModel):
    """单个文本行的 OCR 识别结果"""

    poly: List[Tuple[int | float, int | float]] = Field(
        list,
        min_items=4,
        max_items=4,
        description="区域的四边形边界坐标，包含4个(x,y)顶点",
    )
    text: Optional[str] = None # 识别的文本内容
    type: Optional[str] = None # 识别类型（如 img_ocr）
    score: float | List[Any] = Field(None, description="识别置信度相关数据;新版是float,旧版是list")


class ImageOcrVo(BaseModel):
    """OCR 模型的整体识别结果"""

    version: str = ""  # 模型版本号
    width: int | float = 0  # 图片宽度
    height: int | float = 0  # 图片高度
    angle: int | float = 0  # 图片旋转角度
    lines: List[Line] = []  # 所有识别到的文本行列表