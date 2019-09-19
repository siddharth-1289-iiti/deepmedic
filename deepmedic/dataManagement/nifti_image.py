from __future__ import print_function

import numpy as np
from PIL import Image
import SimpleITK as sitk


def get_nifti_reader(filename):
    reader = sitk.ImageFileReader()

    reader.SetFileName(filename)
    reader.LoadPrivateTagsOn()

    reader.ReadImageInformation()

    return reader


def save_nifti(image, filename):
    writer = sitk.ImageFileWriter()
    writer.SetFileName(filename)
    writer.Execute(image)


def get_new_size(size, new_pix_dims, old_pix_dims):
    return tuple([int(x) for x in np.array(size) * (np.array(old_pix_dims) / np.array(new_pix_dims))])


def get_new_origin(origin, new_pix_dims, old_pix_dims):
    return tuple([x for x in np.array(origin) * (np.array(old_pix_dims) / np.array(new_pix_dims))])


class NiftiImage(object):

    def __init__(self, filename):
        self.image_reader = get_nifti_reader(filename)
        self.image = None
        self.reader = self.image_reader

    def update_reader(self, filename):
        self.reader = get_nifti_reader(filename)

    def open(self):
        if self.image is None:
            self.image = self.reader.Execute()
            self.reader = self.image
        return self.image

    def get_num_dims(self):
        return self.reader.GetDimension()

    def get_size(self):
        return self.reader.GetSize()

    def get_pixel_dims(self):
        return self.reader.GetSpacing()

    def get_origin(self):
        return self.reader.GetOrigin()

    def get_direction(self):
        return self.reader.GetDirection()

    def get_pixel_type(self):
        return self.reader.GetPixelIDValue()

    def get_pixel_type_string(self):
        return self.reader.GetPixelID()

    def get_resample_parameters(self):
        return self.get_size(), self.get_pixel_dims(), self.get_direction(), self.get_origin()

    def get_header_keys(self):
        return self.reader.GetMetaDataKeys()

    def apply_resample(self, origin, pixel_dims, direction, size, interpolator=sitk.sitkLinear):

        resample = sitk.ResampleImageFilter()
        resample.SetInterpolator(interpolator)
        resample.SetOutputDirection(direction)
        resample.SetOutputOrigin(origin)
        resample.SetOutputSpacing(pixel_dims)
        resample.SetSize(size)

        return resample.Execute(self.open())

    def resample(self, origin=None, pixel_dims=None, direction=None, size=None, standard=False,
                 save=False, filename=None, copy=False, ref_image=None):
        # get transformation parameters
        if ref_image:
            size, pixel_dims, direction, origin = ref_image.get_resample_parameters()
        else:
            if pixel_dims is None:
                if standard:
                    pixel_dims = (1., 1., 1.)
                else:
                    pixel_dims = self.get_pixel_dims()
            if size is None:
                size = get_new_size(self.get_size(), pixel_dims, self.get_pixel_dims())
            num_dims = len(size)
            if origin is None:
                if standard:
                    origin = np.zeros(num_dims)
                else:
                    origin = get_new_origin(self.get_origin(), pixel_dims, self.get_pixel_dims())
            if direction is None:
                if standard:
                    direction = np.identity(num_dims).flatten()
                else:
                    direction = self.get_direction()

        # apply transformation
        resampled = self.apply_resample(origin, pixel_dims, direction, size)

        # save/update
        if save:
            save_nifti(resampled, filename)
        if not copy:
            self.update_reader(filename)
            self.image = resampled

        return resampled

    def save_thumbnail(self, filename, thumbnail_size=(128, 128), max_slice=False):
        size = self.get_size()
        image = sitk.GetArrayFromImage(self.open())
        if max_slice:
            image_bool = image > 0
            max_val = 0
            max_i = None
            for i in range(size[0]):
                sum_ = np.sum(image_bool[:, :, i])
                if sum_ > max_val:
                    max_val = sum_
                    max_i = i
        else:
            max_i = int(size[0]/2)
        img_slice = np.flip(image[:, :, max_i], (0, 1))
        img_slice = (img_slice - np.min(img_slice)) * 255.0 / (np.max(img_slice) - np.min(img_slice))
        im = Image.fromarray(img_slice)
        im = im.convert('L')
        im.thumbnail(thumbnail_size)
        im.save(filename)

    def save(self, filename):
        save_nifti(self.open(), filename)
