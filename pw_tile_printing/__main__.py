import argparse
import sys

OPEN_UI = not bool(sys.argv[1:])

if __name__ == '__main__':
    if OPEN_UI:
        from pw_tile_printing import main
        main.show()
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('-im', '--image')
        parser.add_argument('-wd', '--image_width')
        parser.add_argument('-hg', '--image_height')
        parser.add_argument('-ka', '--keep_aspect_ratio')
        parser.add_argument('-pg', '--pages', nargs='+', required=False)
        parser.add_argument('-op', '--output_path')
        parser.add_argument('-pr', '--print')
        parser.add_argument('-pn', '--printer_name')
        parser.add_argument('-pd', '--page_padding')
        parser.add_argument('-ox', '--offset_x')
        parser.add_argument('-oy', '--offset_y')


