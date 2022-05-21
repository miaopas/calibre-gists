from email.mime import image
from time import time
from calibre.customize.conversion import OutputFormatPlugin
from calibre.ptempfile import TemporaryDirectory
from calibre.customize.conversion import OutputFormatPlugin, OptionRecommendation
from calibre import CurrentDir
from pathlib import Path
from polyglot.urllib import unquote
from os.path import dirname, abspath, relpath as _relpath, exists, basename
import os
from calibre.utils import zipfile
import xml.etree.ElementTree as ET
from PIL import Image


class CBZOutput(OutputFormatPlugin):
    name = "CBZ Output"
    author = "JHT"
    version = (1, 0, 0)
    file_type = "cbz"
    commit_name = "cbz_output"


    options = {
        OptionRecommendation(name='no_crop',
            recommended_value=True, level=OptionRecommendation.MED,
            help=' 不裁切'
        ),
        OptionRecommendation(name='starting_page',
            recommended_value=0, level=OptionRecommendation.LOW,
            help='从这一页开始裁切'
        ),
        OptionRecommendation(name='starting_page_left_crop',
            recommended_value=0, level=OptionRecommendation.LOW,
            help='起始页左侧剪裁'),
        OptionRecommendation(name='starting_page_right_crop',
        recommended_value=0, level=OptionRecommendation.LOW,
        help='起始页右侧剪裁'),
        OptionRecommendation(name='starting_page_up_crop',
            recommended_value=0, level=OptionRecommendation.LOW,
            help='起始页上剪裁'),
        OptionRecommendation(name='starting_page_down_crop',
        recommended_value=0, level=OptionRecommendation.LOW,
        help='起始页下剪裁'),

        OptionRecommendation(name='next_page_left_crop',
        recommended_value=0, level=OptionRecommendation.LOW,
        help='下一页左侧剪裁'),
        OptionRecommendation(name='next_page_right_crop',
        recommended_value=0, level=OptionRecommendation.LOW,
        help='下一页右侧剪裁'),
        OptionRecommendation(name='next_page_up_crop',
        recommended_value=0, level=OptionRecommendation.LOW,
        help='下一页上剪裁'),
        OptionRecommendation(name='next_page_down_crop',
        recommended_value=0, level=OptionRecommendation.LOW,
        help='下一页下剪裁')
    }

    # recommendations = {
    #     ('no_crop', True, OptionRecommendation.HIGH),
    #     ('starting_page',  0, OptionRecommendation.HIGH),
    #     ('starting_page_left_crop', 0, OptionRecommendation.HIGH),
    #     ('starting_page_right_crop', 0, OptionRecommendation.HIGH),
    #     ('next_page_left_crop', 0, OptionRecommendation.HIGH),
    #     ('next_page_right_crop',  0, OptionRecommendation.HIGH),
    #     }

    def convert(self, oeb_book, output_path, input_plugin, opts, log):
        with TemporaryDirectory('_epub_output') as tdir:
            print(f'Working in {tdir}')
            with CurrentDir(tdir):
                # unload all book data from manifest
                for item in oeb_book.manifest:
                    path = unquote(item.href)
                    dir = dirname(path)
                    # log.info(path, dir)
                    if not exists(dir) and dir != '':
                        os.makedirs(dir)
                    with open(path, 'wb') as f:
                        f.write(item.bytes_representation)
                    item.unload_data_from_memory(memory=path)
                
                # import time
                # time.sleep(2000)

                img_path = Path('output_images')
                img_path.mkdir()
                id = 0
                filters = ['jpeg', 'jpg', 'gif', 'png']
                for item in oeb_book.spine:
                    path =  unquote(item.href)
                    log.info(path)
                    import re
                    with open(path, 'r') as f:
                        contents = f.read()
                    res = []
                    matches = re.findall('"(.*?)"', contents)
                    for match in matches:
                        for ext in filters:
                            if ext in match:
                                res.append(match)
                    if len(res) != 1:
                        raise Exception('Found more than 1 image in one html page!')
                    
                    image = Path(res[0])
                    if image.parts[0] in ['..', '.']:
                        image = Path(*image.parts[1:])
                    ext = image.suffix
                    image.rename(img_path / Path(f'{id:03d}{ext}'))
                    id = id + 1

                def get_files(path, extensions):
                    all_files = []
                    for ext in extensions:
                        all_files.extend(Path(path).glob(ext))
                    return all_files

                
                # crop the images
                
                if not opts.no_crop:
                    log.info('-------------------------Begin to crop imagaes-----------')
                    i = 0
                    # left, right, up, down
                    crop_even = (opts.starting_page_left_crop,opts.starting_page_right_crop,opts.starting_page_up_crop,opts.starting_page_down_crop)
                    crop_odd = (opts.next_page_left_crop,opts.next_page_right_crop,opts.next_page_up_crop,opts.next_page_down_crop)
                    images = get_files(img_path,('*.png', '*.jpeg', '*.jpg', '*.gif'))
                    for path in sorted(list(images))[opts.starting_page:]:
                        log.info(path)

                        image = Image.open(path)
                        size = image.size
                        if i % 2 == 0:
                            crop = (crop_even[0], crop_even[2], size[0]-crop_even[1], size[1]-crop_even[3])
                        else:
                            crop = (crop_odd[0], crop_odd[2], size[0]-crop_odd[1], size[1]-crop_odd[3])
                        cropped_image = image.crop(crop)
                        cropped_image.save(path)
                        i = i + 1
                        

                zfile = zipfile.ZipFile(output_path, "w")
                zfile.add_dir(img_path)
                

                
    def gui_configuration_widget(self, parent, get_option_by_name, get_option_help, db, book_id=None):
        
        from calibre_plugins.cbz_output.ui import PluginWidget
        return PluginWidget(parent, get_option_by_name, get_option_help, db, book_id)