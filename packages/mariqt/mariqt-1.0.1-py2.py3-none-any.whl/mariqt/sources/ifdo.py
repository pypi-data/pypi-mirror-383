""" This class provides functionalities to create, read and adapt iFDO files"""

from math import pi
import math
import yaml
import os
import json
import numpy as np
import ast
import copy
import datetime
from pprint import pprint
from deepdiff import DeepDiff
from packaging.version import Version
import statistics
import requests
import zipfile
import io
import warnings

import mariqt.core as miqtc
import mariqt.directories as miqtd
import mariqt.files as miqtf
import mariqt.variables as miqtv
import mariqt.image as miqti
import mariqt.tests as miqtt
import mariqt.navigation as miqtn
import mariqt.settings as miqts
import mariqt.provenance as miqtp
import mariqt.geo as miqtg
import mariqt.sources.osis as miqtosis
import mariqt.equipment as miqtequip
from mariqt.sources.ifdo_reader import IfdoReader


class NonCoreFieldIntermediateItemInfoFile:
    def __init__(self, fileName:str, separator:str, header:dict, datetime_format:str=miqtv.date_formats['mariqt']):
        self.fileName = fileName
        self.separator = separator
        self.header = header
        self.datetime_format = datetime_format

    def __eq__(self, other):
        if self.fileName==other.fileName and self.separator == other.separator and self.header==other.header and self.datetime_format==other.datetime_format:
            return True
        else:
            return False




def ifdoFromFile(iFDOfile:str,
                 handle_prefix='20.500.12085',
                 provenance = None,
                 verbose=True,
                 ignore_image_files=False,
                 write_tmp_prov_file=True,
                 image_broker_uuid="ee277578-a911-484d-a515-9c781d79aa91",
                 sub_folders_ignore:list=[]):
    """ Convenience function to create an iFDO object directly form an existing iFDO file. Tries to infer image files location from 'image-set-local-path'. Returns iFDO object. 
        - iFDOfile: string path to load an explicit iFDO file.
        - handle_prefix: string prefix of the handle server. Default: the one for Geomar.
        - provenance: mariqt.provencance.Provenance object to track data provenance. Default: a new provenance object is created in the 'protocol' subfolder.
        - verbose: bool whether to print out information. Processing is faster if verbose is False. Default: True.
        - ignore_image_files: bool whether it's accepted that there are not images yet in 'dir'. Default: False.
        - write_tmp_prov_file: bool whether to write a temporary provenance file during the iFDO creation process which will be replaced by a final one in the end. Default: True
        - image_broker_uuid: uuid of image broker to create image handles as https://hdl.handle.net/<handle_prefix>/<image_broker_uuid>@<image-uuid> 
        - sub_folders_ignore: list of strings containing names of folders which are to be ignored while scanning dir for image data 
    """
    
    reader = IfdoReader(iFDOfile)
    imagesDir = miqtc.toUnixPath(os.path.normpath(miqtc.toUnixPath(reader.getImageDirectory())))
    baseDir = miqtc.toUnixPath(os.path.commonpath([iFDOfile,imagesDir]))
    imageDataTypeFolder = [e for e in imagesDir.replace(baseDir,"").split("/") if e != ""][0]
    if imageDataTypeFolder not in miqtd.Dir.dt.__members__:
        raise miqtc.IfdoException("Images are not located in a valid data type directory (raw, intermediate, processed, ...) in the same project as iFDO file.")
    imagesDataTypeDir = os.path.join(baseDir,imageDataTypeFolder)
    dirObj = miqtd.Dir("",imagesDataTypeDir, create=False, with_gear=False)
    return iFDO(dir=dirObj,handle_prefix=handle_prefix,provenance=provenance,verbose=verbose,ignore_image_files=ignore_image_files,write_tmp_prov_file=write_tmp_prov_file,
                iFDOfile=iFDOfile,image_broker_uuid=image_broker_uuid, create_all_type_folders=False,sub_folders_ignore=sub_folders_ignore)


class iFDO:
    " Class for creating and editing iFDO.yaml files "

    def __init__(self, dir:miqtd.Dir, 
                 handle_prefix='20.500.12085', 
                 provenance:miqtp.Provenance = None,
                 verbose=True,
                 ignore_image_files=False,
                 write_tmp_prov_file=True,
                 iFDOfile=None,
                 image_broker_uuid="ee277578-a911-484d-a515-9c781d79aa91", 
                 create_all_type_folders=True, 
                 sub_folders_ignore:list=[]):
        """ Creates an iFOD object. Requires a valid directory containing image data or/and and iFDO file and a handle prefix if it's not the Geomar one. Loads directory's iFDO file if it exists already.
            - dir: mariqt.directories.Dir object pointing to a valid data type directory (raw, intermediate, processed, ...) containing the image data.
            - handle_prefix: string prefix of the handle server. Default: the one for Geomar.
            - provenance: mariqt.provencance.Provenance object to track data provenance. Default: a new provenance object is created in the 'protocol' subfolder.
            - verbose: bool whether to print out information. Default: True.
            - ignore_image_files: images files are ignored. They are not searched for in 'raw' and items values are not updated nor checked. Default = False
            - write_tmp_prov_file: bool whether to write a temporary provenance file during the iFDO creation process which will be replaced by a final one in the end. Default: True
            - iFDOfile: string path to load an explicit iFDO file. If not provided a matching iFDO file (if it already exists) will be loaded from the 'products' subdirectory. Default: None 
            - image_broker_uuid: uuid of image broker to create image handles as https://hdl.handle.net/<handle_prefix>/<image_broker_uuid>@<image-uuid> 
            - create_all_type_folders: whether to create all type folders (external, intermediate, processed, ...) or only the needed ones 
            - sub_folders_ignore: list of strings containing names of folders which are to be ignored while scanning dir for image data 
        """

        miqtv.setGlobalVerbose(verbose)
        self._handle_prefix = "https://hdl.handle.net/" + handle_prefix
        self._image_handle_prefix = self._handle_prefix + "/" + image_broker_uuid
        self._ignore_image_files = ignore_image_files
        self._initAndCheckDir(dir, create_all_type_folders)
        self._initProvenance(provenance, write_tmp_prov_file)

        self._raiseExceptionIfNeitherDirNorIfdoFileProvided(dir, iFDOfile)
        
        self._ifdo_file = ""
        if self._ifdoFileProvidedAndSet(iFDOfile):
            ifdo_file_to_try_load = self._ifdo_file
        else:
            ifdo_file_to_try_load = self._constructIfdoFileNameFromDir()

        self._initInternalIfdoDics()
        self._initIntermediateFilesVariables()
        self._initImagesLists(sub_folders_ignore) # browses for images, may take some time
        self._checkLoadedImagesNamesAreUniqueAndValid()
        
        self._tryLoadIfdoFileOrFirstInProductsDirIfAny(ifdo_file_to_try_load)
        
        self._fillImageSetUuidAndHandleIfEmpty()
        self._fillImageSetIfdoVersion()
        self._fillEmptyHeaderFieldsWithAvailableInfoFromDirNames()
        self._fillImageSetNameIfEmptyFromFieldsProjectEventSensorIfAvailable()
        self._fillImageSetLocalPath()


    def _initAndCheckDir(self, dir:miqtd.Dir, create_all_type_folders:bool):
        self._dir = dir
        self._images_dir = dir.totype()
        if create_all_type_folders:
            self._dir.createTypeFolder()

        if not self._ignore_image_files and not dir.exists():
            raise miqtc.IfdoException("directroy", dir.str(), "does not exist.")

        if not dir.validDataDir():
            raise miqtc.IfdoException("directroy", dir.str(), "not valid. Does not comply with structure /base/project/[Gear/]event/sensor/data_type/")


    def _initProvenance(self, provenance:miqtp.Provenance, write_tmp_prov_file:bool):
        self._prov = provenance
        if self._prov == None:
            tmpFilePath = ""
            if write_tmp_prov_file:
                self._dir.createTypeFolder([self._dir.dt.protocol.name])
                tmpFilePath = self._dir.to(self._dir.dt.protocol)
            self._prov = miqtp.Provenance("iFDO",verbose=miqtv.getGlobalVerbose(),tmpFilePath=tmpFilePath)


    def _raiseExceptionIfNeitherDirNorIfdoFileProvided(self, dir, ifdo_file):
        if dir is None and ifdo_file is None:
            raise miqtc.IfdoException("Neither dir nor iFDOfile provided for iFDO.")

    
    def _ifdoFileProvidedAndSet(self, ifdo_file):
        if ifdo_file == "":
            ifdo_file = None

        if ifdo_file is not None:
            if not os.path.isfile(ifdo_file):
                raise miqtc.IfdoException("iFDO file not found: " + ifdo_file)
            self._ifdo_file = ifdo_file
            return True
        return False


    def _constructIfdoFileNameFromDir(self):
        path = self._dir.to(self._dir.dt.products)
        file_name = iFDO.constructImageSetName(self._dir.project(), self._dir.event(), self._dir.sensor()) + '_iFDO.json' 
        return os.path.join(path, file_name)


    def _initInternalIfdoDics(self):
        self._ifdo_tmp = {miqtv.image_set_header_key: {},
                          miqtv.image_set_items_key: {}}
        self._ifdo_parsed = None
        self._ifdo_checked = copy.deepcopy(self._ifdo_tmp)  # to be set by createiFDO() only!
        self._all_uuids_checked = False


    def _initIntermediateFilesVariables(self):
        self.intermediateFilesDef_core = {
            'hashes': {
                'creationFct': 'create_image_sha256_file()',
                'suffix': '_image-hashes.txt',
                'cols': [miqtv.col_header['mariqt']['hash']],
                'optional': []},
            'uuids': {
                'creationFct': 'create_uuid_file()',
                'suffix': '_image-uuids.txt',
                'cols': [miqtv.col_header['mariqt']['uuid']],
                'optional': []},
            'datetime': {
                'creationFct': 'create_start_time_file()',
                'suffix': '_image-start-times.txt',
                'cols': [miqtv.col_header['mariqt']['utc']],
                'optional': []},
            'navigation': {
                'creationFct': 'create_image_navigation_file()',
                'suffix': '_image-navigation.txt',
                'cols': [miqtv.col_header['mariqt']['utc']],
                'optional': [miqtv.col_header['mariqt']['lon'], miqtv.col_header['mariqt']['lat'], miqtv.col_header['mariqt']['alt'], miqtv.col_header['mariqt']['hgt'], miqtv.col_header['mariqt']['uncert']]},
        }

        self.nonCoreFieldIntermediateItemInfoFiles = []


    def _initImagesLists(self, sub_folders_ignore:list):
        """ browse for image files if not self._ignore_image_files and set internal images lists """
        self._images_in_images_dir = []
        if self._ignore_image_files:
            self._prov.log("Caution! running in ignore_image_files mode.")
        else:
            self._images_in_images_dir = miqti.browseForImageFiles(self._images_dir, sub_folders_ignore=sub_folders_ignore)
        self._images_in_images_dir_sorted_list = [file for file in self._images_in_images_dir]
        self._images_in_images_dir_sorted_list.sort()
        self._imageNamesImagesDir = [os.path.basename(file) for file in self._images_in_images_dir]

        if len(self._images_in_images_dir) == 0 and not self._ignore_image_files:
            raise Exception("No images files found in " + self._images_dir + " and its subdirectories")
        
        files_found_log_msg_append = " image files found"
        if len(sub_folders_ignore) != 0:
            files_found_log_msg_append += ", ignoring subfolders " + str(sub_folders_ignore)
        self._prov.log(str(len(self._images_in_images_dir)) + files_found_log_msg_append)
        

    def _checkLoadedImagesNamesAreUniqueAndValid(self):
        unique, dup = miqtt.filesHaveUniqueName(self._images_in_images_dir)
        if not unique:
            raise Exception(
                "Not all files have unique names. Duplicates: " + str(dup))

        allvalid, msg = miqtt.allImageNamesValid(self._images_in_images_dir) 
        if not allvalid:
            raise Exception(msg)
        

    def _tryLoadIfdoFileOrFirstInProductsDirIfAny(self, ifdo_file_to_try_load):
        loaded_ifdo = False
        if(os.path.isfile(ifdo_file_to_try_load) and self._parseAndCheckIfdoFile(ifdo_file_to_try_load)):
            loaded_ifdo = True
        else:
            loaded_ifdo, ifdo_file_to_try_load = self._loadFirstIfdoFileInProductsDirIfAny()

        if loaded_ifdo:
            self._ifdo_file = ifdo_file_to_try_load
            self._assertIfdoFileName()


    def _assertIfdoFileName(self):
        if miqtc.assertSlash(os.path.dirname(self._ifdo_file)) != miqtc.assertSlash(self._dir.to(self._dir.dt.products)):
            self._prov.log("Caution! iFDO file path is not in 'products' sub folder as" \
                           "recommended. Consider resetting with setiFDOFileName()." + os.path.basename(self._ifdo_file))
        try:
            event = self.getUncheckedValue('image-event')['name']
            sensor = self.getUncheckedValue('image-sensor')['name']
        except miqtc.IfdoException:
            event = self._dir.event()
            sensor = self._dir.sensor()

        iFDOfileName = os.path.basename(self._ifdo_file)
        if  not event in iFDOfileName or not iFDO.getShortEquipmentID(sensor) in iFDOfileName:
            self._prov.log("Caution! iFDO file name does not contain project, event and sensor name as recommended." \
                           "Consider resetting with setiFDOFileName(). " +  os.path.basename(self._ifdo_file))


    def _loadFirstIfdoFileInProductsDirIfAny(self):
        loaded_ifdo = False
        ifdo_file_to_try_load = ""
        try:
            path = self._dir.to(self._dir.dt.products)
            for file_ in os.listdir(path):
                if file_[-10:-4] == "_iFDO." and self._parseAndCheckIfdoFile(path+file_):
                    loaded_ifdo = True
                    ifdo_file_to_try_load = path+file_
                    break
        except FileNotFoundError:
            pass
        return loaded_ifdo, ifdo_file_to_try_load


    def _fillImageSetUuidAndHandleIfEmpty(self):
        if not 'image-set-uuid' in self._ifdo_tmp[miqtv.image_set_header_key]:
            self._ifdo_tmp[miqtv.image_set_header_key]['image-set-uuid'] = str(miqtc.uuid4())
        if not 'image-set-handle' in self._ifdo_tmp[miqtv.image_set_header_key]:
            self._ifdo_tmp[miqtv.image_set_header_key]['image-set-handle'] = self._handle_prefix + "/" + self.getUncheckedValue('image-set-uuid')
        

    def _fillImageSetIfdoVersion(self):
        self._ifdo_tmp[miqtv.image_set_header_key]['image-set-ifdo-version'] = miqtv.iFDO_version


    def _fillEmptyHeaderFieldsWithAvailableInfoFromDirNames(self):
        """ Sets certain header fields e.g. from directory if they are not set yet """
        if self.findUncheckedValue('image-sensor') == "":
            self._ifdo_tmp[miqtv.image_set_header_key]['image-sensor'] = {'name': self._dir.sensor()}
            self._prov.log("'image-sensor'\t empty, parsed from directoy and set to: " + self._ifdo_tmp[miqtv.image_set_header_key]['image-sensor']['name'])

        if self.findUncheckedValue('image-event') == "":
            self._ifdo_tmp[miqtv.image_set_header_key]['image-event'] = {'name': self._dir.event()}
            self._prov.log("'image-event'\t empty, parsed from directoy and set to: " + self._ifdo_tmp[miqtv.image_set_header_key]['image-event']['name'])

        if self.findUncheckedValue('image-project') == "":
            self._ifdo_tmp[miqtv.image_set_header_key]['image-project'] =  {'name': self._dir.project()}
            self._prov.log("'image-project'\t empty, parsed from directoy and set to: " + self._ifdo_tmp[miqtv.image_set_header_key]['image-project']['name'])

        if self.findUncheckedValue('image-platform') == "" and self._dir.gear() != "":
            self._ifdo_tmp[miqtv.image_set_header_key]['image-platform'] = {'name': self._dir.gear()}
            self._prov.log("'image-platform'\t empty, parsed from directoy and set to: " + self._ifdo_tmp[miqtv.image_set_header_key]['image-platform']['name'])


    def _fillImageSetNameIfEmptyFromFieldsProjectEventSensorIfAvailable(self):
        if not 'image-set-name' in self._ifdo_tmp[miqtv.image_set_header_key] or self.findUncheckedValue('image-set-name') == "":
            # construct as <project>_<event>_<sensor>
            project_ = self.findUncheckedValue("image-project")['name']
            event_ = self.findUncheckedValue("image-event")['name']
            if event_ == "":
                event_ = self._dir.event()
            sensor_ = self.findUncheckedValue("image-sensor")['name']
            if sensor_ == "":
                sensor_ = self._dir.sensor()
            self._ifdo_tmp[miqtv.image_set_header_key]['image-set-name'] = iFDO.constructImageSetName(project_,event_,sensor_)

    
    def setImageSetNameFieldFromProjectEventSensor(self):
        """ Sets field image-set-name from current tmp fields for project, event and sensor. 
        Returns image-set-name value. """
        
        new_image_set_name = self._getImageSetNameFieldFromProjectEventSensor(self._ifdo_tmp)
        self._ifdo_tmp[miqtv.image_set_header_key]['image-set-name'] = new_image_set_name
        return new_image_set_name
        

    @staticmethod
    def _getImageSetNameFieldFromProjectEventSensor(ifdo:dict):
        """ Creates and returns image-set-name from current tmp fields for project, event and sensor. """
        new_image_set_name = iFDO.constructImageSetName(ifdo['image-set-header']['image-project']['name'],
                                                        ifdo['image-set-header']['image-event']['name'],
                                                        ifdo['image-set-header']['image-sensor']['name'])
        return new_image_set_name



    def _fillImageSetLocalPath(self):
        """ Sets header field 'image-set-local-path' from image dir """
        self._ifdo_tmp[miqtv.image_set_header_key]['image-set-local-path'] = os.path.relpath(self._images_dir, os.path.dirname(self.getIfdoFileName()))


    def _parseAndCheckIfdoFile(self,file:str):
        """ loads iFDO file """

        s = miqtc.PrintLoadingMsg("Loading iFDO file")
        try:
            self._ifdo_tmp = self._openIfdoFile(file)
            self._ifdo_parsed = copy.deepcopy(self._ifdo_tmp)
            s.stop()
            self._prov.addPreviousProvenance(self._prov.getLastProvenanceFile(self._dir.to(self._dir.dt.protocol),self._prov.executable))
        except miqtc.IfdoException:
            s.stop()
            return False
        except Exception as e:
            s.stop()
            self._prov.log(str(e))
            return False

        # try to parse e.g. strings that represent dicts
        miqtc.recursiveEval(self._ifdo_tmp)

        try:
            self._makeSureContainsHeaderAndItmesDict(self._ifdo_tmp)
        except Exception as ex:
            raise miqtc.IfdoException("Error loading iFDO file ", file, ": " + str(ex))

        self._prov.log("iFDO file loaded: " + os.path.basename(file))

        try:
            self._convertToDefaultDatetimeFormat(self._ifdo_tmp)
        except Exception as ex:
            self._prov.log("Checking datetime formats: " + str(ex))

        self._tryUpgradeToCurrentIfdoVersion()

        self._makePhotoItemsDictIfListOfDicts(self._ifdo_tmp)

        # check and update internal ifdo dict
        try:
            self._createAndCheck(self._ifdo_tmp[miqtv.image_set_header_key], self._ifdo_tmp[miqtv.image_set_items_key])
        except miqtc.IfdoException as ex:
            self._prov.log("Loaded iFDO file not valid yet: " + str(ex))

        return True


    @staticmethod
    def _openIfdoFile(file:str):  
        """ open ifdo json or yaml or zip file and return as dict. """
        
        # if file is zip, unzip
        if file.split('.')[-1] == 'zip':
            file_name = '.'.join(os.path.basename(file).split('.')[0:-1])
            zip_file = zipfile.ZipFile(file)
            ifdo_file = zip_file.open(file_name, 'r')
            with io.TextIOWrapper(ifdo_file, encoding="utf-8") as o:
                if file.split('.')[-1] == 'yaml':
                    ifdo_dct = miqtf.loadYamlFileFromStream(o)
                else:
                    ifdo_dct = miqtf.loadJsonFileFromStream(o)

        else:
            try_yaml = False
            
            # if file is yaml file load it as such
            if file.split('.')[-1] == 'yaml':
                try_yaml = True
                file_yaml = file

            if not os.path.isfile(file):
                # if file does not exist check if yaml version exsist and try to load that one
                file_yaml = file.replace('.json','.yaml')
                if os.path.isfile(file_yaml):
                    try_yaml = True
                else:
                    raise miqtc.IfdoException("File not found: " + file)

            # try load json, otherwise try yaml
            if try_yaml:
                ifdo_dct = miqtf.loadYamlFile(file_yaml)
            else:
                ifdo_dct = miqtf.loadJsonFile(file)

        return ifdo_dct


    @staticmethod
    def _makeSureContainsHeaderAndItmesDict(ifdo:dict):
        if miqtv.image_set_header_key not in ifdo:
            raise Exception("does not contain ", miqtv.image_set_header_key)
        if miqtv.image_set_items_key not in ifdo:
            raise Exception("does not contain ", miqtv.image_set_items_key)

        if ifdo[miqtv.image_set_header_key] == None:
            ifdo[miqtv.image_set_header_key] = {}
        if ifdo[miqtv.image_set_items_key] == None:
            ifdo[miqtv.image_set_items_key] = {}


    def _convertToDefaultDatetimeFormat(self, ifdo):
        """ Checks if all items' 'image-datetime' fields match default datetime format or a custom one defined in 'image-datetime-format'
            and converts to default format. Throws exception if datetime cannot be parsed """
        customDateTimeFormatFound = False
        headerCustomDateTimeFormat = iFDO._findPlainValue(ifdo[miqtv.image_set_header_key],'image-datetime-format')
        if headerCustomDateTimeFormat != "":
            ifdo[miqtv.image_set_header_key]['image-datetime-format'] = "" # remove custom format # TODO why not keep?
            customDateTimeFormatFound = True
        prog = miqtc.PrintKnownProgressMsg("Checking datetime formats", len(ifdo[miqtv.image_set_items_key]),modulo=1)
        for file,item in ifdo[miqtv.image_set_items_key].items():
            prog.progress()
            if not isinstance(item,list):
                    item = [item]
            subItemDefault = item[0]
            itemCustomDateTimeFormat = ""
            if 'image-datetime-format' in subItemDefault:
                itemCustomDateTimeFormat = subItemDefault['image-datetime-format']
                subItemDefault['image-datetime-format'] = "" # remove custom format # TODO why not keep?
                customDateTimeFormatFound = True
            for subItem in item:
                try:
                    format = miqtv.date_formats['mariqt']
                    datetime.datetime.strptime(subItem['image-datetime'],format)
                except:
                    try:
                        format = headerCustomDateTimeFormat
                        dt = datetime.datetime.strptime(subItem['image-datetime'],format)
                        subItem['image-datetime'] = datetime.datetime.strftime(dt,miqtv.date_formats['mariqt'])
                    except:
                        try:
                            format = itemCustomDateTimeFormat
                            dt = datetime.datetime.strptime(subItem['image-datetime'],format)
                            subItem['image-datetime'] = datetime.datetime.strftime(dt,miqtv.date_formats['mariqt'])
                        except:
                            prog.clear()
                            raise miqtc.IfdoException('Invalid datetime value',subItem['image-datetime'], "does not match format default or custom format")
        if customDateTimeFormatFound:
            self._prov.log("Custom datetime formats found. They will be replaced by the default format.")   
        prog.clear()    


    def writeIfdoFile(self,allow_missing_required=False, as_zip:bool=False, float_decimals=None):
        """ Writes an iFDO file to disk. Overwrites potentially existing file.
        as_zip: safe file as zip file
        float_decimals: (unittesting only) number of decimals for float to string conversion. Keep None to use max precision. """

        s = miqtc.PrintLoadingMsg("Writing iFDO file")

        self._dir.createTypeFolder([self._dir.dt.products.name, self._dir.dt.protocol.name])

        self._checkFieldsAgainIfChangedSinceLastCheck(allow_missing_required)
        
        # add "$schema"
        self._ifdo_checked["$schema"] = miqtv.ifdo_schema['$id']
        
        iFDO_path = self.getIfdoFileName(overwrite=True)

        # convert dictionary to JSON string
        json_data = self._getIfdoAsJsonStr(self._ifdo_checked, float_decimals)

        # write the JSON string to a file
        if as_zip:
            with zipfile.ZipFile(iFDO_path + '.zip','w', zipfile.ZIP_DEFLATED) as zip:
                zip.writestr(os.path.basename(iFDO_path), json_data)
        else:
            with open(iFDO_path, 'w') as f:
                f.write(json_data)
        
        # log changes
        if self._ifdo_parsed is not None:
            ifdo_update = DeepDiff(self._ifdo_parsed,self._ifdo_checked)
            s.stop() 
            #pprint(ifdo_update)
            if ifdo_update != {}:
                self._prov.log("iFDO updated")
                self._prov.log(ifdo_update.to_json(), dontShow=True) # to_json to have uniform conversion to string
        else:
             s.stop() 
        
        self._prov.write(self._dir.to(self._dir.dt.protocol))
        self._prov.log("Wrote iFDO to file " + self._dir.getRelativePathToProjectsBaseDir(iFDO_path))


    def _checkFieldsAgainIfChangedSinceLastCheck(self, allow_missing_required:bool):
        if self._ifdo_tmp != self._ifdo_checked:
            self._createAndCheck(self._ifdo_tmp[miqtv.image_set_header_key], self._ifdo_tmp[miqtv.image_set_items_key],
                            allow_missing_required=allow_missing_required)


    def getIfdoFileName(self,overwrite=False):
        """ Returns the current iFDO file's name with path. If not set yet or overwrite==True it returns and sets the one matching image-set-name. """
        if self._ifdo_file == "" or overwrite:
            # TODO 'image-set-name' kann auch noch leer sein
            file_name = self.getUncheckedValue('image-set-name') + '_iFDO.json'
            if self._ifdo_file != "":
                # rename file but keep location
                if file_name != os.path.basename(self._ifdo_file) and os.path.exists(self._ifdo_file):
                    self._prov.log("Caution! ifdo file renamed to " + file_name)
                self._ifdo_file = os.path.join(os.path.dirname(self._ifdo_file),file_name)
            else:
                self._ifdo_file = os.path.join(self._dir.to(self._dir.dt.products), file_name)
        return self._ifdo_file


    @staticmethod
    def constructImageSetName(project:str,event:str,sensor:str):
        """ returns <project>_<event>_<sensor>, with short version of <sensor> (only id), preventing potential doubling of <project>  """
        project = project.strip().replace(' ','-')
        event = event.strip().replace(' ','-')
        sensor = sensor.strip().replace(' ','-')
        sensor_short = iFDO.getShortEquipmentID(sensor)
        if len(event) > len(project) and event[0:len(project)] == project:
            image_set_name_ = event + "_" + sensor_short
        else:
            image_set_name_ = project + "_" + event + "_" + sensor_short
        return image_set_name_ # TODO include dataType?


    @staticmethod
    def getShortEquipmentID(equipmentID:str):
        """ returns equipment id without potentiall long <name> part, i.e.: <owner>_<type>-<type index[_<subtype>] """
        return '_'.join(equipmentID.split('_')[0:3])


    def _tryUpgradeToCurrentIfdoVersion(self):
        """ Try to convert fields from iFDO version < 2.0.0 to 2.x """
        read_version_str = "v1.0.0" # did not have the 'image-set-ifdo-version' field yet
        try: 
            read_version_str = self.getUncheckedValue('image-set-ifdo-version')
        except miqtc.IfdoException:
            pass
        read_version = Version(read_version_str)
        current_version = Version(miqtv.iFDO_version)

        if read_version > current_version:
            self._prov.log("Warning! Loaded iFDO has version " + read_version_str + " which is ahead of version used here: " + miqtv.iFDO_version)

        if read_version < current_version:
            self._prov.log("Loaded iFDO has version " + read_version_str + " and will be updated to version " + miqtv.iFDO_version)

            # new URI object fields
            new_uri_fields = ['image-sensor','image-event','image-project','image-context','image-license','image-platform']
            for uri_field in new_uri_fields:
                old_str_val = self.findUncheckedValue(uri_field)
                if isinstance(old_str_val,str) and old_str_val != "":                    
                    new_obj_val = {'name': old_str_val}
                    is_uri, msg = miqtt.validateAgainstSchema(old_str_val,{"type": "string","format": "uri"})
                    if is_uri:
                        new_obj_val['uri'] = old_str_val
                    self._ifdo_tmp[miqtv.image_set_header_key][uri_field] = new_obj_val
                    self._prov.log("Auto-upgraded " + uri_field + " from " + old_str_val + " to " + str(new_obj_val))


    @staticmethod
    def _makePhotoItemsDictIfListOfDicts(ifdo:dict, provenance:miqtp.Provenance = None):
        """ Loaded (old) iFDOs may contain photo item which consist of a list of dicts (like videos,
            but of length 1) instead of just a dict. This is corrected here. """
        for item_name in ifdo[miqtv.image_set_items_key]:
            if item_name.split('.')[-1].lower() in miqtv.photo_types:
                item_entry = ifdo[miqtv.image_set_items_key][item_name]
                if isinstance(item_entry, list):
                    if len(item_entry) > 1:
                        error_msg = "Error! Image item '" + item_name + "'contains multiple entries! Please correct!"
                        if provenance is not None:
                            provenance.log(error_msg)
                        else:
                            print(error_msg)
                    else:
                        ifdo[miqtv.image_set_items_key][item_name] = ifdo[miqtv.image_set_items_key][item_name][0]


    def getDir(self):
        return self._dir
    

    def getHandlePrefix(self):
        return self._handle_prefix
    
    
    def __str__(self) -> str:
        """ Prints current iFDO file """
        return self._getIfdoAsJsonStr(self._ifdo_checked)
    

    def _getIfdoAsJsonStr(self, ifdo:dict, float_decimals=None):
        json_to_dump = ifdo
        if float_decimals is not None:
            json_to_dump = miqtc.roundFloats(ifdo, decimals=float_decimals)
        json_data = json.dumps(json_to_dump, indent = 4, sort_keys=True)
        return json_data


    def __getitem__(self, keys:str):
        """ Returns copy of checked ifdo header or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Raises IfdoException if item does not exist. """
        keys = keys.split(':')
        return self._getValue(self._ifdo_checked,keys)
    

    def getUncheckedJson(self):
        """ Retruns json of unchecked ifdo. """
        return self._getIfdoAsJsonStr(self._ifdo_tmp)
    
    
    def getUnchecked(self):
        """ Retruns unchecked ifdo dict. """
        return self._ifdo_tmp


    def getCheckedJson(self):
        """ Retruns json of unchecked ifdo. """
        return self._getIfdoAsJsonStr(self._ifdo_checked)
    

    def getChecked(self):
        """ Return copy of checked ifdo dict. """
        return copy.deepcopy(self._ifdo_checked)


    def getCheckedValue(self,keys:str):
        """ Same as item accessor via "[]" (__getitem__).
            Returns copy of checked ifdo header or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Raises IfdoException if item does not exist.
        """
        keys = keys.split(':')
        return self._getValue(self._ifdo_checked,keys)


    def findCheckedValue(self, keys:str):
        """ Returns copy of checked ifdo header or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Returns empty string if item does not exist. """
        return iFDO._findValue(self._ifdo_checked,keys)


    def getUncheckedValue(self,keys:str):
        """ Returns copy of temporary unchecked ifdo header or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Raises IfdoException if item does not exist. """
        keys = keys.split(':')
        return self._getValue(self._ifdo_tmp,keys)
    

    def findUncheckedValue(self,keys:str):
        """ Returns copy of temporary unchecked ifdo header or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Returns empty string if item does not exist. """
        return iFDO._findValue(self._ifdo_tmp,keys)
    

    @staticmethod
    def _findValue(ifdo:dict,keys):
        """ Returns copy of ifdo set or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Returns empty string if item does not exist. """
        keys = keys.split(':')
        try:
            ret = iFDO._getValue(ifdo,keys)
        except miqtc.IfdoException as ex:
            ret = ""
        return ret


    @staticmethod
    def _getValue(ifdo:dict,keys:list,default_only = False):
        """ returns copy of set or item field value, also considerng default values from header.
            Use keys as e.g. [<item>,<key>,..]. Can be used for header fields as well as item fields.
            Item index can be neglected, in case of video a dict {<image-datatime>:<value>,...} is returned
            unless default_only = False, then default values at index 0 is returned.
            Raises IfdoException if keys do not exist. """

        if not miqtv.image_set_items_key in ifdo or not miqtv.image_set_header_key in ifdo:
            raise miqtc.IfdoException("Invalid ifdo dict, missing items or header key: " + str(ifdo))
        
        if not isinstance(keys,list):
            keys = [keys]

        # remove header or item prefixes if there
        if keys[0] == miqtv.image_set_items_key or keys[0] == miqtv.image_set_header_key:
            keys = keys[1::]

        header = ifdo[miqtv.image_set_header_key]
        items = ifdo[miqtv.image_set_items_key]
        # look for default value
        for skippedInHeader in range(len(keys)):
            defaultVal = iFDO._findPlainValue(header,keys[skippedInHeader::])
            if defaultVal != "":
                break


        ## look for item value
        # header only value, don't check in items
        if iFDO._findPlainValue(items,keys[0:1]) == "" and skippedInHeader == 0:
            ret = defaultVal
            if ret == "":
                raise miqtc.IfdoException("key does not exist:" + str(keys))
        else:
            # if first key not found in items, i.e. is not a image name, and first key is not a header key:
            if iFDO._findPlainValue(items,keys[0:1]) == "" and skippedInHeader != 0:
                raise miqtc.IfdoException("item does not exist:" + str(keys[0:1]))

            # check if index provided
            indexProvided = True
            if len(keys) > 1:
                try:
                    index = int(keys[1])
                except Exception:
                    indexProvided = False
            elif len(keys) == 1:
                indexProvided = False
                
            imageItemTimePoints = items[keys[0]]

            if indexProvided:
                # if key is whole image add all values from header
                if len(keys) == 2:
                    defaultVal = header
                # add default from index 0
                if len(keys) > 1 and index != 0:
                    keys_0 = copy.deepcopy(keys)
                    keys_0[1] = 0
                    ret_0 = iFDO._getItemValueJoinedWithDefaultValue(items,keys_0,skippedInHeader,defaultVal)
                    if isinstance(ret_0,dict):
                        defaultVal = {**defaultVal,**ret_0}
                ret = iFDO._getItemValueJoinedWithDefaultValue(items,keys,skippedInHeader,defaultVal)
            
            else:
                # if key is whole image add all values from header
                if len(keys) == 1:
                    defaultVal = header

                # picture -> just one entry, insert index 0
                if type(imageItemTimePoints) == dict or (type(imageItemTimePoints) == list and len(imageItemTimePoints) == 1):
                    ret = iFDO._getItemValueJoinedWithDefaultValue(items,keys,skippedInHeader,defaultVal)
                    
                # video -> return values for each time stamp
                else:
                    ret = {}
                    for i in range(len(imageItemTimePoints)):
                        timePointData = imageItemTimePoints[i]
                        keys_i = keys[0:1] + [i] + keys[1::]
                        val_i = iFDO._getItemValueJoinedWithDefaultValue(items,keys_i,skippedInHeader,defaultVal)
                        # default only
                        if default_only:
                            ret = val_i
                            break
                        ret[timePointData['image-datetime']] = val_i
                        # remove image-datetime if there
                        if isinstance(ret[timePointData['image-datetime']],dict) and 'image-datetime' in ret[timePointData['image-datetime']]:
                            del ret[timePointData['image-datetime']]['image-datetime']
                        # video defaults
                        if i == 0:
                            if isinstance(ret[timePointData['image-datetime']],dict):
                                defaultVal = {**defaultVal,**ret[timePointData['image-datetime']]}
                            else:
                                defaultVal = ret[timePointData['image-datetime']]

                        i += 1

        if isinstance(ret,dict) or isinstance(ret,list):
            ret = copy.deepcopy(ret)
        if ret == "" or ret == {}:
            raise miqtc.IfdoException("keys do not exist:" + str(keys))
        return ret


    @staticmethod
    def _getItemValueJoinedWithDefaultValue(items,keys,skippedInHeader,defaultVal):
        itemValue = iFDO._findPlainValue(items,keys)

        if itemValue == "":
            ret = defaultVal
        # in case of dicts joined header and item fields
        elif isinstance(itemValue,dict) and defaultVal != "":
            if not isinstance(defaultVal,dict):
                raise miqtc.IfdoException("Item field is dict but default value in header is not: " + str(keys))
            ret = {**defaultVal,**itemValue}
        else:
            ret = itemValue
        return ret
    

    @staticmethod
    def _findPlainValue(ifdo_dict,keys):
        """ Looks for  keys ("key" or [key1,key2]) in ifdo_dict and returns its value or an empty string if key not found. 
            Does not consider default values from header. """
        if not isinstance(keys, list):
            keys = [keys]

        ar = ifdo_dict
        for k in keys:
            if k in ar:
                ar = ar[k]
            else:
                try:
                    k = int(k)
                    if not isinstance(ar,list) or len(ar) < k:
                        raise ValueError("Index",k,"out of bounds",len(ar))
                except:
                    return ""
                ar = ar[k]
        return ar


    def setHeaderFields(self, header: dict):
        """ Clears current header fields und sets provided field values. For updating existing ones use update_header_fields() """
        self._ifdo_tmp[miqtv.image_set_header_key] = {}
        if miqtv.image_set_header_key in header:
            header = header[miqtv.image_set_header_key]
        for field in header:
            self._ifdo_tmp[miqtv.image_set_header_key][field] = header[field]


    def updateHeaderFields(self, header: dict):
        """ Updates existing header fields """
        if miqtv.image_set_header_key in header:
            header = header[miqtv.image_set_header_key]
        log = miqtc.recursivelyUpdateDicts(self._ifdo_tmp[miqtv.image_set_header_key], header)
        self._prov.log(log,dontShow=True)


    def createFields(self, header_only:bool=False, allow_missing_required=False):
        """ Create and validate current header fields and item fields from intermediate files. Overwrites existing fields. """
        if header_only:
            item_data = {}
        else:
            item_data = self._getItemDataFromIntermediateFiles()
        self._createAndCheck(self._ifdo_tmp[miqtv.image_set_header_key], item_data, allow_missing_required=allow_missing_required)


    def updateFields(self, header_only:bool=False):
        """ Update and validate current header fields and item fields from intermediate files. """
        if header_only:
            item_data = {}
        else:
            item_data = self._getItemDataFromIntermediateFiles()
        self._updateAndCheck(self._ifdo_tmp[miqtv.image_set_header_key], item_data)

    
    def _getItemDataFromIntermediateFiles(self):
        """ Read data from core and none-core intermdeate files, check files exist, add 'image-handle'.
        Returns dict of form {image-file-name:{field:value},...} 
        """
        item_data_core = self._getItemDataFromIntermediateFilesCore()
        item_data_none_core = self._getItemDataFromIntermediateFilesNoneCore()
        item_data = item_data_core
        log = miqtc.recursivelyUpdateDicts(item_data, item_data_none_core)
        self._prov.log(log,dontShow=True)
        return item_data
    

    def _getItemDataFromIntermediateFilesCore(self):
        """ Read data from core intermdeate files, check files exist, add 'image-handle'.
        Returns dict of form {image-file-name:{field:value},...} 
        """

        # Which files contain the information needed to create the iFDO items core information and which columns shall be used
        req = self.intermediateFilesDef_core

        item_data = {}
        if miqtv.getGlobalVerbose(): 
            print("Parsing intermediate core data ...")
        for r in req:
            file = self._getIntFilePrefix() + req[r]['suffix']
            if not os.path.exists(file):
                self._prov.log("WARNING! For achieving FAIRness an intermediate image info file is missing: "+ self._getIntFilePrefix() + req[r]['suffix']+ " run first: " + req[r]['creationFct'])
            else:
                self._parseItemDataFromTabFile(item_data, file, req[r]['cols'], req[r]['optional'])
                self._prov.log("Parsed item data from: " + self._dir.getRelativePathToProjectsBaseDir(file))

        if len(item_data) == 0:
            raise Exception("No iFDO items")

        # check files exist
        remove = []
        for img in item_data:
            if not img in self._imageNamesImagesDir:
                remove.append(img)
        for img in remove:
            del item_data[img]

        # add image-url
        for img in item_data:
            if isinstance(item_data[img],list): # item is already a list (video) but parsed data is not, i.e. parsed data refers to whole video (time independent), i.e. write to first entry
                uuid = iFDO._findPlainValue(item_data[img][0],'image-uuid')
                if uuid == "":
                    pprint(item_data[img][0])
                    raise miqtc.IfdoException("uuid not found (a)")
                item_data[img][0]['image-handle'] = self._image_handle_prefix + '@' + uuid
            else:
                uuid = iFDO._findPlainValue(item_data[img],'image-uuid')
                if uuid == "":
                    raise miqtc.IfdoException("uuid not found (b)")
                item_data[img]['image-handle'] = self._image_handle_prefix + '@' + uuid

        return item_data


    def _getItemDataFromIntermediateFilesNoneCore(self):
        """ Read data from non-core intermdeate files.
        Returns dict of form {image-file-name:{field:value},...} 
        """
        req = self.nonCoreFieldIntermediateItemInfoFiles

        item_data = {}
        if miqtv.getGlobalVerbose():
            print("Parsing intermediate additional data ...")
        for r in req:
            if os.path.exists(r.fileName):
                self._praseItemDataFromFile(item_data,r.fileName,r.separator,r.header, r.datetime_format)
                self._prov.log("Parsed item data from: " + self._dir.getRelativePathToProjectsBaseDir(r.fileName))
            else:
                self._prov.log("File does not exists: " + self._dir.getRelativePathToProjectsBaseDir(r.fileName))

        # check files exist
        remove = []
        for img in item_data:
            if not img in self._imageNamesImagesDir:
                remove.append(img)
        for img in remove:
            del item_data[img]

        return item_data
    

    def _parseItemDataFromTabFile(self, items: dict, file: str, cols: list, optional: list = [], datetime_format:str=miqtv.date_formats['mariqt']):
        """ parses data from columns in cols and writes info to items. Column 'image-filename' must be in file and does not need to be passed in cols. 
            File must be tab separated and columns names must equal item field names"""
        tmp_data = miqtf.tabFileData(file, cols+['image-filename']+optional, key_col='image-filename', optional=optional,convert=True)
        self._writeParsedDataToItems(tmp_data,items,self._ifdo_tmp[miqtv.image_set_header_key], datetime_format=datetime_format)


    def _praseItemDataFromFile(self,items:dict,file:str,separator:str,header:dict, datetime_format:str=miqtv.date_formats['mariqt']):
        """ parses data from from file to items. header dict must be of structure: {<item-field-name>:<column-name>}
            and must contain entry 'image-filename' """
        if not 'image-filename' in header:
            raise Exception("header does not contain 'image-filename'")
        
        tmp_data = miqtf.tabFileData(file, header,col_separator=separator, key_col='image-filename',convert=True)
        self._writeParsedDataToItems(tmp_data,items,self._ifdo_tmp[miqtv.image_set_header_key], datetime_format=datetime_format)


    def _writeParsedDataToItems(self,data:dict,items:dict,header:dict, datetime_format:str=miqtv.date_formats['mariqt']):

        # eval strings as dict or list
        miqtc.recursiveEval(data)

        data = miqtc.recursivelyRemoveEmptyFields(data,content2beRemoved=None)

        # potentailly remove const data from items and put in header
        self._extractConstDataValues(data,header)

        # add 'image-filename' field
        for img, entry in data.items():

            # list
            if isinstance(entry,list):
                for listItem in entry:
                    # covert datetime string
                    if 'image-datetime' in listItem:
                        dt = datetime.datetime.strptime(listItem['image-datetime'], datetime_format)
                        listItem['image-datetime'] = dt.strftime(miqtv.date_formats['mariqt'])
            elif isinstance(entry,dict):
                # covert datetime string
                if 'image-datetime' in entry:
                    dt = datetime.datetime.strptime(entry['image-datetime'], datetime_format)
                    entry['image-datetime'] = dt.strftime(miqtv.date_formats['mariqt'])
            else:
                raise miqtc.IfdoException("data entries must be dict or list if dicts")

        miqtc.recursivelyUpdateDicts(items,data)


    @staticmethod
    def _extractConstDataValues(data:dict,header:dict):
        """ Removes fields that are constant for all entries from data dict and put them in header dict. 
            Each entry of data must be a dict with the same set of keys. """
    
        # skip if there is only one item
        if len(list(data.keys())) == 1:
            return

        fieldsToIgnore = ['image-datetime']
        constData = {}
        firstImage = True
        for image,image_data in data.items():
            
            if not isinstance(image_data,list):
                image_data = [image_data]

            if not firstImage and constData == {}:
                break
            
            firstTimePoint = True
            for image_tp_data in image_data:
                # very first data for comparison
                if firstImage and firstTimePoint:
                    constData = copy.deepcopy(image_tp_data)
                    for field in fieldsToIgnore:
                        if field in constData:
                            del constData[field]
                    firstTimePoint = False
                    continue

                constData = miqtc.findCommonDictElements(image_tp_data,constData)

            firstImage = False

        # TODO check within image times -> to image default. (tricky since we don't have the dafault index here. Only a subset might be update here)
        # check within image items -> header
        headerUpdate = copy.deepcopy(constData)
        headerUpdatedTest = copy.deepcopy(header)
        miqtc.recursivelyUpdateDicts(headerUpdatedTest,headerUpdate)
        updateDiff = DeepDiff(header,headerUpdatedTest)
        # check if headerUpdate would overwrite anything from current header (should not happen), if so dont remove from items
        if not 'values_changed' in updateDiff and not 'type_changes' in updateDiff and not 'dictionary_item_removed' in updateDiff:
            header.clear()
            header.update(headerUpdatedTest)

            # remove const values from data
            miqtc.recursiveMakeNoneDictFieldsEmptyStr(constData)
            for image,image_data in data.items():
                if not isinstance(image_data,list):
                    image_data = [image_data]
                for image_tp_data in image_data:
                    miqtc.recursivelyUpdateDicts(image_tp_data,constData)          

        else:
            pass
            # TODO log?


    def _updateAndCheck(self, header: dict, items: dict, allow_missing_required=False):
        """ Updates the current values iFDO with the provided new values.
        allow_missing_required: if True, no exception risen if a required ifdo field is missing. """
        return self._createAndCheck(header, items, updateExisting=True, allow_missing_required=allow_missing_required)


    def _createAndCheck(self, header: dict, items: dict, updateExisting=False, allow_missing_required=False):
        """ Creates FAIR digital object for the image data itself. This consists of header information and item information.
        updateExisting: if False old values are removed, otherwise they are updated.
        allow_missing_required: if True, no exception risen if a required ifdo field is missing. 
        """

        if self._ignore_image_files:
            self._prov.log("Caution! iFDO created in ignore_image_file mode. Image items are not checked.")
        else:
            self._checkFilesHaveBeenFoundInDir(items.keys())

        if updateExisting:
            s = miqtc.PrintLoadingMsg("Updating iFDO")
            # header
            self.updateHeaderFields(header)
            # items
            log = miqtc.recursivelyUpdateDicts(self._ifdo_tmp[miqtv.image_set_items_key], items)
            self._prov.log(log)
            s.stop()
        else:
            # overwrite header
            self.setHeaderFields(header)
            # overwrite items
            self._ifdo_tmp[miqtv.image_set_items_key] = {}
            miqtc.recursivelyUpdateDicts(self._ifdo_tmp[miqtv.image_set_items_key], items)

        self._tryFillImageAbstractPlaceholders(self._ifdo_tmp)
        self._setIfdoVersion(self._ifdo_tmp)
        self._setLatLonBoundingBox(self._ifdo_tmp)
        self._trySetRepresentativeHeaderFieldsDtLatLonAlt(self._ifdo_tmp)
        self._setImageItemIdentificationScheme(self._ifdo_tmp)
        self._ifdo_tmp = self._removeEmptyAndDatetimeOnlyFields(self._ifdo_tmp)

        # check ifdo
        if allow_missing_required:
            self._checkIndividualIfdoFieldsAreValid(self._ifdo_tmp)
        else:
            # check whole ifdo against schema
            s = miqtc.PrintLoadingMsg("Checking items")
            valid, msg = miqtt.validateIfdo(self._ifdo_tmp)
            if not valid:
                s.stop()
                self._prov.log("Warning! iFDO no valid yet: " + msg)
                raise miqtc.IfdoException(msg)
            s.stop()

        if not self._ignore_image_files:
            self._checkAllItemHashes(self._ifdo_tmp[miqtv.image_set_items_key])

        # set final one
        self._ifdo_checked = copy.deepcopy(self._ifdo_tmp)
        return self._ifdo_checked


    def _checkFilesHaveBeenFoundInDir(self, file_names:list):
        for file_name in file_names:
                if file_name not in self._imageNamesImagesDir:
                    raise miqtc.IfdoException("Item '" + file_name + "' not found in /raw directory.")


    def _tryFillImageAbstractPlaceholders(self, ifdo:dict):
        try:
            ifdo[miqtv.image_set_header_key]['image-abstract'] = miqts.parseReplaceVal(ifdo[miqtv.image_set_header_key], 'image-abstract')
        except Exception as ex:
            self._prov.log("Could not replace keys in \'image-abstract\': " + str(ex))


    def _setIfdoVersion(self, ifdo:dict):
        ifdo[miqtv.image_set_header_key]['image-set-ifdo-version'] = miqtv.iFDO_version


    def _removeEmptyAndDatetimeOnlyFields(self, ifdo:dict):
        s = miqtc.PrintLoadingMsg("Removing empty fields")
        ifdo = miqtc.recursivelyRemoveEmptyFields(ifdo)

        # if image-set-item was remove because empty re-create it
        if not miqtv.image_set_items_key in ifdo:
            ifdo[miqtv.image_set_items_key] = {}

        # remove fields that contain 'image-datetime' only
        self._removeItemFieldsWithOnlyDatetime(ifdo)
        s.stop()
        return ifdo


    def _removeItemFieldsWithOnlyDatetime(self, ifdo:dict):
        """ it can happen that an image timestamp does not contain any fields but the timestamp any more. Those are removed here. """ 
        for item in ifdo[miqtv.image_set_items_key]:
            if isinstance(ifdo[miqtv.image_set_items_key][item],list):

                toBeRemoved = []

                for entry in ifdo[miqtv.image_set_items_key][item]:
                    if len(entry) == 1 and 'image-datetime' in entry:
                        toBeRemoved.append(entry)
                for entry in toBeRemoved:
                    ifdo[miqtv.image_set_items_key][item].remove(entry) 


    def _setImageItemIdentificationScheme(self,ifdo:dict):
        """ Set image-item-identification-scheme to `image-project_image-event_image-sensor_image-datetime.ext` if empty. """
        if iFDO._findPlainValue(ifdo[miqtv.image_set_header_key],'image-item-identification-scheme') == "":
            ifdo[miqtv.image_set_header_key]['image-item-identification-scheme'] =  'image-project_image-event_image-sensor_image-datetime.ext'


    def _trySetRepresentativeHeaderFieldsDtLatLonAlt(self,ifdo:dict):
        """ Fill header fields image-datetime and -latitude, -longituede, -altitude-meters, -coordinate-uncertainty-meters, if empty,
        representatively with first items entry and median of all items values, respectively. """

        # 'image-datetime'
        field = 'image-datetime'
        if iFDO._findPlainValue(ifdo[miqtv.image_set_header_key],field) == "":
            try:
                images_sorted = sorted(ifdo[miqtv.image_set_items_key].keys())
                if len(images_sorted) == 0:
                    raise miqtc.IfdoException("No items")
                first_image = images_sorted[0]
                ifdo[miqtv.image_set_header_key][field] = self._getValue(ifdo,[first_image,field],default_only=True)
                self._prov.log("Set representative header field '" + field + "' to " + str(ifdo[miqtv.image_set_header_key][field]) + " from first image.")
            except miqtc.IfdoException as ex:
                self._prov.log("Could not set representative header field: " + str(ex))
                pass

        # rest
        rep_header_fields_median = ['image-latitude','image-longitude','image-altitude-meters','image-coordinate-uncertainty-meters']
        for field in rep_header_fields_median:
            if iFDO._findPlainValue(ifdo[miqtv.image_set_header_key],field) == "":
                values = []
                for image_name in ifdo[miqtv.image_set_items_key].keys():
                    try:
                        item_val = self._getValue(ifdo,[image_name,field])
                        if isinstance(item_val,dict):
                            values += list(item_val.values())
                        else:
                            values.append(item_val)
                    except miqtc.IfdoException as ex:
                        pass
                values = [i for i in values if i != '']
                if len(values) == 0:
                    self._prov.log("Could not set representative header field, no values found: " + field)
                else:
                    # ignore unknonw, i.e. 0.0, values
                    values = [i for i in values if i != 0.0]
                    if len(values) == 0:
                        values.append(0.0) 
                    ifdo[miqtv.image_set_header_key][field] = statistics.median(values)
                    self._prov.log("Set representative header field '" + field + "' to median: " + str(ifdo[miqtv.image_set_header_key][field]) + ".")


    def _setLatLonBoundingBox(self,ifdo:dict):
        """ Set image-set-[min,max]-[latitude,longitude]-degrees """
        lat_min, lat_max, lon_min, lon_max = self._getLatLonBoundingBox(ifdo[miqtv.image_set_items_key])
        if not None in [lat_min, lat_max, lon_min, lon_max]:
            ifdo[miqtv.image_set_header_key]['image-set-min-latitude-degrees'] = lat_min
            ifdo[miqtv.image_set_header_key]['image-set-max-latitude-degrees'] = lat_max
            ifdo[miqtv.image_set_header_key]['image-set-min-longitude-degrees'] = lon_min
            ifdo[miqtv.image_set_header_key]['image-set-max-longitude-degrees'] = lon_max


    def _checkIndividualIfdoFieldsAreValid(self, ifdo:dict):
        """ Checks if exisiting ifdo field are valid. Does not check for requried ifdo fields """
        # check existing fields agianst schema
        # check header
        try:
            miqtt.areValidIfdoFields(ifdo[miqtv.image_set_header_key])
        except miqtc.IfdoException as ex:
            msg = "Invalid header field: " + str(ex)
            self._prov.log("Exception: " + msg, dontShow=True)
            raise miqtc.IfdoException(msg)
        
        # check items
        prog = miqtc.PrintKnownProgressMsg("Checking items", len(ifdo[miqtv.image_set_items_key]),modulo=1)
        for file_name, file_data in ifdo[miqtv.image_set_items_key].items():
            prog.progress()
            try:
                
                file_data_list = file_data
                if isinstance(file_data_list, dict): # photo
                    file_data_list = [file_data_list]
                for time_stamp_data in file_data_list:
                    miqtt.areValidIfdoFields(time_stamp_data)

            except miqtc.IfdoException as e:
                self._prov.log("Invalid image item: "+ str(file_name),dontShow=True)
                self._prov.log("Exception:\n"+ str(e.args),dontShow=True)
                raise miqtc.IfdoException("Invalid image item "+ file_name + ":\nException:\n"+ str(e.args)) # otherwise, in case of many images, it may keep running and throwing errors for quit some time
        prog.clear()


    @staticmethod
    def _getLatLonBoundingBox(items:dict):
        """ Returns lat_min, lat_max, lon_min, lon_max """
        lat_min, lat_max, lon_min, lon_max = None, None, None, None
        i = 0
        for image, data in items.items():
            # make image entry list (also if its a picture)
            if not isinstance(data, list):
                data = [data]
            
            for timepoint_data in data:
                try:
                    lat = timepoint_data['image-latitude']
                    lon = timepoint_data['image-longitude']
                except KeyError as ex:
                    continue

                if i == 0:
                    lat_min, lat_max = lat, lat
                    lon_min, lon_max = lon, lon
                else:
                    if lat < lat_min:
                        lat_min = lat
                    if lat > lat_max:
                        lat_max = lat
                    if lon < lon_min:
                        lon_min = lon
                    if lon > lon_max:
                        lon_max = lon
                i += 1
        return lat_min, lat_max, lon_min, lon_max


    def _checkAllItemHashes(self, items:dict, hard=False, raiseException = True):
        """ 
        Checks if hashes in iFDO match hashes in intermeidate hash file if the latter was changed last after the images has changed.
        Otherwise or if hard==True it redetermines the actuall file's hash and compares the iFDO item's hash with that.
        If hashes do not match a mariqt.core.IfdoException is risen unsless raiseException == False, then a list of lists [<file>,<exception>] is returned.
        """
        hashes = {}
        hashFileModTime = 10e+100
        if os.path.exists(self._getIntHashFile()):
            hashes = miqtf.tabFileData(self._getIntHashFile(), [miqtv.col_header['mariqt']['img'], miqtv.col_header['mariqt']['hash']], key_col=miqtv.col_header['mariqt']['img'])
            hashFileModTime = os.path.getmtime(self._getIntHashFile())

        exceptionList = []

        hashUncheckImagesInRaw = self._getImagesInImagesDir()
        prog = miqtc.PrintKnownProgressMsg("Checking item hashes", len(items))
        for item_name in items:
            prog.progress()

            found = False
            for image in hashUncheckImagesInRaw:
                fileName = os.path.basename(image)
                if fileName == item_name:
                    found = True
                    if isinstance(items[item_name],list): # in case of video with item as list the first entry holds the default and the hash cannot vary for the same image
                        itemEntry = items[item_name][0] 
                    else:
                        itemEntry = items[item_name]

                    imageModTime = os.path.getmtime(image)
                    if not hard and imageModTime < hashFileModTime:
                        if not os.path.basename(image) in hashes:
                            if raiseException:
                                raise miqtc.IfdoException(item_name, "not found in intermeidate hash file",self._getIntHashFile()," run create_image_sha256_file() first") 
                            else:
                                exceptionList.append([fileName,"not found in intermeidate hash file " + str(self._getIntHashFile())])
                        if not itemEntry['image-hash-sha256'] == hashes[os.path.basename(image)]['image-hash-sha256']:
                            if raiseException:
                                raise miqtc.IfdoException(item_name, "incorrect sha256 hash", itemEntry['image-hash-sha256'],"for file",fileName," run create_image_sha256_file() first")
                            else:
                                exceptionList.append([fileName,"incorrect sha256 hash"])
                    elif not itemEntry['image-hash-sha256'] == miqtc.sha256HashFile(image):
                        if raiseException:
                            raise miqtc.IfdoException(item_name, "incorrect sha256 hash", itemEntry['image-hash-sha256'],"for file",fileName," run create_image_sha256_file() first")
                        else:
                            exceptionList.append([fileName,"incorrect sha256 hash"])
                    break
            if found:
                del hashUncheckImagesInRaw[image]
            else:
                if raiseException:
                    raise miqtc.IfdoException( "image", item_name, "not found in directory's raw folder!")
                else:
                    exceptionList.append([fileName,"file not found"])
        prog.clear()
        if not raiseException:
            return exceptionList


    def createStartTimeFile(self):
        """ Creates in /intermediate a text file containing per image its start time parsed from the file name """
        self._dir.createTypeFolder([self._dir.dt.intermediate.name])
        s = miqtc.PrintLoadingMsg("Creating intermediate start time file ")
        imagesInRaw = self._getImagesInImagesDirSortedList()
        if len(imagesInRaw) > 0:

            o = open(self.get_int_startTimes_file(), "w")
            o.write(miqtv.col_header['mariqt']['img'] +
                    "\t"+miqtv.col_header['mariqt']['utc']+"\n")

            for file in imagesInRaw:
                file_name = os.path.basename(file)

                dt = miqtc.parseFileDateTimeAsUTC(file_name)
                o.write(file_name+"\t" + dt.strftime(miqtv.date_formats['mariqt'])+"\n")

            o.close()
            s.stop()
            return "Created start time file"
        else:
            s.stop()
            raise miqtc.IfdoException("No images found to read start times")
        

    def createUuidFile(self,clean=True):
        """ Creates in /intermediate a text file containing per image a created uuid (version 4).

        The UUID is only *taken* from the metadata of the images. It does not write UUIDs to the metadata in case some files are missing it.
        But, it creates a CSV file in that case that you can use together with exiftool to add the UUID to your data. Beware! this can destroy your images
        if not done properly! No guarantee is given it will work. Be careful!

        Use clean=False to not check those files again which are already found in intermediate uuid file
        """
        if miqtv.getGlobalVerbose():
            print("Creating UUID file ...")
        self._dir.createTypeFolder([self._dir.dt.intermediate.name])
        uuids = {}
        # Check whether a file with UUIDs exists, then read it
        if not clean and os.path.exists(self._getIntUuidFile()):
            uuids = miqtf.tabFileData(self._getIntUuidFile(), [miqtv.col_header['mariqt']['img'], miqtv.col_header['mariqt']['uuid']], key_col=miqtv.col_header['mariqt']['img'])
            
        if os.path.exists(self._images_dir):

            missing_uuids = {}
            added_uuids = 0

            unknownFiles = []
            for file in self._getImagesInImagesDir():
                file_name = os.path.basename(file)
                if file_name not in uuids:
                    unknownFiles.append(file)
                else:
                    uuids[file_name] = uuids[file_name][miqtv.col_header['mariqt']['uuid']]

            unknownFilesUUIDs = miqti.imagesContainValidUUID(unknownFiles)
            for file in unknownFilesUUIDs:
                file_name = os.path.basename(file)
                if not unknownFilesUUIDs[file]['valid']:
                    uuid = miqtc.uuid4()
                    missing_uuids[file] = uuid
                else:
                    uuids[file_name] = unknownFilesUUIDs[file]['uuid']
                    added_uuids += 1

            # If previously unknown UUIDs were found in the file headers, add them to the UUID file
            if added_uuids > 0:
                res = open(self._getIntUuidFile(), "w")
                res.write(miqtv.col_header['mariqt']['img'] +"\t"+miqtv.col_header['mariqt']['uuid']+"\n")
                files_sorted = list(uuids.keys())
                files_sorted.sort()
                for file in files_sorted:
                    res.write(file+"\t"+str(uuids[file])+"\n")
                res.close()

            if len(missing_uuids) > 0:
                ecsv_path = self._getIntFilePrefix() + "_exif-add-uuid.csv"
                csv = open(ecsv_path, "w")
                csv.write(miqtv.col_header['exif']['img'] +
                          ","+miqtv.col_header['exif']['uuid']+"\n")
                different_paths = []
                for img in missing_uuids:
                    if os.path.basename(img) not in different_paths:
                        different_paths.append(os.path.basename(img))
                    csv.write(img+","+str(missing_uuids[img])+"\n")
                #return False, "exiftool -csv="+ecsv_path+" "+" ".join(different_paths)
                raise miqtc.IfdoException("Not all images have valid UUIDs. Missing for following files:\n" + '\n'.join(different_paths))
            
            self._all_uuids_checked = True
            return "All images have a UUID"
        raise miqtc.IfdoException("Path "+self._images_dir + " not found.")


    def createImageSha256File(self,reReadAll=True):
        """ Creates in /intermediate a text file containing per image its SHA256 hash.
            If reReadAll is True all images' hashes are determined. Otherwise only for those files
            which are not yet in the intermediate file containing the image hashes  """
        if miqtv.getGlobalVerbose():
            print("Creating intermediate hash file ...")
        self._dir.createTypeFolder([self._dir.dt.intermediate.name])
        hashes = {}
        if os.path.exists(self._getIntHashFile()):
            hashes = miqtf.tabFileData(self._getIntHashFile(), [miqtv.col_header['mariqt']['img'], miqtv.col_header['mariqt']['hash']], key_col=miqtv.col_header['mariqt']['img'])
            msg_0 = "Loaded " + str(len(hashes)) + " hahes from " + os.path.basename(self._getIntHashFile())
            msg_reRedaAll = msg_0 + " - but re-calculating all hashes anyway"
            msg_not_reRedaAll = msg_0 + " - calculating only missing hashes"
            if reReadAll:
                self._prov.log(msg_reRedaAll)
            else:
                self._prov.log(msg_not_reRedaAll)

        imagesInRaw = self._getImagesInImagesDir()
        if len(imagesInRaw) > 0:

            added_hashes = 0
            if self._all_uuids_checked:
                prog = miqtc.PrintKnownProgressMsg("Checking hashes", len(imagesInRaw),modulo=1)
            else:
                prog = miqtc.PrintKnownProgressMsg("Checking uuids and hashes", len(imagesInRaw),modulo=1)
            for file in imagesInRaw:
                prog.progress()

                if not self._all_uuids_checked and not miqti.imageContainsValidUUID(file)[0]:
                    # remove from uuid file
                    if os.path.exists(self._getIntUuidFile()):
                        res = open(self._getIntUuidFile(), "r")
                        lines = res.readlines()
                        res.close()
                    else:
                        lines = []
                    i = 0
                    lineNr = i
                    for line in lines:
                        if os.path.basename(file) in line:
                            lineNr = i
                            break
                        i += 1
                    if lineNr != 0:
                        del lines[lineNr]
                        res = open(self._getIntUuidFile(), "w")
                        res.writelines(lines)
                        res.close()
                    raise Exception( "File " + file + " does not cotain a valid UUID. A a UUID first!")

                file_name = os.path.basename(file)
                if not reReadAll and file_name in hashes:
                    hashes[file_name] = hashes[file_name][miqtv.col_header['mariqt']['hash']]
                else:
                    hashes[file_name] = miqtc.sha256HashFile(file)
                    added_hashes += 1
            prog.clear()

            if reReadAll or added_hashes > 0:
                hash_file = open(self._getIntHashFile(), "w")
                hash_file.write( miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['hash']+"\n")
                files_sorted = list(hashes.keys())
                files_sorted.sort()
                for file_name in files_sorted:
                    hash_file.write(file_name+"\t"+hashes[file_name]+"\n")

                hash_file.close()
                return "Added "+str(added_hashes)+" hashes to hash file"
            else:
                return "All hashes exist"

        else:
            raise miqtc.IfdoException("No images found to hash")


    def createImageNavigationFile(self, nav_path: str, nav_header=miqtv.pos_header['pangaea'], date_format=miqtv.date_formats['pangaea'], 
                                  overwrite=False, col_separator = "\t", video_sample_seconds=1,
                                  offset_x=0, offset_y=0, offset_z=0,angles_in_rad = False, records_to_be_inverted=[]):
        """ Creates in /intermediate a text file with 4.5D navigation data for each image, i.e. a single row per photo, video duration [sec] / videoSampleSeconds rows per video.
            nav_header must be dict containing the keys 'utc','lat','lon','dep'(or 'alt'), optional: 'hgt','uncert' with the respective column headers as values 
            if one of the vehicle x,y,z offsets [m] is not 0 and nav_header also contains 'yaw','pitch','roll' leverarm offsets are compensated for """
        
        self._dir.createTypeFolder([self._dir.dt.intermediate.name])

        if self.intermediateNavFileExists() and not overwrite:
            return "Output file exists: " + self._getIntNavFile()

        if not os.path.exists(nav_path):
            raise miqtc.IfdoException("Navigation file not found: " + nav_path)

        if not os.path.exists(self._images_dir):
            raise miqtc.IfdoException("Image folder not found: " + self._images_dir)

        miqtc.printStaticLoadingMsg("Creating items' navigation data")
        returnMsg = ""
        compensatOffsets = False
        if (offset_x!=0 or offset_y!=0 or offset_z!=0) and 'yaw' in nav_header and 'pitch' in nav_header and 'roll' in nav_header:
            compensatOffsets = True

        # check if for missing fields there are const values in header
        const_values = {}
        for navField in miqtv.pos_header['mariqt']:
            respectiveHeaderField = miqtv.col_header["mariqt"][navField]
            if navField not in nav_header and (respectiveHeaderField in self._ifdo_tmp[miqtv.image_set_header_key] and self.findUncheckedValue(respectiveHeaderField) != ""): 
                const_values[navField] = self.getUncheckedValue(respectiveHeaderField)

         # handle alt vs dep
        if 'alt' in nav_header and 'dep' in nav_header:
            raise miqtc.IfdoException("'alt' and 'dep' provided. Redundant, alt = - dep. Provided only one of both.")
        
        # Load navigation data (if 'alt' instead of 'dep', its automatically inverted)
        nav_data, parseMsg = miqtn.readAllPositionsFromFilePath(nav_path, nav_header, date_format,col_separator=col_separator,const_values=const_values)
        if parseMsg != "":
            self._prov.log(parseMsg,dontShow=True)
            returnMsg = "\n" + parseMsg

        # find for each image the respective navigation data
        success, image_dts, msg = self._findNavDataForImage(nav_data,video_sample_seconds)
        self._prov.log(msg,dontShow=True)
        if msg != "":
            returnMsg += "\n" + msg
        if not success:
            raise miqtc.IfdoException(returnMsg)

        # invert values (if needed) before leverarm compensation
        if records_to_be_inverted != []:
            for file in image_dts:
                positions = image_dts[file]
                for i in range(len(positions)):
                    if 'lat' in records_to_be_inverted:
                        positions[i].lat *= -1
                    if 'lon' in records_to_be_inverted:
                        positions[i].lon *= -1
                    if ('dep' in records_to_be_inverted and 'dep' in nav_header) or ('alt' in records_to_be_inverted and 'alt' in nav_header):
                        positions[i].dep *= -1
                    if 'hgt' in records_to_be_inverted:
                        positions[i].hgt *= -1


        # compensate leverarm offsets
        if compensatOffsets:

            # load frame attitude data from file
            att_data, parseMsg = miqtn.readAllAttitudesFromFilePath(nav_path, nav_header, date_format,col_separator=col_separator,const_values=const_values,anglesInRad=angles_in_rad)
            if parseMsg != "":
                self._prov.log(parseMsg,dontShow=True)
                returnMsg += "\n" + parseMsg

            if records_to_be_inverted != []:
                for file in image_dts:
                    attitudes = image_dts_att[file]
                    for i in range(len(positions)):
                        if 'yaw' in  records_to_be_inverted:
                            attitudes[i].yaw *= -1
                        if 'pitch' in  records_to_be_inverted:
                            attitudes[i].pitch *= -1
                        if 'roll' in  records_to_be_inverted:
                            attitudes[i].roll *= -1

            # find for each image the respective navigation data
            success, image_dts_att, msg = self._findNavDataForImage(att_data,video_sample_seconds)
            self._prov.log(msg,dontShow=True)
            if msg != "":
                returnMsg += "\n" + msg
            if not success:
                raise miqtc.IfdoException(returnMsg)

            # compensate
            for file in image_dts:
                positions = image_dts[file]
                attitudes = image_dts_att[file]
                for i in range(len(positions)):
                    lat = positions[i].lat
                    lon = positions[i].lon
                    dep = positions[i].dep
                    hgt = positions[i].hgt
                    yaw = attitudes[i].yaw
                    pitch = attitudes[i].pitch
                    roll = attitudes[i].roll
                    if yaw is None or pitch is None or roll is None:
                        continue
                    new_lat,new_lon,new_dep,new_hgt = miqtg.addLeverarms2LatLonDepAlt(lat,lon,dep,hgt,offset_x,offset_y,offset_z,yaw,pitch,roll)
                    positions[i].lat = new_lat
                    positions[i].lon = new_lon
                    positions[i].dep = new_dep
                    positions[i].hgt = new_hgt

            self._prov.log("applied lever arm compensation x,y,z = " + str(offset_x) + "," + str(offset_y) + "," + str(offset_z),dontShow=True)

        if len(image_dts) > 0:
            # Check whether depth and height are set
            lat_identical, lon_identical, dep_identical, hgt_identical, dep_not_zero, hgt_not_zero,uncert_not_zero = nav_data.checkPositionsContent()

            # Write to navigation txt file
            # header
            res = open(self._getIntNavFile(), "w")
            res.write(miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['utc'])

            has_alt = True if dep_not_zero and ( 'dep' in nav_header or 'alt' in nav_header ) else False

            if 'lat' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['lat'])
            if 'lon' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['lon'])
            if has_alt:
                res.write("\t"+miqtv.col_header['mariqt']['alt'])
            if hgt_not_zero and 'hgt' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['hgt'])
            if uncert_not_zero and 'uncert' in nav_header:
                res.write("\t"+miqtv.col_header['mariqt']['uncert'])
            res.write("\n")
            # data lines
            for file in image_dts:
                for timepoint in image_dts[file]:
                    res.write(file+"\t"+timepoint.dateTime().strftime(miqtv.date_formats['mariqt']))
                    if 'lat' in nav_header:
                        iFDO._writeToStreamAndRoundIfFloat(res, timepoint.lat, separator="\t", float_decimals=8)
                    if 'lon' in nav_header:
                        iFDO._writeToStreamAndRoundIfFloat(res, timepoint.lon, separator="\t", float_decimals=8)
                    if has_alt:
                        val = timepoint.dep
                        # dep to alt
                        val *= -1
                        iFDO._writeToStreamAndRoundIfFloat(res, val, separator="\t", float_decimals=8)
                    if hgt_not_zero and 'hgt' in nav_header:
                        iFDO._writeToStreamAndRoundIfFloat(res, timepoint.hgt, separator="\t", float_decimals=8)
                    if uncert_not_zero and 'uncert' in nav_header:
                        iFDO._writeToStreamAndRoundIfFloat(res, timepoint.uncert, separator="\t", float_decimals=8)
                    res.write("\n")
            res.close()

            # Write to geojson file
            geojson = {'type': 'FeatureCollection', 'name': self._dir.event()+"_"+self._dir.sensor()+"_image-navigation", 'features': []}
            for file in image_dts:
                # photo
                if len(image_dts[file]) == 1:
                    try:
                        geojson_feature = image_dts[file][0].toGeoJsonPointFeature(id=file, include_depth=dep_not_zero)
                        geojson['features'].append(geojson_feature)
                    except ValueError:
                        pass

                # video
                else:
                    geojson_feature = miqtg.positionsToGeoJsonMultiPointFeature(image_dts[file], id=file, include_depth=dep_not_zero)
                    geojson['features'].append(geojson_feature)
                
            o = open(self._getIntNavFile().replace(".txt", ".geojson"),
                     "w", errors="ignore", encoding='utf-8')
            geojson_rounded = miqtc.roundFloats(geojson, decimals=8)
            json.dump(geojson_rounded, o, ensure_ascii=False, indent=4)
            o.close()

            self._prov.addArgument("inputNavigationFile", self._dir.getRelativePathToProjectsBaseDir(nav_path) , overwrite=True)
            self._prov.log("parsed from inputNavigationFile: " + str(nav_header),dontShow=True)
            return "Navigation data created" + returnMsg
        else:
            raise miqtc.IfdoException("No image coordinates found" + returnMsg)


    @staticmethod
    def _writeToStreamAndRoundIfFloat(stream:io.StringIO, value, separator="\t",float_decimals:int=8):
        if isinstance(value, float):
            value = round(value, float_decimals)
            stream.write(separator + str(value))


    def intermediateNavFileExists(self):
        if os.path.exists(self._getIntNavFile()):
            return True
        else:
            return False


    def setImageSetAttitude(self,yaw_frame:float,pitch_frame:float,roll_frame:float,yaw_cam2frame:float,pitch_cam2frame:float,roll_cam2frame:float):
        """ calculates the the cameras absolute attitude and sets it to image set header. All angles are expected in degrees. 
        camera2frame angles: rotation of camera coordinates (x,y,z = top, right, line of sight) with respect to vehicle coordinates (x,y,z = forward,right,down) 
        in accordance with the yaw,pitch,roll rotation order convention:

        1. yaw around z,
        2. pitch around rotated y,
        3. roll around rotated x

        Rotation directions according to \'right-hand rule\'.

        I.e. camera2Frame angles = 0,0,0 camera is facing downward with top side towards vehicle's forward direction' """

        R_frame2ned = miqtg.R_YawPitchRoll(yaw_frame,pitch_frame,roll_frame)
        R_cam2frame = miqtg.R_YawPitchRoll(yaw_cam2frame,pitch_cam2frame,roll_cam2frame)
        R_cam2ned = R_frame2ned.dot(R_cam2frame)
        yaw,pitch,roll = miqtg.yawPitchRoll(R_cam2ned)

        # pose matrix cam2utm
        R_camStd2utm = self._getRcamStd2utm(R_cam2frame,R_frame2ned)

        """
        x = np.array([1,0,0])
        y = np.array([0,1,0])
        z = np.array([0,0,1])
        print('x',R_camStd2utm.dot(x).round(5))
        print('y',R_camStd2utm.dot(y).round(5))
        print('z',R_camStd2utm.dot(z).round(5))
        """

        headerUpdate = {
            miqtv.col_header['mariqt']['yaw']:yaw,
            miqtv.col_header['mariqt']['pitch']:pitch,
            miqtv.col_header['mariqt']['roll']:roll,
            miqtv.col_header['mariqt']['pose']:{'pose-absolute-orientation-utm-matrix':R_camStd2utm.flatten().tolist()}
        }
        self.updateHeaderFields(headerUpdate)


    def createImageAttitudeFile(self, att_path:str, frame_att_header:dict, camera2Frame_yaw:float,camera2Frame_pitch:float,camera2Frame_roll:float,
                                date_format=miqtv.date_formats['pangaea'], const_values = {}, overwrite=False, col_separator = "\t",
                                att_path_angles_in_rad = False, video_sample_seconds=1,records_to_be_inverted=[]):
        """ Creates in /intermediate a text file with camera attitude data for each image. All angles are expected in degrees. Use att_path_angles_in_rad if necessary. 
        camera2Frame angles: rotation of camera coordinates (x,y,z = top, right, line of sight) with respect to vehicle coordinates (x,y,z = forward,right,down) 
        in accordance with the yaw,pitch,roll rotation order convention:
        1. yaw around z,
        2. pitch around rotated y,
        3. roll around rotated x

        Rotation directions according to \'right-hand rule\'.

        I.e. camera2Frame angles = 0,0,0 camera is facing downward with top side towards vehicle's forward direction' """

        int_attutude_file = self._getIntFilePrefix() + '_image-attitude.txt'
        output_header_att = {   miqtv.col_header['mariqt']['img']:  miqtv.col_header['mariqt']['img'],
                                miqtv.col_header['mariqt']['utc']:miqtv.col_header['mariqt']['utc'],
                                miqtv.col_header['mariqt']['yaw']:miqtv.col_header['mariqt']['yaw'],
                                miqtv.col_header['mariqt']['pitch']:miqtv.col_header['mariqt']['pitch'],
                                miqtv.col_header['mariqt']['roll']:miqtv.col_header['mariqt']['roll'],
                            }

        int_pose_file = self._getIntFilePrefix() + '_image-camera-pose.txt'
        output_header_pose = {  miqtv.col_header['mariqt']['img']:miqtv.col_header['mariqt']['img'],
                                miqtv.col_header['mariqt']['utc']:miqtv.col_header['mariqt']['utc'],
                                miqtv.col_header['mariqt']['pose']:miqtv.col_header['mariqt']['pose'],
                            }

        if os.path.exists(int_attutude_file) and not overwrite:
            self.addItemInfoTabFile(int_attutude_file,"\t",output_header_att)
            extra_msg = ""
            if os.path.exists(int_pose_file):
                self.addItemInfoTabFile(int_pose_file,"\t",output_header_pose)
                extra_msg = ", " + int_pose_file
            return "Output file exists: "+int_attutude_file + extra_msg

        if not os.path.exists(att_path):
            raise miqtc.IfdoException("Attitude file not found: "+att_path)

        if not os.path.exists(self._images_dir):
            raise miqtc.IfdoException("Image folder not found: "+ self._images_dir)

        miqtc.printStaticLoadingMsg("Creating items' attitude data")

        # load frame attitude data from file
        att_data, parseMsg = miqtn.readAllAttitudesFromFilePath(att_path, frame_att_header, date_format,col_separator=col_separator,const_values=const_values,anglesInRad=att_path_angles_in_rad)
        if parseMsg != "":
            self._prov.log(parseMsg,dontShow=True)
            parseMsg = "\n" + parseMsg

        # find for each image the respective navigation data
        success, image_dts, msg = self._findNavDataForImage(att_data,video_sample_seconds)
        if not success:
            raise miqtc.IfdoException(msg + parseMsg)

        # invert values (if needed) before leverarm compensation
        if records_to_be_inverted != []:
            for file in image_dts:
                attitudes = image_dts[file]
                for i in range(len(attitudes)):
                    if 'yaw' in  records_to_be_inverted:
                        attitudes[i].yaw *= -1
                    if 'pitch' in  records_to_be_inverted:
                        attitudes[i].pitch *= -1
                    if 'roll' in  records_to_be_inverted:
                        attitudes[i].roll *= -1


        # add camera2Frame angles
        R_cam2frame = miqtg.R_YawPitchRoll(camera2Frame_yaw,camera2Frame_pitch,camera2Frame_roll)
        R_cam2utm_list = []
        for file in image_dts:
            for timepoint in image_dts[file]:
                attitude = timepoint
                if attitude.yaw is None or attitude.pitch is None or attitude.roll is None:
                    R_cam2utm_list.append("")
                    continue
                R_frame2ned = miqtg.R_YawPitchRoll(attitude.yaw,attitude.pitch,attitude.roll)
                R_cam2ned = R_frame2ned.dot(R_cam2frame)
                yaw,pitch,roll = miqtg.yawPitchRoll(R_cam2ned)
                attitude.yaw = yaw
                attitude.pitch = pitch
                attitude.roll = roll

                R_camStd2utm = self._getRcamStd2utm(R_cam2frame,R_frame2ned)
                R_cam2utm_list.append(R_camStd2utm.flatten().tolist())

        self._prov.log("applied frame to camera rotation yaw,pitch,roll = " + str(camera2Frame_yaw) + "," + str(camera2Frame_pitch) + "," + str(camera2Frame_roll),dontShow=True)

        if len(image_dts) > 0:

            # Write to navigation txt file
            # header
            res = open(int_attutude_file, "w")
            res.write(miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['utc'])
            res.write("\t"+miqtv.col_header['mariqt']['yaw'])
            res.write("\t"+miqtv.col_header['mariqt']['pitch'])
            res.write("\t"+miqtv.col_header['mariqt']['roll'])

            res.write("\n")
            # data lines
            for file in image_dts:
                for timepoint in image_dts[file]:
                    res.write(file+"\t"+timepoint.dateTime().strftime(miqtv.date_formats['mariqt'])) 
                    iFDO._writeToStreamAndRoundIfFloat(res, timepoint.yaw, separator="\t", float_decimals=8)
                    iFDO._writeToStreamAndRoundIfFloat(res, timepoint.pitch, separator="\t", float_decimals=8)
                    iFDO._writeToStreamAndRoundIfFloat(res, timepoint.roll, separator="\t", float_decimals=8)
                    res.write("\n")
            res.close()

            self._prov.addArgument("inputAttitudeFile",self._dir.getRelativePathToProjectsBaseDir(att_path), overwrite=True)
            self._prov.log("parsed from inputAttitudeFile: " + str(frame_att_header),dontShow=True)
            self.addItemInfoTabFile(int_attutude_file,"\t",output_header_att)

            # Write to pose txt file
            # header
            res = open(int_pose_file, "w")
            res.write(miqtv.col_header['mariqt']['img']+"\t"+miqtv.col_header['mariqt']['utc'])
            res.write("\t"+miqtv.col_header['mariqt']['pose'])
            res.write("\n")
            # data lines
            i = 0
            for file in image_dts:
                for timepoint in image_dts[file]:
                    if R_cam2utm_list[i] == "":
                        i += 1
                        continue
                    res.write(file+"\t"+timepoint.dateTime().strftime(miqtv.date_formats['mariqt'])) 
                    entry = str({'pose-absolute-orientation-utm-matrix':R_cam2utm_list[i]}).replace('\n','')
                    res.write("\t"+entry)
                    i += 1
                    res.write("\n")
            res.close()
            self.addItemInfoTabFile(int_pose_file,"\t",output_header_pose)
            return "Attitude data created" + parseMsg
        else:
            raise miqtc.IfdoException("No image attitudes found" + parseMsg)
        

    def _getRcamStd2utm(self, R_cam2frame:np.array, R_frame2ned:np.array):
        """ return rotation matrix R tranforming from camStd: (x,y,z = right,buttom,line of sight) to utm (x,y,z = easting,northing,up) """
        R_camiFDO2camStd = miqtg.R_YawPitchRoll(90,0,0) # in iFDO cam: (x,y,z = top,right,line of sight) but for pose the 'standard' camStd: (x,y,z = right,buttom,line of sight) is expected
        R_camStd2frame = R_cam2frame.dot(R_camiFDO2camStd)
        R_camStd2ned = R_frame2ned.dot(R_camStd2frame)
        R_ned2utm = miqtg.R_XYZ(180,0,90) # with utm x,y,z = easting,northing,up
        R_camStd2utm = R_ned2utm.dot(R_camStd2ned).round(5)
        return R_camStd2utm


    def _findNavDataForImage(self,data:miqtg.NumDataTimeStamped,videoSampleSeconds=1):
        """ creates a dict (image_dts) with file name as key and a list of data elements as value. 
            In case of photos the list has only a single entry, for videos it has video duration [sec] / videoSampleSeconds entries.
            Returns success, image_dts, msg """

        if videoSampleSeconds <= 0:
            raise Exception("findNavDataForImage: videoSampleSeconds must be greater 0")

        # create sorted time points
        time_points = list(data.keys())
        time_points.sort()
        unmatchedTimePoints = []
        image_dts = {}
        startSearchIndex = 0
        imagesInRaw =  self._getImagesInImagesDir()
        imagesInRawSortedList = self._getImagesInImagesDirSortedList()
        prog = miqtc.PrintKnownProgressMsg("Interpolating navigation for image", len(imagesInRaw),modulo=1)
        for file in imagesInRawSortedList:
            prog.progress()
            file_name = os.path.basename(file)

            dt_image = miqtc.parseFileDateTimeAsUTC(file_name)
            dt_image_ts = int(dt_image.timestamp() * 1000)

            runTime = imagesInRaw[file][1] # -1 for photos
            # video
            if imagesInRaw[file][2] in miqtv.video_types and runTime <= 0: # ext
                print("Caution! Could not read video run time from file",file) # TODO does this happen? Handle better?

            sampleTimeSecs = 0
            pos_list = []
            go = True
            while go:
                try:                    
                    pos, startSearchIndex = data.interpolateAtTime(dt_image_ts + sampleTimeSecs * 1000,time_points,startSearchIndex)
                    
                    # interpolateAtTime returns None values if time out of range
                    if pos.cotainsNoneValuesInRequiredFields():
                        unmatchedTimePoints.append((dt_image_ts + sampleTimeSecs * 1000)/1000)
                    else:
                        pos_list.append(pos)
                except Exception as e:
                    return False, image_dts, "Could not find image time "+ datetime.datetime.utcfromtimestamp((dt_image_ts + sampleTimeSecs * 1000)/1000).strftime(miqtv.date_formats['mariqt']) +" in "+str(data.len())+" data positions" + str(e.args)
                sampleTimeSecs += videoSampleSeconds
                if sampleTimeSecs > runTime:
                    go = False
            
            image_dts[file_name] = pos_list
        prog.clear()
        returnMsg = ""
        if len(unmatchedTimePoints) != 0:
            unmatchedTimePoints.sort()
            unmatchedTimePoints = [datetime.datetime.utcfromtimestamp(ts).strftime(miqtv.date_formats['mariqt']) for ts in unmatchedTimePoints]
            returnMsg = "Caution! Navigation not found for the following image time points. Double check or provide at least static default navigation in header fields."
            returnMsg += "\n" + "\n".join(unmatchedTimePoints)
        return True, image_dts, returnMsg


    def createAcquisitionSettingsExifFile(self,override=False):
        """ Creates in /intermediate a text file containing per image a dict of exif tags and their values parsed from the image """

        int_acquisitionSetting_file = self._getIntFilePrefix() + '_image-acquisition-settings.txt'
        header = {  miqtv.col_header['mariqt']['img']:  miqtv.col_header['mariqt']['img'],
                    miqtv.col_header['mariqt']['acqui']:miqtv.col_header['mariqt']['acqui']}
        if os.path.exists(int_acquisitionSetting_file) and not override:
            self.addItemInfoTabFile(int_acquisitionSetting_file,"\t",header)
            return "Result file exists"

        imagesInRaw = self._getImagesInImagesDirSortedList()
        if len(imagesInRaw) > 0:

            o = open(int_acquisitionSetting_file, "w")
            o.write(miqtv.col_header['mariqt']['img'] + "\t"+miqtv.col_header['mariqt']['acqui']+"\n")
 
            imagesExifs = miqti.getImagesAllExifValues(imagesInRaw, self._prov, dir=self._dir)
            for file in imagesExifs:
                file_name = os.path.basename(file)
                o.write(file_name+"\t"+str(imagesExifs[file])+"\n")

            o.close()

            self.addItemInfoTabFile(int_acquisitionSetting_file,"\t",header)
            return "Created acquisition settings file"
        else:
            raise miqtc.IfdoException("No images found")


    def addItemInfoTabFile(self, fileName: str, separator:str, header:dict, datetime_format = miqtv.date_formats['mariqt']):
        """ Add a column seperated text file to parse item data from by createFields() or updateFields(). 
        Columns headers will be set as item field names. Must contain column 'image-filename'.
        """
        if fileName == None or not os.path.exists(fileName):
            raise Exception("File",fileName,"not found")

        for field in header:
            if header[field] not in miqtf.tabFileColumnNames(fileName,col_separator=separator):
                raise Exception("Column", header[field], "not in file", fileName)

        if miqtc.assertSlash(os.path.dirname(fileName)) != miqtc.assertSlash(self._dir.to(self._dir.dt.intermediate)):
            self._prov.log( "Caution! It is recommended to put file in the directory's 'intermediate' folder: " + 
                           self._dir.getRelativePathToProjectsBaseDir(fileName))
        ncfiif = NonCoreFieldIntermediateItemInfoFile(fileName, separator, header, datetime_format)
        if ncfiif not in self.nonCoreFieldIntermediateItemInfoFiles: 
            self.nonCoreFieldIntermediateItemInfoFiles.append(ncfiif)


    def removeItemInfoTabFile(self, fileName: str, separator:str, header:dict, datetime_format:str = miqtv.date_formats['mariqt']):
        """ removes file item from list of files to parse item data from by createFields() or updateFields() """
        ncfiif = NonCoreFieldIntermediateItemInfoFile(fileName, separator, header, datetime_format)
        if ncfiif in self.nonCoreFieldIntermediateItemInfoFiles: 
            self.nonCoreFieldIntermediateItemInfoFiles.remove(ncfiif)


    def _getImagesInImagesDir(self):
        return copy.deepcopy(self._images_in_images_dir)


    def _getImagesInImagesDirSortedList(self):
        return copy.deepcopy(self._images_in_images_dir_sorted_list)


    def trySetHeaderEquipmentUriToHandleUrl(self,ifdo_field:str, override:bool = False, ignore_offline:bool = False):
        """ Constructs equipment handle url from ifdo_field['name'] and write it to ifdo_field['uri'].
        Params:
            override: if False set only if uri is empty or does not exist.
            ignore_offline: write to ifdo_field['uri'] even if constructed url is not reachable. """
        if not override and self.findUncheckedValue(ifdo_field+':uri') != "":
            self._prov.log("Caution! " + ifdo_field + ":uri already exists and is not overridden: " + self.findUncheckedValue(ifdo_field+ ':uri'))
            return
        
        eqip_url = self.getEquipmentHandleUrl(self._ifdo_tmp, ifdo_field, self._handle_prefix, self._prov)
        if eqip_url == "":
            return
        try:
            ret = requests.head(eqip_url + '?noredirect', timeout=5) # seems not work without ?noredirect
            if ret.status_code != 200:
                raise Exception()
        except Exception:
            if not ignore_offline:
                self._prov.log("Error! " + ifdo_field + ":uri ignored, not reachable: " + eqip_url)
                return
            else:
                self._prov.log("Caution! " + ifdo_field + ":uri set but not reachable " + eqip_url)

        self._ifdo_tmp[miqtv.image_set_header_key][ifdo_field]['uri'] = eqip_url
        self._prov.log(ifdo_field + ":uri set to " + eqip_url)
        

    @staticmethod
    def getEquipmentHandleUrl(ifdo:dict, ifdo_field:str, handle_prefix:str, prov:miqtp.Provenance=None ):
        """ Constructs and returns handle url from eqipment id in ifdo_field['name']. Returns "" if fails. Does not check is site is up. 
            handle_prefix prefix must be of form e.g. https://hdl.handle.net/20.500.12085 
        """
        def _log(msg:str):
            if prov is not None:
                prov.log(msg)
            else:
                print(msg)

        image_field = iFDO._findValue(ifdo,ifdo_field)
        if image_field == "" or 'name' not in image_field or image_field['name'] == "":
            _log("Error! Can't construct "  + ifdo_field + " uri, name not filled.")
            return ""
        return miqtc.assertSlash(handle_prefix) + miqtequip.equipmentShortName(image_field['name'])
    

    def trySetHeaderImageProjectUriToOsisExpeditionUrl(self,override:bool = False):
        """ Sets header image-project uri to osis expedition url parsed from image-project['name'].
        Params:
            override: if False set only if uri is empty or does not exist. """

        if not override and self.findUncheckedValue('image-project:uri') != "":
            self._prov.log("Caution! image-project:uri already exists and is not overridden: " + self.findUncheckedValue('image-project:uri'))
            return

        expedition_url = self.getHeaderImageProjectUriToOsisExpeditionUrl(self._ifdo_tmp,self._prov)
        if expedition_url == "":
            return
        self._ifdo_tmp[miqtv.image_set_header_key]['image-project']['uri'] = expedition_url
        try:
            ret = requests.head(expedition_url)
            if ret.status_code != 200:
                raise Exception()
        except Exception:
            self._prov.log("Caution! image-project:uri set but not reachable " + expedition_url)
        self._prov.log("image-project:uri set to " + expedition_url)


    @staticmethod
    def getHeaderImageProjectUriToOsisExpeditionUrl(ifdo:dict,prov:miqtp.Provenance=None):
        """ Returns header image-project uri as osis expedition url parsed from image-project['name']."""

        def _log(msg:str):
            if prov is not None:
                prov.log(msg)
            else:
                print(msg)

        image_project = iFDO._findValue(ifdo,'image-project')
        if image_project == "" or 'name' not in image_project or image_project['name'] == "":
            _log("Error! Can't construct image-project uri, image-project not filled.")
            return ""
        
        # get expedition id
        try:
            expedition_id = miqtosis.getExpeditionIdFromLabel(image_project['name'])
        except ValueError:
            _log("Error! Can't get osis expedition id from image-project " + str(image_project))
            return ""

        expedition_url = miqtosis.getExpeditionUrl(expedition_id)
        return expedition_url


    def trySetHeaderImageEventUriToOsisEventUrl(self,override:bool = False):
        """ Sets header image-event uri to osis event url parsed from image-project and image-event['name'] or 
        image-event['uri'] if it refers to osis.
        Params:
            override: if False set only if uri is empty or does not exist. """

        if not override and self.findUncheckedValue('image-event:uri') != "":
            self._prov.log("Caution! image-event:uri already exists and is not overridden: " + self.findUncheckedValue('image-event:uri'))
            return

        osis_url = self.getHeaderImageEventUriToOsisEventUrl(self._ifdo_tmp,self._prov)
        if osis_url == "":
            return
        self._ifdo_tmp[miqtv.image_set_header_key]['image-event']['uri'] = osis_url
        try:
            ret = requests.head(osis_url)
            if ret.status_code != 200:
                raise Exception()
        except Exception:
            self._prov.log("Caution! image-event:uri set but not reachable " + osis_url)
        self._prov.log("image-event:uri set to " + osis_url)


    @staticmethod
    def getHeaderImageEventUriToOsisEventUrl(ifdo:dict,prov:miqtp.Provenance=None):
        """ Returns header image-event uri as osis event url parsed from image-project and image-event['name'] or 
        image-event['uri'] if it refers to osis. Returns empty string if fails. """

        def _log(msg:str):
            if prov is not None:
                prov.log(msg)
            else:
                print(msg)

        image_project = iFDO._findValue(ifdo, 'image-project')
        if image_project == "" or 'name' not in image_project or image_project['name'] == "":
            _log("Error! Can't construct image-event uri, image-project not filled.")
            return ""

        # get expedition id
        ## try parse expedition id from project osis uri
        if 'uri' in image_project and image_project['uri'] != "":
            expedition_id = miqtosis.getExpeditionIdFromUrl(image_project['uri'])
        # get expedition id from osis api by expedition name
        else:
            try:
                expedition_id = miqtosis.getExpeditionIdFromLabel(image_project['name'])
            except ValueError:
                _log("Error! Can't get osis expedition id from image-project " + str(image_project))
                return ""

        # try parse event id
        event_name = iFDO._findValue(ifdo, 'image-event:name')
        if event_name == "":
            _log("Error! Can't construct image-event uri, image-event:name not filled.")
            return ""

        osis_url = miqtosis.getOsisEventUrl(expedition_id, event_name)

        if osis_url == "":
            _log("Error! Can't construct image-event uri from expedition_id and event_name: " + str(expedition_id) + ", " + event_name)
            return ""

        return osis_url


    def trySetLicenseUriFromLicenseName(self, override:bool = False):
        """ Sets header image-license uri to url guessed from image-license.
        Params:
            override: if False set only if uri is empty or does not exist. """
        
        if not override and self.findUncheckedValue('image-license:uri') != "":
            self._prov.log("Caution! image-license:uri already exists and is not overridden: " + self.findUncheckedValue('image-license:uri'))
            return
        
        license_url = self._getLicenseUriToLicense(self._ifdo_tmp)
        if license_url == "":
            self._prov.log("Warning! Can't guess image-license:uri from name")
            return
        self._ifdo_tmp[miqtv.image_set_header_key]['image-license']['uri'] = license_url
        try:
            ret = requests.head(license_url)
            if ret.status_code != 200:
                raise Exception()
        except Exception:
            self._prov.log("Caution! image-license:uri set but not reachable " + license_url)
        self._prov.log("image-license:uri set to " + license_url)


    @staticmethod
    def _getLicenseUriToLicense(ifdo:dict):
        """ Returns header image-license uri guessed from license name. Returns empty string if fails. """
        image_license = iFDO._findValue(ifdo, 'image-license')
        if isinstance(image_license, dict):
            return iFDO._getLicenseUri(image_license['name'])
        else:
            return iFDO._getLicenseUri(image_license)
        

    @staticmethod
    def _getLicenseUri(licence_name:str):
        """ Tries to guess licence url from license name and returns it. Returns "" if fails. """
        licenses_dict = {
            "ccby": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "cc0": "https://creativecommons.org/publicdomain/zero/1.0/legalcode"
        }
        cleand_license = licence_name.strip().lower().replace('-', '')
        if cleand_license in licenses_dict:
            return licenses_dict[cleand_license]
        else:
            return ""


    def _getIntHashFile(self):
        return self._getIntFilePrefix() + self.intermediateFilesDef_core['hashes']['suffix']

    def _getIntUuidFile(self):
        return self._getIntFilePrefix() + self.intermediateFilesDef_core['uuids']['suffix']

    def get_int_startTimes_file(self):
        return self._getIntFilePrefix() + self.intermediateFilesDef_core['datetime']['suffix']

    def _getIntNavFile(self):
        return self._getIntFilePrefix() + self.intermediateFilesDef_core['navigation']['suffix']
    
    def _getIntFilePrefix(self):
        """ depends on 'image-event' and 'image-sensor' so it can change during upate """
        return os.path.join(self._dir.to(self._dir.dt.intermediate), self.getUncheckedValue('image-set-name'))

