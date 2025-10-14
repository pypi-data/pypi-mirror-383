import os

import mariqt.variables as miqtv
import mariqt.core as miqtc
import mariqt.variables as miqtv
import mariqt.geo as miqtg
import mariqt.sources.ifdo as miqtifdo


class IfdoReader:
    " Provides convenient functions for reading data from iFDO files "

    def __init__(self, iFDOfile:str):
        " Provides convenient functions for reading data from iFDO files "
        
        self.iFDOfile = iFDOfile
        self.ifdo = miqtifdo.iFDO._openIfdoFile(self.iFDOfile)


    def __getitem__(self, keys):
        """ Returns copy of checked ifdo set or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Raises IfdoException if item does not exist. """
        keys = keys.split(':')
        return miqtifdo.iFDO._getValue(self.ifdo,keys)

    
    def find(self, keys:str):
        """ Returns copy of ifdo header or item field value, also considerng default values from header.
            Use keys as e.g. '<item>:<key>:...'. Can be used for header fields as well as item fields.
            Item index can be leglected, in case of video a dict {<image-datatime>:<value>,...} is returned.
            Returns empty string if item does not exist. """
        return miqtifdo.iFDO._findValue(self.ifdo,keys)


    def getImagesPositions(self,image_types=miqtv.image_types):
        """ Returns images first position(s) 
            @return: {'imageName': [{'lat': value, 'lon': value, 'datetime': value}]}, image-coordinate-reference-system """
        
        retDict = {}
        retRefsys = self.ifdo[miqtv.image_set_header_key]['image-coordinate-reference-system']

        headerValLat = None
        try:
            headerValLat = self.ifdo[miqtv.image_set_header_key]['image-latitude']
        except KeyError:
            pass

        headerValLon = None
        try:
            headerValLon = self.ifdo[miqtv.image_set_header_key]['image-longitude']
        except KeyError:
            pass


        for fileName in self.ifdo[miqtv.image_set_items_key]:
            if fileName.split('.')[-1].lower() in image_types:
                retDict[fileName] = self._getItemLatLon(fileName,headerValLat,headerValLon)

        return retDict, retRefsys


    def writeWorldFilesForPhotos(self,destDir:str,imageSourceDir:str):
        """ Writes world files for photos if all required fields are there under the assumption that the camera was looking straight down (pitch and roll are ignored!). 
            Returns a list of items for which creation failed: [[item,msg],...]"""

        # TODO get images online from broker

        iFDOexceptions = []

        # get images position
        positionsLatLon, refsys = self.getImagesPositions(image_types=miqtv.photo_types)
        crsFieldTmp = ''.join(e for e in refsys if e.isalnum()).lower()
        if crsFieldTmp == 'wgs84' or crsFieldTmp == 'epsg4326':
            refsys = "WGS84"
        else:
            iFDOexceptions.append(["","Coordinates reference system \"" + refsys + "\" can not be handled. Use preferably EPSG:4326 or WGS84"])
            return iFDOexceptions


        for photo in positionsLatLon:
            try:
                self.checkItemHash(photo,imageSourceDir) # TODO could be in different subfolder or from online broker

                # convert to utm to avoid precision issue with lat/lon values in world files
                lat = positionsLatLon[photo][0]['lat']
                lon = positionsLatLon[photo][0]['lon']
                easting,northing,zone,isNorth = miqtg.latLon2utm(lat,lon,refsys)
                exif = self._getItemDefaultValue(photo,'image-acquisition-settings') # TODO what if not there? read from image directly? Should be checked if hash matches? Image could have been cropped after iFDO creation
                imageWidth = int(str(exif['Image Width']).strip('\''))
                imageHeight = int(str(exif['Image Height']).strip('\''))
                heading = self._getItemDefaultValue(photo,'image-camera-yaw-degrees')
                altitude = self._getItemDefaultValue(photo,'image-meters-above-ground')

                domePort,msg = self._tryGetIsDomePort(photo)
                focalLenghPixels, msg = self._tryGetFocalLengthInPixels(photo, domePort)
                if focalLenghPixels == [-1,-1] or focalLenghPixels == -1:
                    raise miqtc.IfdoException(msg)
                miqtg.writeSimpleUtmWorldFile(os.path.join(destDir,miqtg.convertImageNameToWorldFileName(photo)),easting,northing,zone,isNorth,imageWidth,imageHeight,heading,altitude,focalLenghPixels[0],focalLenghPixels[1])
            except miqtc.IfdoException as e:
                iFDOexceptions.append([photo,str(e.args)])

        return iFDOexceptions


    def checkItemHash(self,item:str,fileDir:str):
        """ compares file's hash with hash in iFDO and throws exception if they don't match """

        file = os.path.join(fileDir,item)
        if not os.path.isfile(file):
            raise miqtc.IfdoException("File \"" + item + "\" not found in dir \"" + fileDir + "\"")

        if isinstance(self.ifdo[miqtv.image_set_items_key][item],list): # in case of video with item as list the first entry holds the default and the hash cannot vary for the same image
            itemEntry = self.ifdo[miqtv.image_set_items_key][item][0] 
        else:
            itemEntry = self.ifdo[miqtv.image_set_items_key][item]
        if not itemEntry['image-hash-sha256'] == miqtc.sha256HashFile(file):
            raise miqtc.IfdoException(item, "iFDO entry is not up to date, image hash does not match.")

    def getImageDirectory(self):
        """ Returns the lowermost local directory containing the image files inferred from 'image-set-local-path'. If 'image-set-local-path' not provided for all image items the iFDO's parent directory is returned. """
        localPaths = []
        iFDOFileParentDir = os.path.dirname(os.path.dirname(self.iFDOfile))
        for item in self.ifdo[miqtv.image_set_items_key]:
            try:
                itemLocalPath = self._getItemDefaultValue(item,'image-set-local-path')
            except miqtc.IfdoException:
                try:
                    itemLocalPath = self._getItemDefaultValue(item,'image-local-path') # backwards compatibility
                except miqtc.IfdoException:
                    itemLocalPath = iFDOFileParentDir
            if itemLocalPath not in localPaths:
                localPaths.append(itemLocalPath)
        commonPath = os.path.commonpath(localPaths)
        if not os.path.isabs(commonPath):
            commonPath = os.path.normpath(os.path.join(os.path.dirname(self.iFDOfile), commonPath))
        return commonPath


    def _tryGetIsDomePort(self,item):
        """ Tries to read port type from 'image-camera-housing-viewport'[viewport-type] or 'image-flatport-parameters'/'image-domeport-parameters' 
            Returns True,msg if dome port, False,msg if flat port, None,msg otherwise """

        try:
            portTypeStr = self._getItemDefaultValue(item,'image-camera-housing-viewport')
            portTypeStr = portTypeStr['viewport-type']
            if 'dome' in portTypeStr.lower() and not 'flat' in portTypeStr.lower():
                return True,"Parsed from 'image-camera-housing-viewport'['viewport-type']"
            elif not 'dome' in portTypeStr.lower() and 'flat' in portTypeStr.lower():
                return False,"Parsed from 'image-camera-housing-viewport'['viewport-type']"
            else:
                return None,"Could not read port type from 'image-camera-housing-viewport'['viewport-type'] in item: " + item
        except (miqtc.IfdoException, KeyError):
            pass

        flatPortParamsFound = False
        try: 
            flatPortParams = self._getItemDefaultValue(item,'image-flatport-parameters')
            flatPortParamsFound = True
        except miqtc.IfdoException:
            pass
        domePortParamsFound = False
        try: 
            domePortParams = self._getItemDefaultValue(item,'image-domeport-parameters')
            domePortParamsFound = True
        except miqtc.IfdoException:
            pass

        if flatPortParamsFound and domePortParamsFound:
            return None,"Could not read port type from item as it contains info on both flat and dome port: " + item
        if flatPortParamsFound:
            return False,"Assumed as flat port as 'image-flatport-parameters' found in item: " + item
        if domePortParamsFound:
            return True,"Assumed as dome port as 'image-domeport-parameters' found in item: " + item
        return None,"Could not read port type from item: " + item


    def _tryGetFocalLengthInPixels(self,item:str,domePort=None):
        """ 
        Tries to read/determine focal length in pixels either from 'image-camera-calibration-model'['calibration-focal-length-xy-pixel'] or from exif values.
        if domePort = False, flat port is assumed and a correction factor of 1.33 is applied for focal length determined from exif values
        Returns either focalLength, message or [focalLengthX,focalLengthY], message. If unsuccessful focalLength = -1
        """

        # try read from 'image-camera-calibration-model'['calibration-focal-length-xy-pixel']
        try:
            focalLengthXY = self._getItemDefaultValue(item,'image-camera-calibration-model')
            try:
                focalLengthXY = focalLengthXY['calibration-focal-length-xy-pixel']
            except KeyError:
                raise miqtc.IfdoException(item,"does not contain 'image-camera-calibration-model'['calibration-focal-length-xy-pixel']")

            if not isinstance(focalLengthXY,list): # x and y value are identical
                focalLengthXY = [focalLengthXY,focalLengthXY]
            if len(focalLengthXY) != 2:
                raise miqtc.IfdoException(item,"Invalid entry for 'image-camera-calibration-model'['calibration-focal-length-xy-pixel'] : " + str(focalLengthXY) )

            if not isinstance(focalLengthXY[0],float) or not isinstance(focalLengthXY[0],int) or not isinstance(focalLengthXY[1],float) or not isinstance(focalLengthXY[1],int):
                try:
                    focalLengthXY = [float(focalLengthXY[0]),float(focalLengthXY[1])]
                except ValueError:
                    raise miqtc.IfdoException(item,"Invalid entry for 'image-camera-calibration-model'['calibration-focal-length-xy-pixel'] : " + str(focalLengthXY) )
            
            return focalLengthXY, "Parsed from 'image-camera-calibration-model'['calibration-focal-length-xy-pixel']"
        except miqtc.IfdoException:
            pass

        underwaterImage = True
        try:
            alt0 = self[item+'0:image-altitude-meters'] #self.__getItemDefaultValue(item, 'image-altitude-meters')
            if alt0 > 0:
                underwaterImage = False
        except miqtc.IfdoException:
            pass

        # add correction factor for flat port
        if domePort is None and underwaterImage:
            return [-1,-1], "Could not determine focal length from 'image-camera-calibration-model'['calibration-focal-length-xy-pixel'] and port type, which is required for correct evaluation of exif values, is not provided!"
        correctionFkt = 1.0
        if domePort == False and underwaterImage:
            correctionFkt = 1.33

        # otherwise try derive from exif tags
        exif = self._getItemDefaultValue(item,'image-acquisition-settings')
        ## from Focal Length, Focal Plane X Resolution, Focal Plane Y Resolution, Focal Plane Resolution Unit
        focalLengthXY, msg = self._tryDetermineFocalLenghtInPixelsFromExif_1(exif)
        if focalLengthXY != [-1,-1]:
            return [e*correctionFkt for e in focalLengthXY], 'Derived from exif tags Focal Length, Focal Plane X Resolution, Focal Plane Y Resolution, Focal Plane Resolution Unit'
        ## from from 35 mm equivalent focal length
        focalLengthXY, msg = self._tryDetermineFocalLenghtInPixelsFromExif_2(exif)
        if focalLengthXY != [-1,-1]:
            return [e*correctionFkt for e in focalLengthXY], 'Derived from exif tag Focal Length with 35 mm equivalent'
 
        return [-1,-1], "Could not determine from focal length in pixels from neither 'image-camera-calibration-model'['calibration-focal-length-xy-pixel'] nor exif tags Focal Length, Focal Plane X Resolution, Focal Plane Y Resolution, Focal Plane Resolution Unit"


    def _tryDetermineFocalLenghtInPixelsFromExif_1(self,exifDict:dict):
        """ try to determine focal length in pixels from exif tags Focal Length, Focal Plane X Resolution, Focal Plane Y Resolution, Focal Plane Resolution Unit.
            Retruns [focalLengthPixels_x,focalLengthPixels_y], message
            Retruns focalLengthPixels = -1 if not successfull """

        try:
            focalLength = str(exifDict['Focal Length'])
            focalPlaneRes_x = float(str(exifDict['Focal Plane X Resolution']).strip('\''))
            focalPlaneRes_y = float(str(exifDict['Focal Plane Y Resolution']).strip('\''))
            focalPlaneRes_unit = str(exifDict['Focal Plane Resolution Unit']).strip('\'')
        except (KeyError, ValueError):
            return [-1,-1], "Could not find all required fields Focal Length, Focal Plane X Resolution, Focal Plane Y Resolution, Focal Plane Resolution Unit"
        
        # parse focal length from left (may be '7.5 mm (...)')
        focalLengthStripped = focalLength.strip()
        focalLengthFloat = None
        for i in range(len(focalLengthStripped)):
            try:
                focalLengthFloat = float(focalLengthStripped[0:i+1])
            except ValueError:
                pass
        if focalLengthFloat is None:
            return [-1,-1], "Could not parse forcal length from 'Focal Length': " + focalLength
        scaleFkt_focal = self._unitConversionFact2mm(focalLength)
        if scaleFkt_focal == -1:
            return [-1,-1], "Could not parse forcal length unit from 'Focal Length': " + focalLength
        focalLength_mm = focalLengthFloat * scaleFkt_focal

        scaleFkt_res = self._unitConversionFact2mm(focalPlaneRes_unit)
        if scaleFkt_res == -1:
            return [-1,-1], "Could not parse Focal Plane Resolution Unit from 'Focal Plane Resolution Unit': " + focalPlaneRes_unit

        focalLengthPixels_x = focalLength_mm * focalPlaneRes_x / scaleFkt_res
        focalLengthPixels_y = focalLength_mm * focalPlaneRes_y / scaleFkt_res

        return [focalLengthPixels_x,focalLengthPixels_y], ""


    def _tryDetermineFocalLenghtInPixelsFromExif_2(self,exifDict:dict):
        """ try to determine focal length in pixels from 35 mm equivalent focal length in exif tag Focal Length's add on e.g. '7.0 mm (35 mm equivalent: 38.8 mm)'.
            Retruns [focalLengthPixels_x,focalLengthPixels_y], message
            Retruns focalLengthPixels = -1 if not successfull """

        try:
            focalLength = str(exifDict['Focal Length'])
            imageWidth = int(str(exifDict['Image Width']).strip('\''))
        except (KeyError, ValueError):
            return [-1,-1], "Could not find all required fields Focal Length, Image Width"

        # try parse 35 mm equivalent from e.g.:  7.0 mm (35 mm equivalent: 38.8 mm)
        colonIndex = focalLength.find(':')
        if colonIndex == -1:
            return [-1,-1], "Could not parse 35 mm equivalent focal length from 'Focal Length': " + focalLength
        focalLengthEq35mmFloat = None
        equal35mmPart = focalLength[colonIndex+1::].strip()
        for i in range(len(equal35mmPart)):
            try:
                focalLengthEq35mmFloat = float(equal35mmPart[0:i+1])
            except ValueError:
                pass
        scaleFkt = self._unitConversionFact2mm(focalLength[colonIndex+1::])
        if focalLengthEq35mmFloat is None or scaleFkt == -1:
            return [-1,-1], "Could not parse 35 mm equivalent focal length from 'Focal Length': " + focalLength
        
        focalLengthPixels = focalLengthEq35mmFloat * scaleFkt * imageWidth / 36.0
        return [focalLengthPixels,focalLengthPixels], ""


    def _unitConversionFact2mm(self,unit:str):
        """ looks for letter sequence in unit and checks if it's 'inches','m','cm','mm','um' or '' and returns respective conversion factor to mm (if there are no letters it returns 1). Otherwise return -1 """

        firstLetterSeq = ""
        firstFound = False
        for i in range(len(unit)):
            if unit[i].isalpha():
                firstFound = True
                firstLetterSeq += unit[i]
            if not unit[i].isalpha() and firstFound == True:
                break

        if firstLetterSeq.lower() == "inches":
            scaleFkt = 25.4
        elif firstLetterSeq.lower() == "m":
            scaleFkt = 1000.0
        elif firstLetterSeq.lower() == "cm":
            scaleFkt = 10.0
        elif firstLetterSeq.lower() == "mm":
            scaleFkt = 1.0
        elif firstLetterSeq.lower() == "um":
            scaleFkt = 1/1000
        elif firstLetterSeq.lower() == "":
            scaleFkt = 1
        else:
            scaleFkt = -1

        return scaleFkt


    def _getItemDefaultValue(self,item:str,fieldName:str):
        """ returns item values (first entry in case of videos). Throws mariqt.core.IfdoException if field not found. """

        ret = self[":".join([item,'0',fieldName])]
        if ret == "":
           raise miqtc.IfdoException("Error: Field {0} neither found in item {1} nor header".format(fieldName,item))
        return ret


    def _getItemLatLon(self,item:str,headerValLat,headerValLon):
        """ returns {'lat': value, 'lon': value, 'datetime': value} of list of those """

        itemVal = self.ifdo[miqtv.image_set_items_key][item]
        if not isinstance(itemVal,list):
            ret = self._parse2LatLonDict(itemVal,headerValLat,headerValLon)
        else:
            ret = []
            try:
                itemLatDefault = itemVal[0]['image-latitude']
            except KeyError:
                itemLatDefault = headerValLat
                #if itemLatDefault is None:
                #    raise Exception("Error: Field {0} neither found in item {1} nor header".format('image-latitude',item))

            try:
                itemLonDefault = itemVal[0]['image-longitude']
            except KeyError:
                itemLonDefault = headerValLon
                #if itemLonDefault is None:
                #    raise Exception("Error: Field {0} neither found in item {1} nor header".format('image-latitude',item))

            for subEntry in itemVal:
                ret.append(self._parse2LatLonDict(subEntry,itemLatDefault,itemLonDefault))

        return ret
            

    def _parse2LatLonDict(self,itemVal,headerValLat,headerValLon):
        """ returns {'lat':lat,'lon':lon,'datetime':datetime} """
        datetime = itemVal['image-datetime']
        try:
            lat = itemVal['image-latitude']
        except KeyError:
            lat = headerValLat
            if lat is None:
                raise Exception("Error: Field {0} neither found in item {1} nor header".format('image-latitude',itemVal))
        try:
            lon = itemVal['image-longitude']
        except KeyError:
            lon = headerValLon
            if lon is None:
                raise Exception("Error: Field {0} neither found in item {1} nor header".format('image-longitude',itemVal))
        return {'lat':lat,'lon':lon,'datetime':datetime}


