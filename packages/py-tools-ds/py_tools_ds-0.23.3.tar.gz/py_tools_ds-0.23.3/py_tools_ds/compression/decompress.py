# -*- coding: utf-8 -*-

# py_tools_ds - A collection of geospatial data analysis tools that simplify standard
# operations when handling geospatial raster and vector data as well as projections.
#
# Copyright (C) 2016–2025
# - Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz.de)
# - GFZ Helmholtz Centre for Geosciences, Potsdam, Germany (https://www.gfz.de/)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import zipfile
import tarfile
import gzip
from logging import getLogger
import shutil

__author__ = 'Daniel Scheffler'


def decompress(compressed_file, outputpath=None, logger=getLogger('decompressor')):
    """Decompress ZIP, TAR, TAR.GZ, TGZ and GZ archives to a given output path.

    :param compressed_file:
    :param outputpath:
    :param logger:      instance of logging.Logger
    """
    # define output folder and filename
    in_folder, in_filename = os.path.split(compressed_file)
    out_folder, out_filename = os.path.split(outputpath) if outputpath else ('', '')
    out_filename = out_filename or in_filename.partition(".")[0]
    out_folder = out_folder or in_folder
    outputpath = os.path.join(out_folder, out_filename)

    # decompress
    logger.info('Extracting ' + in_filename + '...')

    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)

    if compressed_file.endswith(".zip"):
        assert zipfile.is_zipfile(compressed_file), \
            logger.critical(compressed_file + " is not a valid zipfile!")
        zf = zipfile.ZipFile(compressed_file)
        names = zf.namelist()
        count_extracted = 0
        for n in names:
            if os.path.exists(os.path.join(outputpath, n)) and \
                    zipfile.ZipFile.getinfo(zf, n).file_size == os.stat(os.path.join(outputpath, n)).st_size:
                logger.warning("file '%s' from '%s' already exists in the directory: '%s'"
                               % (n, in_filename, outputpath))
            else:
                written = 0
                while written == 0:
                    try:
                        zf.extract(n, outputpath)
                        logger.info("Extracting %s..." % n)
                        count_extracted += 1
                        written = 1
                    except OSError as e:
                        if e.errno == 28:
                            print('No space left on device. Waiting..')
                        else:
                            raise
        if count_extracted == 0:
            logger.warning("No files of %s have been decompressed.\n" % in_filename)
        else:
            logger.info("Extraction of '" + in_filename + " was successful\n")
        zf.close()

    elif compressed_file.endswith((".tar", ".tar.gz", ".tgz")):
        tf = tarfile.open(compressed_file)
        names, members = tf.getnames(), tf.getmembers()
        count_extracted = 0
        for n, m in zip(names, members):
            if os.path.exists(os.path.join(outputpath, n)) and \
                    m.size == os.stat(os.path.join(outputpath, n)).st_size:
                logger.warning("file '%s' from '%s' already exists in the directory: '%s'"
                               % (n, in_filename, outputpath))
            else:
                written = 0
                while written == 0:
                    try:
                        tf.extract(n, outputpath)
                        logger.info("Extracting %s..." % n)
                        count_extracted += 1
                        written = 1
                    except OSError as e:
                        if e.errno == 28:
                            print('No space left on device. Waiting..')
                        else:
                            raise
        if count_extracted == 0:
            logger.warning("No files of %s have been decompressed.\n" % in_filename)
        else:
            logger.info("Extraction of '" + in_filename + " was successful\n")
        tf.close()

    elif compressed_file.endswith(".gz"):
        with gzip.open(compressed_file, 'rb') as f_in:
            with open(outputpath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    else:
        raise ValueError('Unexpected file extension of compressed file. Supported file extensions are: '
                         '*.zip, *.tar and *.tgz')
