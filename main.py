from PIL import Image, ImageDraw

# import Image, ImageDraw

# ========== настройки ========== #
# режим вывода:
# 0 - на выходе исходная картинка с отмеченными амогусами
# 1 - на выходе картинка с прозрачным фоном и отметками в местах,
#     где на оригинальной картинке были амогусы
#     (чтобы потом самому наложить в редакторе на оригинал)
mode = 0

# каждые сколько процентов выводится информация:
dp = 5

# полный или относительный путь до исследуемого файла:
name = 'place_x1.png'

# ширина рамки вокруг найденных амогусов в пикселях:
border_width = 1

# добавить свои шаблоны для поиска:
# пробел - вообще любой цвет
# точка  - цвет, отличающийся от пронумерованных
# цифра  - пронумерованный цвет, разные цифры - разные цвета, одинаковые цифры - одинаковые цвета
patterns = [
    [
        ' ...  ',
        '.000. ',
        '...00.',
        '.0000.',
        '.0.0. ',
        ' . .  ',
    ],
    [
        ' ...  ',
        '.000. ',
        '...00.',
        '.0000.',
        '.000. ',
        '.0.0. ',
        ' . .  ',
    ],
]
# =============================== #
# автогенерация шаблонов, отраженных по горизонтали:
count = 0
for i in range(len(patterns)):
    patt = patterns[count]
    patterns.insert(count + 1, [])
    for line in patt:
        patterns[count + 1].append(''.join(reversed(line)))
    count += 2

img = Image.open(name)
if mode == 0:
    out = img.copy()
elif mode == 1:
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
else:
    raise Exception('выбран неправильный режим')

pixels = img.load()
WIDTH, HEIGHT = img.size
draw = ImageDraw.Draw(out)


def check_pattern(x0, y0, pattern):
    pattern_w = len(pattern[0])
    pattern_h = len(pattern)
    if (x0 + pattern_w > WIDTH) or (y0 + pattern_h > HEIGHT):
        return False

    # нахождение цветов, соответствующих символам на макете
    colors = {}
    for y1 in range(pattern_h):
        for x1 in range(pattern_w):
            letter = pattern[y1][x1]
            if letter == ' ':
                continue
            checked_color = pixels[x0 + x1, y0 + y1]
            if letter == '.':
                for c in colors.values():
                    if checked_color == c:
                        return False
                continue
            if letter not in colors.keys():
                colors[letter] = checked_color
                continue
            if checked_color != colors[letter]:
                return False

    # проверяем совпадение цветов, соответствующих одинаковым символам в макете
    for k1 in colors.keys():
        for k2 in colors.keys():
            if k1 != k2 and colors[k1] == colors[k2]:
                return False
    return True


def draw_rect(x0, y0, x1, y1, color, width):
    draw.rectangle((x0 - width, y0 - width, x1 + width - 1, y1 + width - 1), fill=None, outline=color, width=width)


number_of_amogus = 0
count = 0
N = HEIGHT * WIDTH
progress = 0
# итерация по стартовым точкам
for y0 in range(HEIGHT):
    for x0 in range(WIDTH):
        for patt in patterns:
            if check_pattern(x0, y0, patt):
                number_of_amogus += 1
                draw_rect(x0, y0, x0 + len(patt[0]), y0 + len(patt), (0, 255, 0), border_width)
                break
        count += 1
        if count / N - progress > dp / 100:
            progress = count / N
            print(f'processing... {progress * 100:.0f}%\t number of amogus - {number_of_amogus}')
print('complete!')
print(f'total number of amogus - {number_of_amogus}')

out.save('out.png', "PNG")
out.show()
