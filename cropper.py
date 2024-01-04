import os.path
import numpy as np
from PIL import Image, ImageDraw
import time


class ImgCutter:
    def __init__(self, image_path):
        self.image = self.__get_image_as_array(image_path)
        self.images = []
        self.points = set()
        self.visited = set()

    @staticmethod
    def __get_image_as_array(path):
        try:
            image = Image.open(path).convert('RGBA')
            image_array = np.asarray(image)
            return image_array
        except Exception as err:
            print(err)

    @property
    def y_len(self):
        return self.image.shape[0]

    @property
    def x_len(self):
        return self.image.shape[1]

    def rec_find_image(self, x, y, image):
        image.add((x, y))
        self.points.add((x, y))

        nb = self.__get_nb(x, y)

        while nb:
            nb_cur = []
            for n in nb:
                image.add((n[0], n[1]))
                new_nbs = self.__get_nb(n[0], n[1])
                if new_nbs:
                    nb_cur.extend(new_nbs)
            nb = nb_cur

    def find_images(self):
        for y in range(self.y_len):
            for x in range(self.x_len):
                if self.image[y][x][3] and (x, y) not in self.points:
                    # проверяем заполнена ли клетка и есть ли клетка в уже пройденных изображениях
                    self.images.append(set())
                    image = self.images[-1]
                    self.rec_find_image(x, y, image)

    def __get_nb(self, x, y):
        nb = []
        for y_cur in [y - 1, y, y + 1]:
            if y_cur >= self.y_len or y_cur < 0:
                continue
            for x_cur in [x - 1, x, x + 1]:
                if self.x_len > x_cur >= 0 \
                        and self.image[y_cur][x_cur][3] \
                        and not (x == x_cur and y == y_cur) \
                        and not (x_cur, y_cur) in self.points:
                    nb.append((x_cur, y_cur))
                    self.points.add((x_cur, y_cur))
        return nb

    def __str__(self):
        return str(self.images)


# utils
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} took {execution_time:.5f} seconds to execute.")
        return result

    return wrapper


def check_folder(filename: str) -> str:
    if os.path.exists(f'{filename}_imgs'):
        return f'{filename}_imgs'
    os.makedirs(f'{filename}_imgs', exist_ok=True)
    return f'{filename}_imgs'


def cut_image(image, img_dir):
    img_cutted = ImgCutter(image)
    img_cutted.find_images()

    w, h = img_cutted.x_len, img_cutted.y_len

    for i, img_arr in enumerate(img_cutted.images):
        if len(img_arr) < 50:
            continue
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for x, y in img_arr:
            draw.point((x, y), fill=tuple(img_cutted.image[y][x]))
        print(i)
        bbox = img.getbbox()
        trimmed_image = img.crop(bbox)
        trimmed_image.save(f'{img_dir}/img_{i}.png')


@timing_decorator
def main():
    print('[START]')
    filename = input("Введите название файла:\n")
    img_dir = check_folder(filename)
    cut_image(f'{filename}.png', img_dir)
    print('[DONE]')


if __name__ == '__main__':
    main()