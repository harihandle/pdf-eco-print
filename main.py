import os
from math import ceil

from PIL import Image
from pdf2image import pdf2image


def create_images_from_pdf(file_path, blank_pages_in_front=0, blank_pages_in_back=0):
    """
    Each page in the PDF is converted into a PIL Image and blank pages are added in front and back based on the params.
    Extra blank pages will be auto added towards the end such that the total images will always be divisible by 4.
    :param file_path:
    :param blank_pages_in_front:
    :param blank_pages_in_back:
    :return: list of PIL Image.
    """
    pdf_images = pdf2image.convert_from_path(file_path, output_folder='images')
    white_image = Image.new('RGB', (pdf_images[0].size[0], pdf_images[0].size[1]), (250, 250, 250))
    images = list()
    if blank_pages_in_front:
        images.extend([white_image for _ in range(blank_pages_in_front)])

    images.extend(pdf_images)

    if blank_pages_in_back:
        images.extend([white_image for _ in range(blank_pages_in_back)])

    extra_blanks = (4 - (len(images) % 4)) % 4
    if extra_blanks:
        images.extend([white_image for _ in range(extra_blanks)])

    return images


def create_page_bundles_arrangement(total_pages, bundle_length=20):
    """
    Creates a 0-index based page bundles arrangement.
    :param total_pages:
    :param bundle_length: In the final output pdf, how many pages should be in one bundle for any future binding.
    :return: [page_bundle[fronts[[a, b], ...], backs[[c,d], ...]], ...]
    """
    page_arrangement = list()
    current_index = 0
    while current_index < total_pages:
        total_images_to_bundle = min(total_pages - current_index, (bundle_length * 2))
        fronts, backs = create_page_bundle_arrangement(total_images_to_bundle)
        page_arrangement.append([fronts, backs])
        current_index += total_images_to_bundle
    return page_arrangement


def create_page_bundle_arrangement(page_length):
    """
    Creates a Page Bundle Arrangement.
    :param page_length:
    :return:
    """
    '''
        Total pages = 16
        Front   Back
        16 1     2 15
        14 3     4 13
        12 5     6 11
        10 7     8 9
    '''
    total_papers = ceil(page_length / 4)
    fronts = [[None, None] for _ in range(total_papers)]
    backs = [[None, None] for _ in range(total_papers)]

    image_index = 0
    front_index = 1
    back_index = 0
    for index in range(total_papers):
        fronts[index][front_index] = image_index
        image_index += 1
        backs[index][back_index] = image_index
        image_index += 1

    front_index = 0
    back_index = 1
    for index in range(total_papers - 1, -1, -1):
        backs[index][back_index] = image_index
        image_index += 1
        if image_index >= page_length:
            break
        fronts[index][front_index] = image_index
        image_index += 1
        if image_index >= page_length:
            break

    return fronts, backs


def merge_images(image1, image2):
    """
    Merge image1 with image2.
    Output: \n
    image2 (left rotate 90 deg) \n
    image1 (left rotate 90 deg)
    :param image1: PIL Image
    :param image2: PIL Image
    :return: PIL Image
    """
    image1 = image1.rotate(90, expand=True)
    image2 = image2.rotate(90, expand=True)

    new_image = Image.new('RGB', (image1.size[0], 2 * image1.size[1]), (250, 250, 250))
    new_image.paste(image1, (0, image1.size[1]))
    new_image.paste(image2, (0, 0))
    return new_image


def create_page_image_bundles_arrangement(images, page_bundles):
    """
    Create a Page Image Bundles arrangement from Page Bundles arrangement. This will take care of merging images.
    :param images:
    :param page_bundles:
    :return: [page_image_bundle[fronts[img1, img2, ...], backs[img3, img4, ...]], ...]
    """
    page_image_bundles = list()
    for page_bundle in page_bundles:
        front_images = list()
        back_images = list()

        # page_bundle will always be of length 2. [fronts, backs].
        fronts = page_bundle[0]
        backs = page_bundle[1]

        for index in range(len(fronts)):
            front_page_indices = fronts[index]
            back_page_indices = backs[index]

            front_page_left_index = front_page_indices[0]
            front_page_right_index = front_page_indices[1]
            front_image_left = images[front_page_left_index]
            front_image_right = images[front_page_right_index]
            front_images.append(merge_images(front_image_left, front_image_right))

            back_page_left_index = back_page_indices[0]
            back_page_right_index = back_page_indices[1]
            back_image_left = images[back_page_left_index]
            back_image_right = images[back_page_right_index]
            back_images.append(merge_images(back_image_left, back_image_right))

        page_image_bundles.append([front_images, back_images])
    return page_image_bundles


def create_pdfs(page_image_bundles):
    """
    Creates multiple PDFs. For each page_image_bundle, there will be 2 PDFs, 1 - Front Papers, 2 - Back Papers.
    :param page_image_bundles:
    :return:
    """
    bundle_index = 1
    for page_image_bundle in page_image_bundles:
        side = None
        for page_images in page_image_bundle:
            side = 'front' if not side else 'back'
            if side == 'back':
                page_images.reverse()
            page_images[0].save(
                f'images/merged-{bundle_index}-{side}.pdf',
                "PDF", resolution=100.0, save_all=True, append_images=page_images[1:]
            )
        bundle_index += 1


def cleanup():
    os.system('rm -rf images && mkdir images')


INSTRUCTIONS = '''
Save Paper by printing efficiently.

RESULT:
- Creates a bundled book.
- 2 pages are made to fit in a single side of an A4 sheet.
- A single A4 paper will have 4 pages of the PDF printed. 2 in front and 2 in back.
- Finally, the printed papers can be folded at the center and it will become a booklet.

USAGE:
- Printer Used: Brother DCP-T426W
- The printer prints the pages in reverse order so that all the pages after the print will be in the expected order.
    - Eg., If there are 2 pages to be printed, the printer prints the second page first and then the first page.
      The final ordering will be the first page and then the second page because the first page was printed last by
      the printer.
- In order to get the pages in the expected order towards the end. Do the following,
    1. Print merged-x-back.pdf first. Ordering is already reversed in the PDF.
    2. Take all the printed papers and put them exactly in the tray as they are. No need to turn, shuffle or reverse.
    3. Print merged-x-front.pdf.
'''


if __name__ == '__main__':
    print(INSTRUCTIONS)
    cleanup()
    images = create_images_from_pdf('sample.pdf')
    page_bundles = create_page_bundles_arrangement(len(images))
    print(page_bundles)
    page_image_bundles = create_page_image_bundles_arrangement(images, page_bundles)
    create_pdfs(page_image_bundles)
