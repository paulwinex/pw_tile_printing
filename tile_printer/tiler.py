from pathlib import Path
from PIL import Image,  ImageDraw
from functools import cached_property
from dataclasses import dataclass
from pprint import pprint


PAPER_A3 = (297, 420)
PAPER_A4 = (210, 297)
PAPER_A5 = (148, 210)
PAPER_A6 = (105, 148)
ORIENT_PORTRAIT = 1
ORIENT_LANDSCAPE = 2


class Tiler:
    def __init__(self, src_image: Path, dpi: int = None):
        self.path = Path(src_image)
        self.image: Image.Image = Image.open(self.path.as_posix())
        self.dpi = dpi or 96
        self.image.info['dpi'] = self.dpi

    @cached_property
    def image_size_mm(self):
        return (
            px_to_mm(self.image.width, self.dpi),
            px_to_mm(self.image.height, self.dpi))

    @cached_property
    def image_size_mm_x(self):
        return self.image_size_mm[0]

    @cached_property
    def image_size_mm_y(self):
        return self.image_size_mm[1]

    def make_tiles(self,
                   image_size: tuple,
                   padding: tuple = (0, 0, 0, 0),
                   keep_aspect_ratio: bool = True,
                   border_cut_line: bool = True,
                   border_cut_line_height: int = 10,
                   dpi: int = 300,
                   page_size: tuple = PAPER_A4,
                   page_orient: int = ORIENT_PORTRAIT,
                   save_path: Path = None,
                   offset: tuple = (0, 0),
                   ) -> dict:
        """
        Split and resize image to tiles

        :param image_size: output image size (mm)
        :param padding: print padding, depended on printer model (mm): left, top, right, bottom
        :param keep_aspect_ratio: keep aspect ratio on image resize
        :param border_cut_line: add border cut line on image
        :param border_cut_line_height:  (mm)
        :param dpi: printing dpi
        :param page_size: page size (mm). Default A4
        :param page_orient: page orientation
        :param save_path: save result to files and return path list if not None, else return PIL.Image objects
        :param offset: global offset on page (mm)
        :return: dict
        """
        page_size = self.orient_page(page_size, orient=page_orient)
        scale_factor_x = image_size[0]/self.image_size_mm_x
        scale_factor_y = image_size[1]/self.image_size_mm_y
        if keep_aspect_ratio:
            scale_factor_x = scale_factor_y = min((scale_factor_x, scale_factor_y))
        # get image size in mm
        full_img_w, full_img_h = (self.image_size_mm_x*scale_factor_x,
                                  self.image_size_mm_y*scale_factor_y)
        # get page size in mm without padding
        full_page_w, full_page_h = (page_size[0]-padding[0]-padding[2],
                                    page_size[1]-padding[1]-padding[3])
        image_rect = Rect(0, 0, full_img_w, full_img_h)
        page_rect = Rect(0, 0, full_page_w, full_page_h)
        tiles = image_rect.tile_rects_in_area(page_rect, offset=offset, crop=True)
        pprint(tiles)
        # resize image to full size in mm using dpi
        resized = self.image.resize((mm_to_px(full_img_w, dpi), mm_to_px(full_img_h, dpi)))
        # get save path
        if save_path:
            filename = fix_format(Path(Path(save_path).name or f'page_####.png').with_suffix('.png').name)
            save_path = Path(save_path).parent
        else:
            filename = None
        save_path.mkdir(exist_ok=True, parents=True)

        pages = []
        for page_num, tile in enumerate(tiles['rects']):
            rect = tile['rect']
            page_pos = tile['page_pos']
            cropped_img = resized.crop((mm_to_px(rect.x, dpi),
                                       mm_to_px(rect.y, dpi),
                                       mm_to_px(rect.x2, dpi),
                                       mm_to_px(rect.y2, dpi)))
            new_image = Image.new('RGB', (mm_to_px(page_size[0], dpi),
                                          mm_to_px(page_size[1], dpi)),
                                  color=(255, 255, 255))
            new_image.paste(cropped_img, (mm_to_px(padding[0]+page_pos[0], dpi),
                                          mm_to_px(padding[1]+page_pos[1], dpi)))
            if border_cut_line:
                self.add_border_cut_lines(
                    new_image, mm_to_px(border_cut_line_height, dpi),
                    tuple(map(lambda x: mm_to_px(x, dpi), padding)))
            if save_path:
                img_save_path = save_path / filename.format(page_num)
                new_image.save(img_save_path.as_posix(), 'PNG')
                new_image = img_save_path.as_posix()
            pages.append(dict(
                image=new_image,
                page=page_num,
                size=rect.size,
                coords_pixels=rect.as_pixels(),
                coords_mm=(rect.x, rect.y, rect.w, rect.h),
            ))

        return dict(
            rows=tiles['rows'],
            columns=tiles['columns'],
            pages=pages
        )

    @staticmethod
    def orient_page(page_size, orient):
        page_orient = ORIENT_PORTRAIT if page_size[0] < page_size[1] else ORIENT_LANDSCAPE
        if orient == page_orient:
            return page_size
        else:
            return tuple(reversed(page_size))

    def add_border_cut_lines(self, img, height, padding, width=0.5):
        color = (0, 0, 0)
        width = mm_to_px(width, self.dpi)
        draw = ImageDraw.Draw(img)
        p1 = (padding[0], padding[1])
        p2 = (img.width - padding[2], padding[1])
        p3 = (img.width - padding[2], img.height - padding[3])
        p4 = (padding[0], img.height - padding[3])

        if height:
            draw.line((p1, (p1[0]+height, p1[1])), fill=color, width=width)
            draw.line((p1, (p1[0], p1[1]+height)), fill=color, width=width)
            draw.line((p2, (p2[0]-height, p2[1])), fill=color, width=width)
            draw.line((p2, (p2[0], p2[1]+height)), fill=color, width=width)
            draw.line((p3, (p3[0]-height, p3[1])), fill=color, width=width)
            draw.line((p3, (p3[0], p3[1]-height)), fill=color, width=width)
            draw.line((p4, (p4[0]+height, p4[1])), fill=color, width=width)
            draw.line((p4, (p4[0], p4[1]-height)), fill=color, width=width)
        else:
            draw.line((p1, p2), fill=color, width=width)
            draw.line((p2, p3), fill=color, width=width)
            draw.line((p3, p4), fill=color, width=width)
            draw.line((p4, p1), fill=color, width=width)
        del draw


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    def __repr__(self):
        return f'<Rect x={self.x} y={self.y} w={self.w} h={self.h}>'

    def __str__(self):
        return f'x={self.x} y={self.y} w={self.w} h={self.h}'

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    @property
    def size(self):
        return self.w, self.h

    def is_intersected(self, other_rect):
        """Check if two rectangles are intersected"""
        if self.x < other_rect.x + other_rect.w and self.x + self.w > other_rect.x and\
                self.y < other_rect.y + other_rect.h and self.y + self.h > other_rect.y:
            return True
        else:
            return False

    def as_pixels(self, dpi: int = 300):
        return (
            mm_to_px(self.x, dpi),
            mm_to_px(self.y, dpi),
            mm_to_px(self.w, dpi),
            mm_to_px(self.h, dpi),
        )

    def crop(self, bounding_box: 'Rect'):
        x = max(self.x, bounding_box.x)
        y = max(self.y, bounding_box.y)
        w = min(self.x + self.w, bounding_box.x + bounding_box.w) - x
        h = min(self.y + self.h, bounding_box.y + bounding_box.h) - y
        return Rect(x, y, w, h)

    def tile_rects_in_area(self, rect: 'Rect', offset: tuple = (0, 0), crop: bool = True):
        """
        Function make grid on rectangles rect in other big area
        :param crop:
        :param rect: tuple(float, float)
        :param offset: tuple(float, float)
        :return: list(Rect,)
        """
        rects = []
        columns = rows = 0
        for y_step in range(int(self.h // rect.h) + 2):
            for x_step in range(int(self.w//rect.w)+2):
                next_rect = Rect((rect.w*x_step)-offset[0], (rect.h*y_step)-offset[1], rect.w, rect.h)
                if self.is_intersected(next_rect):
                    rows = max(y_step + 1, rows)
                    columns = max(x_step + 1, columns)
                    rects.append(dict(
                        rect=next_rect if not crop else next_rect.crop(self),
                        page_pos=(
                            offset[0] if (y_step == 0 and x_step == 0) else 0,
                            offset[1] if y_step == 0 else 0
                        )
                    )
                    )
        return {
            'rects': rects,
            'columns': columns,
            'rows': rows
        }


def px_to_mm(pixels: int, dpi: int):
    return pixels * 25.4 / dpi


def mm_to_px(mm, dpi):
    return int(mm * dpi / 25.4)


def fix_format(filename: str) -> str:
    """
    replace hashe symbols to python format with zero padding
    :param filename:
    :return:
    """
    import re
    if re.search(r'#+', filename):
        return re.sub('#+', '{:0>%dd}' % filename.count('#'), filename)
    else:
        return f"{Path(filename).stem}_{{:04d}}{Path(filename).suffix}"
