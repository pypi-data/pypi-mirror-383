from pydantic import BaseModel, model_validator, Field, ConfigDict
from shapely import Polygon
from typing_extensions import Self


def get_rectangle_points(bottom_left, top_right):
    """
        根据交点获取逆时针坐标
    """
    x1, y1 = bottom_left
    x2, y2 = top_right
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


class RectangleHelper(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bottom_left: tuple[float, float]
    top_right: tuple[float, float]
    rectangle: Polygon = Field(default=None)

    @model_validator(mode="after")
    def init(self) -> Self:
        points = get_rectangle_points(self.bottom_left, self.top_right)
        self.rectangle = Polygon(points)

    def contains(self, bottom_left: tuple[float, float], top_right: tuple[float, float]) -> bool:
        """
            rectangle 是否包含rectangle2矩形
        """
        points = get_rectangle_points(bottom_left, top_right)
        rectangle2 = Polygon(points)
        return self.rectangle.contains(rectangle2)

    def intersection(self, bottom_left: tuple[float, float], top_right: tuple[float, float]) -> bool:
        """
            rectangle 是否与rectangle2矩形有交集
        """
        points = get_rectangle_points(bottom_left, top_right)
        rectangle2 = Polygon(points)
        if self.rectangle.intersection(rectangle2):
            return True
        else:
            return False

    def in_top(self, bottom_left: tuple[float, float], top_right: tuple[float, float]) -> bool:
        """
            PDF坐标系是反转的, center_y值越大,越在下面
            rectangle 是否在rectangle2的上面
        """
        points = get_rectangle_points(bottom_left, top_right)
        rectangle2 = Polygon(points)
        rectangle1_center = self.rectangle.centroid
        rectangle1_center_y = rectangle1_center.y
        rectangle2_center = rectangle2.centroid
        rectangle2_center_y = rectangle2_center.y
        return rectangle2_center_y > rectangle1_center_y
