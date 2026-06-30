import math
import bdffont
import os


def write_bmcf(path: str, res_index: int, dim_x: int, dim_y: int, bitmap: list[list[int]]):
    signature = 0x424d43
    header = (signature << (2 + 7 + 7)) | (res_index << (7 + 7)) | (dim_x << 7) | dim_y
    binary_bitmap = 0
    for row in bitmap:
        for bit in row:
            binary_bitmap = (binary_bitmap << 1) | bit
    binary_bitmap_length = math.ceil(dim_x * dim_y / 8)

    header_bytes = header.to_bytes(5, byteorder='big')
    binary_bitmap_bytes = binary_bitmap.to_bytes(length=binary_bitmap_length, byteorder='big')
    file = header_bytes + binary_bitmap_bytes
    with open(path, 'wb') as f:
        f.write(file)


def read_bmcf(path: str):
    with open(path, 'rb') as f:
        data = f.read()

    if len(data) < 5:
        raise ValueError('Файл слишком мал: отсутствует заголовок (5 байт)')

    header = int.from_bytes(data[:5], byteorder='big')

    dim_y = header & 0x7F                    # 7 бит
    dim_x = (header >> 7) & 0x7F             # 7 бит
    res_index = (header >> 14) & 0x3         # 2 бита
    signature = (header >> 16) & 0xFFFFFF    # 24 бита

    if signature != 0x424d43:
        raise ValueError('Неверная сигнатура BMCF')

    total_bits = dim_x * dim_y
    expected_bytes = (total_bits + 7) // 8

    bitmap_bytes = data[5:5 + expected_bytes]
    if len(bitmap_bytes) < expected_bytes:
        raise ValueError('Недостаточно данных для битовой карты')

    bitmap_int = int.from_bytes(bitmap_bytes, byteorder='big')
    bit_string = bin(bitmap_int)[2:].zfill(total_bits)

    bitmap = []
    for i in range(dim_y):
        row = [int(bit) for bit in bit_string[i * dim_x:(i + 1) * dim_x]]
        bitmap.append(row)

    return res_index, dim_x, dim_y, bitmap


def change_currency_character(bdf_path, bmcf_path):
    resolution_index, dimension_x, dimension_y, bitmap = read_bmcf(bmcf_path)
    res_to_offset = {
        1: 2,
        2: 2,
        3: 4
    }
    res_to_folder = {
        1: '720p',
        2: '1080p',
        3: '1440p'
    }

    font = bdffont.BdfFont.load(bdf_path)
    for glyph in font.glyphs:
        if glyph.encoding == 164:
            glyph.bitmap = bitmap
            glyph.dimensions = (dimension_x, dimension_y)
            glyph.device_width_x = dimension_x + res_to_offset[resolution_index]
    os.makedirs(f'resources/temp/fonts/{res_to_folder[resolution_index]}', exist_ok=True)
    font.save(f'resources/temp/fonts/{res_to_folder[resolution_index]}/BulBulPoly.bdf')


if __name__ == '__main__':
    write_bmcf('test.bmcf', 1, 7, 12,
                [[0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                 [0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                 [0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                 [0, 1, 1, 1, 0, 1, 1, 0, 0, 0]])

    print(read_bmcf('test.bmcf'))
