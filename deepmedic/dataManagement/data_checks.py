from __future__ import print_function

import glob
import os
from tqdm import tqdm
import numpy as np

from nifti_image import NiftiImage, save_nifti


def print_dict(item, prefix=''):
    for elem in sorted(item.items()):
        print("{2}{0:5d}: {1}".format(elem[1], elem[0], prefix))


def get_image_dims_stats(image_list, do_pixs=True, do_dims=True, do_dtypes=True,
                         disable_tqdm=False,
                         tqdm_text='Getting Pixel Dimension Stats'):
    if not (do_dims or do_pixs):
        return {}, {}
    dims_count = {}
    pix_dims_count = {}
    for image_path in tqdm(image_list, desc=tqdm_text, disable=disable_tqdm):
        image = NiftiImage(image_path)

        if do_dims:
            dims = image.get_size()

            if dims in dims_count:
                dims_count[dims] += 1
            else:
                dims_count[dims] = 1

        if do_pixs:
            pix_dims = image.get_pixel_dims()
            if pix_dims in pix_dims_count:
                pix_dims_count[pix_dims] += 1
            else:
                pix_dims_count[pix_dims] = 1

            if not pix_dims == (1., 1., 1.):
                image.save('/vol/biomedic2/bgmarque/deepmedic/examples/test_original.nii.gz')
                image.save_thumbnail('/vol/biomedic2/bgmarque/deepmedic/examples/test_thumbnail.png')
                image.resample(size=(240, 240, 240), pixel_dims=(min(pix_dims), min(pix_dims), min(pix_dims)),  save=True,
                               filename='/vol/biomedic2/bgmarque/deepmedic/examples/test_resampled_size.nii.gz')
                image.save_thumbnail('/vol/biomedic2/bgmarque/deepmedic/examples/test_thumbnail_resampled.png')
                break

        if do_dtypes:
            print(image.get_pixel_type())
    return dims_count, pix_dims_count


def pix_check(pix_count, verbose=True):
    prefix = ' '*(len('[PASSED]') + 1)
    if len(pix_count) > 1:
        print('[FAILED] Pixel dimensions check')
        if verbose:
            print(prefix + 'Pixel dimensions do not match in between images')
            print(prefix + 'We recommend resampling every image to the same pixel dimensions for every dimension '
                  '(e.g. (1, 1, 1))')
            print(prefix + 'pixel Sizes Count:')
            print_dict(pix_count, prefix)
    else:
        pix_dims = list(pix_count.keys())[0]
        for pix_dim in pix_dims:
            if not pix_dim == pix_dims[0]:
                print('[FAILED] Pixel dimensions check')
                if verbose:
                    print(prefix + 'Pixel dimensions do not match across dimensions')
                    print(prefix + 'We recommend resampling every image to the same pixel dimensions for every dimension '
                          '(e.g. (1, 1, 1))')
                    print(prefix + 'Pixel Sizes Count:')
                    print_dict(pix_count, prefix)
                return

        print('[PASSED] Pixel dimensions check')
        if verbose:
            print(prefix + 'Pixel Dimensions: ' + str(pix_dims))


def dims_check(dims_count, verbose=True):
    prefix = ' '*(len('[PASSED]') + 1)
    if len(dims_count) > 1:
        print('[FAILED] Images dimensions check')
        if verbose:
            print(prefix + 'Pixel dimensions do not match in between images')
            print(prefix + 'We recommend resampling every image to the same pixel dimensions for every dimension '
                  '(e.g. (1, 1, 1))')
            print(prefix + 'pixel Sizes Count:')
            print_dict(dims_count, prefix)
    else:
        print('[PASSED] Images dimensions check')
        if verbose:
            print(prefix + 'Image Dimensions: ' + str(list(dims_count.keys())[0]))


def run_checks(filelist, pixs=False, dims=False, dtypes=False, disable_tqdm=False):
    print('Running Checks')
    dims_count, pix_dims_count = get_image_dims_stats(filelist, do_dims=dims, do_pixs=pixs,
                                                      disable_tqdm=disable_tqdm,
                                                      tqdm_text='Running Image and Pixel Dimension Checks')
    if dims:
        dims_check(dims_count)
    if pixs:
        pix_check(pix_dims_count)


if __name__ == "__main__":
    base_path = '/vol/vipdata/data/brain/adni/images/brain_adni2/'
    # base_path = '/vol/vipdata/data/brain/brats/2017_kostas/preprocessed_v2'
    # base_path = '/vol/biomedic2/bgmarque/deepmedic/examples/dataForExamples/brats2017_kostas2'
    # test_image = '/vol/vipdata/data/brain/brats/2017_kostas/preprocessed_v2/Brats17TrainingData/HGG/Brats17_2013_2_1/Brats17_2013_2_1_t1.nii.gz'
    # img = NiftiImage(test_image)
    # for key in img.get_header_keys():
    #     print("{0}: {1}".format(key, img.reader.GetMetaData(key)))
    filelist = glob.glob(os.path.join(base_path, '**/*.nii.gz'), recursive=True)
    # run_checks(filelist, dims=True, pixs=True, disable_tqdm=False)
    # dims_count, pixel_count = get_image_dims_stats(glob.glob(os.path.join(base_path, '**/*.nii.gz'), recursive=True), do_dims=False)
    # print('Dims Count')
    # print_dict(dims_count)
    # print('Pixel Count')
    # print_dict(pixel_count)

    # image1 = NiftiImage('/vol/biomedic2/bgmarque/data_for_bernadro/T1w_trio_P00030_10798_baseline_20150703_U-ID35697.nii.gz')
    # image2 = NiftiImage('/vol/biomedic2/bgmarque/data_for_bernadro/T2w_trio_P00030_10798_baseline_20150703_U-ID35697.nii.gz')
    #
    # image2.resample(size=image1.get_size(), pixel_dims=image1.get_pixel_dims(),
    #                 origin=image1.get_origin(), direction=image1.get_direction(), save=True,
    #                 filename='/vol/biomedic2/bgmarque/data_for_bernadro/resampled_T2w_trio_P00030_10798_baseline_20150703_U-ID35697.nii.gz')
    #
    # image2.save_thumbnail('/vol/biomedic2/bgmarque/data_for_bernadro/resampled_thumb_T2w_trio_P00030_10798_baseline_20150703_U-ID35697.png')
    # image1.save_thumbnail('/vol/biomedic2/bgmarque/data_for_bernadro/thumb_T1w_trio_P00030_10798_baseline_20150703_U-ID35697.png')
