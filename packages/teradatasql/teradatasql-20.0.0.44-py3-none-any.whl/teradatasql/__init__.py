# Copyright 2018-2019 by Teradata Corporation. All rights reserved.

import binascii
import ctypes
import datetime
import decimal
import io
import itertools
import json
import os
import platform
import re
import struct
import sys
import threading
import time
import traceback
from . import vernumber

__version__ = vernumber.sVersionNumber

try:
    import numpy
    numpyArrayType = numpy.ndarray
except ImportError:
    numpyArrayType = None

try:
    import pandas
    dataFrameType = type (pandas.DataFrame ())
except ImportError:
    dataFrameType = None

apilevel = "2.0" # Required by DBAPI 2.0

threadsafety = 2 # Threads may share the module and connections, but not cursors # Required by DBAPI 2.0

paramstyle = "qmark" # Required by DBAPI 2.0

class Warning(Exception): # Required by DBAPI 2.0
    pass

class Error(Exception): # Required by DBAPI 2.0
    pass

class InterfaceError(Error): # Required by DBAPI 2.0
    pass

class DatabaseError(Error): # Required by DBAPI 2.0
    pass

class DataError(DatabaseError): # Required by DBAPI 2.0
    pass

class OperationalError(DatabaseError): # Required by DBAPI 2.0
    pass

class IntegrityError(DatabaseError): # Required by DBAPI 2.0
    pass

class InternalError(DatabaseError): # Required by DBAPI 2.0
    pass

class ProgrammingError(DatabaseError): # Required by DBAPI 2.0
    pass

class NotSupportedError(DatabaseError): # Required by DBAPI 2.0
    pass

lockInit = threading.Lock()
bInitDone = False
goside = None

def logMsg (sCategory, s):
    print ("{:.23} [{}] PYDBAPI-{} {}".format (datetime.datetime.now ().strftime ("%Y-%m-%d.%H:%M:%S.%f"), threading.current_thread ().name, sCategory, s), flush = True)

def traceLog (s):
    logMsg ("TRACE", s)

def debugLog (s):
    logMsg ("DEBUG", s)

def timingLog (s):
    logMsg ("TIMING", s)

def prototype (rtype, func, *args):
    func.restype = rtype
    func.argtypes = args

def _safeReadFile (sPathName):
    try:
        with open (sPathName, encoding="utf-8") as f:
            return f.read ()
    except:
        return ""

class TeradataConnection:

    def __init__ (self, sConnectParams=None, **kwargs):

        self.uLog = 0
        self.bTraceLog = False
        self.bDebugLog = False
        self.bTimingLog = False
        self.uConnHandle = None # needed by __repr__

        if not sConnectParams:
            sConnectParams = '{}'

        for sKey, oValue in kwargs.items ():
            if isinstance (oValue, bool):
                kwargs [sKey] = str (oValue).lower () # use lowercase words true and false
            else:
                kwargs [sKey] = str (oValue)

        # Compose a streamlined stack trace of script file names and package names
        listFrames = []
        sPackagesDir = os.path.dirname (os.path.dirname (__file__)).replace (os.sep, "/") + "/"
        for fr in traceback.extract_stack ():
            sFrame = fr [0].replace (os.sep, "/")
            if sFrame.startswith (sPackagesDir):
                sFrame = sFrame [len (sPackagesDir) : ].split ("/") [0] # remove the packages dir prefix and take the first directory, which is the package name
            else:
                sFrame = sFrame.split ("/") [-1] # take the last element, which is the Python script file name
            if not sFrame.startswith ("<") and sFrame not in listFrames: # omit <string>, omit <template>, omit repeated entries
                listFrames += [ sFrame ]

        kwargs ['client_kind'  ] = 'P' # G = Go, P = Python, R = R, S = Node.js
        kwargs ['client_vmname'] = 'Python ' + sys.version
        kwargs ['client_osname'] = platform.platform () + ' ' + platform.machine ()
        kwargs ['client_stack' ] = " ".join (listFrames)
        kwargs ['client_extra' ] = 'PYTHON=' + platform.python_version () + ';' # must be semicolon-terminated
        try:
            kwargs ['client_extra'] += 'TZ=' + datetime.datetime.now (tz=datetime.timezone.utc).astimezone ().strftime ('%Z %z') + ';' # must be semicolon-terminated
        except: # astimezone() can fail when the TZ environment variable is set to an unexpected format
            pass

        sConnectArgs = json.dumps (kwargs)

        global bInitDone, goside # assigned-to variables are local unless marked as global

        try:
            lockInit.acquire()
            if not bInitDone:
                bInitDone = True

                sOSType = platform.system ().lower ()
                sCPU    = platform.machine ().lower ()
                bARM    = sCPU.startswith ("arm") or sCPU.startswith ("aarch")
                bPOWER  = sCPU == "ppc64le"
                bFIPS   = sOSType == "linux" and _safeReadFile ("/proc/sys/crypto/fips_enabled").strip () == "1"
                nBits   = ctypes.sizeof (ctypes.c_voidp) * 8 # is 32 or 64

                if sOSType == "windows":
                    if nBits == 32:
                        sExtension = "x86.dll"
                    else:
                        sExtension = "dll"
                elif sOSType == "darwin":
                    sExtension = "dylib"
                elif sOSType == "aix":
                    sExtension = "aix.so"
                elif bARM and bFIPS: # Linux from here on
                    sExtension = "arm.fips.so"
                elif bARM:
                    sExtension = "arm.so"
                elif bPOWER:
                    sExtension = "power.so"
                elif nBits == 32: # must check before FIPS
                    sExtension = "x86.so"
                elif bFIPS:
                    sExtension = "fips.so"
                else:
                    sExtension = "so"

                sLibPathName = os.path.join(os.path.dirname(__file__), "teradatasql." + sExtension)
                goside = ctypes.cdll.LoadLibrary(sLibPathName)

                prototype (None, goside.goCombineJSON     , ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goParseParams     , ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64))
                prototype (None, goside.goCreateConnection, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64))
                prototype (None, goside.goCloseConnection , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goCancelRequest   , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goCreateRows      , ctypes.c_uint64, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_uint64, ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64))
                prototype (None, goside.goResultMetaData  , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64), ctypes.POINTER (ctypes.c_uint16), ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_int32), ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goFetchRow        , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_int32), ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goNextResult      , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_char))
                prototype (None, goside.goCloseRows       , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goFreePointer     , ctypes.c_uint64, ctypes.POINTER (ctypes.c_char))

        finally:
            lockInit.release()

        pcError = ctypes.POINTER (ctypes.c_char) ()
        pcCombined = ctypes.POINTER (ctypes.c_char) ()
        goside.goCombineJSON (sConnectParams.encode ('utf-8'), sConnectArgs.encode ('utf-8'), ctypes.byref (pcError), ctypes.byref (pcCombined))
        if pcError:
            sErr = ctypes.string_at (pcError).decode ('utf-8')
            goside.goFreePointer (self.uLog, pcError)
            raise OperationalError (sErr)

        sConnectParams = ctypes.string_at (pcCombined).decode ('utf-8')
        goside.goFreePointer (self.uLog, pcCombined)

        pcError = ctypes.POINTER (ctypes.c_char) ()
        uLog = ctypes.c_uint64 ()
        goside.goParseParams (sConnectParams.encode ('utf-8'), ctypes.byref (pcError), ctypes.byref (uLog))
        if pcError:
            sErr = ctypes.string_at (pcError).decode ('utf-8')
            goside.goFreePointer (self.uLog, pcError)
            raise OperationalError (sErr)

        self.uLog = uLog.value
        self.bTraceLog  = (self.uLog & 1) != 0
        self.bDebugLog  = (self.uLog & 2) != 0
        self.bTimingLog = (self.uLog & 8) != 0

        if self.bTraceLog:
            traceLog ("> enter __init__ {}".format (sConnectParams))
        try:
            pcError = ctypes.POINTER (ctypes.c_char)()
            uConnHandle = ctypes.c_uint64()
            goside.goCreateConnection (self.uLog, __version__.encode ('utf-8'), sConnectParams.encode ('utf-8'), ctypes.byref (pcError), ctypes.byref (uConnHandle))
            if pcError:
                sErr = ctypes.string_at(pcError).decode('utf-8')
                goside.goFreePointer (self.uLog, pcError)
                raise OperationalError(sErr)

            self.uConnHandle = uConnHandle.value

        finally:
            if self.bTraceLog:
                traceLog ("< leave __init__ {}".format (self))

        # end __init__

    def close(self): # Required by DBAPI 2.0

        if self.bTraceLog:
            traceLog ("> enter close {}".format (self))
        try:
            pcError = ctypes.POINTER (ctypes.c_char)()
            goside.goCloseConnection (self.uLog, self.uConnHandle, ctypes.byref (pcError))
            if pcError:
                sErr = ctypes.string_at(pcError).decode('utf-8')
                goside.goFreePointer (self.uLog, pcError)
                raise OperationalError(sErr)

        finally:
            if self.bTraceLog:
                traceLog ("< leave close {}".format (self))

        # end close

    def cancel(self):

        if self.bTraceLog:
            traceLog ("> enter cancel {}".format (self))
        try:
            pcError = ctypes.POINTER (ctypes.c_char)()
            goside.goCancelRequest (self.uLog, self.uConnHandle, ctypes.byref (pcError))
            if pcError:
                sErr = ctypes.string_at(pcError).decode('utf-8')
                goside.goFreePointer (self.uLog, pcError)
                raise OperationalError(sErr)

        finally:
            if self.bTraceLog:
                traceLog ("< leave cancel {}".format (self))

        # end cancel

    def commit(self): # Required by DBAPI 2.0
        if self.bTraceLog:
            traceLog ("> enter commit {}".format (self))
        try:
            with self.cursor () as cur:
                cur.execute ("{fn teradata_commit}")
        finally:
            if self.bTraceLog:
                traceLog ("< leave commit {}".format (self))

        # end commit

    def rollback(self): # Required by DBAPI 2.0
        if self.bTraceLog:
            traceLog ("> enter rollback {}".format (self))
        try:
            with self.cursor () as cur:
                cur.execute ("{fn teradata_rollback}")
        finally:
            if self.bTraceLog:
                traceLog ("< leave rollback {}".format (self))

        # end rollback

    def cursor(self): # Required by DBAPI 2.0
        return TeradataCursor(self)

    def nativeSQL(self, sSQL):
        if self.bTraceLog:
            traceLog ("> enter nativeSQL {}".format (self))
        try:
            with self.cursor () as cur:
                cur.execute ("{fn teradata_nativesql}" + sSQL) # teradata_nativesql never produces a fake result set
                return cur.fetchone () [0]
        finally:
            if self.bTraceLog:
                traceLog ("< leave nativeSQL {}".format (self))

        # end nativeSQL

    @property
    def autocommit(self): # Required by SQLAlchemy 2.0
        if self.bTraceLog:
            traceLog ("> enter autocommit getter {}".format (self))
        try:
            return self.nativeSQL ("{fn teradata_autocommit}") == "true"
        finally:
            if self.bTraceLog:
                traceLog ("< leave autocommit getter {}".format (self))

        # end commit

    @autocommit.setter
    def autocommit(self, value): # Required by SQLAlchemy 2.0
        if self.bTraceLog:
            traceLog ("> enter autocommit setter {}".format (self))
        if type (value) != bool:
            raise TypeError ("value unexpected type {}".format (type (value)))
        try:
            s = "on" if value else "off"
            self.nativeSQL ("{fn teradata_autocommit_" + s + "}")
        finally:
            if self.bTraceLog:
                traceLog ("< leave autocommit setter {}".format (self))

    def __enter__(self): # Implements with-statement context manager
        return self

    def __exit__(self, t, value, traceback): # Implements with-statement context manager

        if self.bTraceLog:
            traceLog ("> enter __exit__ {}".format (self))
        try:
            self.close()

        finally:
            if self.bTraceLog:
                traceLog ("< leave __exit__ {}".format (self))

        # end __exit__

    def __repr__(self): # Equivalent to the toString method in Java or the String method in Go
        return("{} uConnHandle={}".format(self.__class__.__name__, self.uConnHandle))

    # end class TeradataConnection

class DBAPITypeObject:

    def __init__(self, *values):
        self.values = values

    def __eq__(self, other):
        return other in self.values

    # end class DBAPITypeObject

connect = TeradataConnection # Required by DBAPI 2.0

Date = datetime.date # Required by DBAPI 2.0

Time = datetime.time # Required by DBAPI 2.0

Timestamp = datetime.datetime # Required by DBAPI 2.0

DateFromTicks = datetime.date.fromtimestamp # Required by DBAPI 2.0

def TimeFromTicks (x): # Required by DBAPI 2.0
    return datetime.datetime.fromtimestamp (x).time ()

TimestampFromTicks = datetime.datetime.fromtimestamp # Required by DBAPI 2.0

Binary = bytes # Required by DBAPI 2.0

STRING = str # Required by DBAPI 2.0

BINARY = bytes # Required by DBAPI 2.0

NUMBER = DBAPITypeObject (int, float, decimal.Decimal) # Required by DBAPI 2.0

DATETIME = DBAPITypeObject (datetime.date, datetime.time, datetime.datetime) # Required by DBAPI 2.0

ROWID = None # Required by DBAPI 2.0

# Serialized data value type codes:
# B=bytes
# D=double (64-bit double)
# F=false (bool)
# I=integer (32-bit integer)
# L=long (64-bit integer)
# M=number
# N=null
# S=string (UTF8-encoded)
# T=true (bool)
# U=date
# V=time
# W=time with time zone
# X=timestamp
# Y=timestamp with time zone
# Z=terminator

def _serializeCharacterValue (abyTypeCode, s):

    aby = s.encode ('utf-8')
    return abyTypeCode + struct.pack (">Q", len (aby)) + aby

def _deserializeCharacterValue (abyTypeCode, pc, i, row):

    if pc [i] == abyTypeCode:
        i += 1

        uByteCount = struct.unpack (">Q", pc [i : i + 8]) [0] # uint64
        i += 8

        sValue = pc [i : i + uByteCount].decode ('utf-8')
        i += uByteCount

        if row is not None:

            # Accommodate optional fractional seconds for V=time, W=time with time zone, X=timestamp, Y=timestamp with time zone
            sFormatSuffix = '.%f' if abyTypeCode in (b'V', b'W', b'X', b'Y') and '.' in sValue else ''

            if abyTypeCode in (b'W', b'Y'): # W=time with time zone, Y=timestamp with time zone
                sValue = sValue [ : -3] + sValue [-2 : ] # remove colon from time zone value for compatibility with strptime
                sFormatSuffix += '%z'

            if abyTypeCode == b'U': # U=date
                row.append (datetime.datetime.strptime (sValue, '%Y-%m-%d').date ())

            elif abyTypeCode in (b'V', b'W'): # V=time, W=time with time zone
                row.append (datetime.datetime.strptime (sValue, '%H:%M:%S' + sFormatSuffix).timetz ())

            elif abyTypeCode in (b'X', b'Y'): # X=timestamp, Y=timestamp with time zone
                row.append (datetime.datetime.strptime (sValue, '%Y-%m-%d %H:%M:%S' + sFormatSuffix))

            elif abyTypeCode == b'M': # M=number
                row.append (decimal.Decimal (sValue))

            else: # S=string
                row.append (sValue)

            # end if row is not None

        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type {}/N but got {} at byte offset {}'.format (abyTypeCode, pc [i], i))

    # end _deserializeCharacterValue

def _serializeBool (b):

    return b'T' if b else b'F'

def _deserializeBool (pc, i, row):

    if pc [i] in (b'T', b'F'): # T=true, F=false

        if row is not None:
            row.append (pc [i] == b'T')
        return i + 1

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type T/F/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeBool

def _serializeBytes (aby):

    return b'B' + struct.pack (">Q", len (aby)) + aby

def _deserializeBytes (pc, i, row):

    if pc [i] == b'B': # B=bytes
        i += 1

        uByteCount = struct.unpack (">Q", pc [i : i + 8]) [0] # uint64
        i += 8

        abyValue = pc [i : i + uByteCount]
        i += uByteCount

        if row is not None:
            row.append (abyValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type B/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeBytes

def _serializeDate (da):

    return _serializeCharacterValue (b'U', da.isoformat ())

def _deserializeDate (pc, i, row):

    return _deserializeCharacterValue (b'U', pc, i, row)

def _serializeDouble (d):

    return b'D' + struct.pack (">d", d)

def _deserializeDouble (pc, i, row):

    if pc [i] == b'D': # D=double
        i += 1

        dValue = struct.unpack (">d", pc [i : i + 8]) [0] # float64
        i += 8

        if row is not None:
            row.append (dValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type D/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeDouble

def _serializeInt (n):

    return b'I' + struct.pack (">i", n)

def _deserializeInt (pc, i, row):

    if pc [i] == b'I': # I=integer
        i += 1

        nValue = struct.unpack (">i", pc [i : i + 4]) [0] # int32
        i += 4

        if row is not None:
            row.append (nValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type I/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeInt

def _serializeLong (n):

    return b'L' + struct.pack (">q", n)

def _deserializeLong (pc, i, row):

    if pc [i] == b'L': # L=long
        i += 1

        nValue = struct.unpack (">q", pc [i : i + 8]) [0] # int64
        i += 8

        if row is not None:
            row.append (nValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type L/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeLong

def _serializeNull ():

    return b'N'

def _deserializeNull (pc, i, row):

    if pc [i] == b'N': # N=null

        if row is not None:
            row.append (None)
        return i + 1

    else:
        raise OperationalError ('Expected column type N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeNull

def _serializeNumber (dec):

    return _serializeCharacterValue (b'M', '{:f}'.format (dec)) # avoid exponential notation

def _deserializeNumber (pc, i, row):

    return _deserializeCharacterValue (b'M', pc, i, row)

def _serializeString (s):

    return _serializeCharacterValue (b'S', s)

def _deserializeString (pc, i, row):

    return _deserializeCharacterValue (b'S', pc, i, row)

def _serializeTime (ti):

    return _serializeCharacterValue (b'W' if ti.tzinfo else b'V', ti.isoformat ())

def _deserializeTime (pc, i, row):

    return _deserializeCharacterValue (b'V', pc, i, row)

def _deserializeTimeWithTimeZone (pc, i, row):

    return _deserializeCharacterValue (b'W', pc, i, row)

def _serializeTimestamp (ts):

    return _serializeCharacterValue (b'Y' if ts.tzinfo else b'X', ts.isoformat (' '))

def _deserializeTimestamp (pc, i, row):

    return _deserializeCharacterValue (b'X', pc, i, row)

def _deserializeTimestampWithTimeZone (pc, i, row):

    return _deserializeCharacterValue (b'Y', pc, i, row)

def _formatTimedelta (tdelta):

    # Output format matches VARCHAR values accepted by the Teradata Database for implicit conversion to INTERVAL DAY TO SECOND.
    # positive:  1234 12:34:56.123456
    # negative: -1234 12:34:56.123456

    nMM, nSS = divmod (tdelta.seconds, 60)
    nHH, nMM = divmod (nMM, 60)

    # Prepend a space character for a positive days value.
    return '{: d} {:02d}:{:02d}:{:02d}.{:06d}'.format (tdelta.days, nHH, nMM, nSS, tdelta.microseconds)

    # end _formatTimedelta

def _hexDump (aby):

    asLines = []

    for iOffset in range (0, len (aby), 16):

        abySegment = aby [iOffset : min (iOffset + 16, len (aby))]

        sHexDigits = binascii.hexlify (abySegment).decode ('ascii')
        asHexDigits = [ sHexDigits [i : i + 2] for i in range (0, len (sHexDigits), 2) ]
        sSpacedHexDigits = " ".join (asHexDigits)

        abyPrintable = b''
        for i in range (0, len (abySegment)):
            if abySegment [i] in range (32, 126): # printable chars are 32 space through 126 ~ tilde
                abyPrintable += abySegment [i : i + 1]
            else:
                abyPrintable += b'.'

        sPrintable = abyPrintable.decode ('ascii')

        asLines += [ "{:08x}  {:<47}  |{}|".format (iOffset, sSpacedHexDigits, sPrintable) ]

    return "\n".join (asLines)

    # end _hexDump

class TeradataCursor:

    def __init__(self, con):

        self.description = None # Required by DBAPI 2.0
        self.columntypename = None
        self.rowcount = -1 # Required by DBAPI 2.0
        self.activitytype = None
        self.activityname = None
        self.arraysize = 1 # Required by DBAPI 2.0
        self.rownumber = None # Optional by DBAPI 2.0
        self.connection = con # Optional by DBAPI 2.0
        self.uRowsHandle = None
        self.bClosed = False

        # end __init__

    def callproc(self, sProcName, params=None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter callproc {}".format (self))
        try:
            sCall = "{call " + sProcName

            if params:
                sCall += " (" + ", ".join (["?"] * len (params)) + ")"

            sCall += "}"

            self.execute (sCall, params)

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave callproc {}".format (self))

        # end callproc

    def close(self): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter close {}".format (self))
        try:
            if not self.bClosed:
                self.bClosed = True
                self._closeRows ()
        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave close {}".format (self))

        # end close

    def _stopIfClosed (self):

        if self.connection.bTraceLog:
            traceLog ("> enter _stopIfClosed {}".format (self))
        try:
            if self.bClosed:
                raise ProgrammingError ("Cursor is closed")
        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave _stopIfClosed {}".format (self))

        # end _stopIfClosed

    def _closeRows (self):

        if self.connection.bTraceLog:
            traceLog ("> enter _closeRows {}".format (self))
        try:
            if self.uRowsHandle:
                pcError = ctypes.POINTER (ctypes.c_char)()
                goside.goCloseRows (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError))

                self.uRowsHandle = None

                if pcError:
                    sErr = ctypes.string_at(pcError).decode('utf-8')
                    goside.goFreePointer (self.connection.uLog, pcError)
                    raise OperationalError(sErr)

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave _closeRows {}".format (self))

        # end _closeRows

    def execute (self, sOperation, params = None, ignoreErrors = None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter execute {}".format (self))
        try:
            if params is None:
                self.executemany (sOperation, None, ignoreErrors)

            elif dataFrameType is not None and isinstance (params, dataFrameType):
                self.executemany (sOperation, params, ignoreErrors)

            elif type (params) not in [list, tuple]:
                raise TypeError ("params unexpected type {}".format (type (params)))

            elif len (params) == 0:
                self.executemany (sOperation, None, ignoreErrors)

            elif type (params [0]) in [list, tuple]:
                # Excerpt from PEP 249 DBAPI documentation:
                #  The parameters may also be specified as list of tuples to e.g. insert multiple rows in a single
                #  operation, but this kind of usage is deprecated: .executemany() should be used instead.
                self.executemany (sOperation, params, ignoreErrors)

            else:
                self.executemany (sOperation, [params, ], ignoreErrors)

            return self

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave execute {}".format (self))

        # end execute

    def _obtainResultMetaData (self):

        if self.connection.bTraceLog:
            traceLog ("> enter _obtainResultMetaData {}".format (self))
        try:
            pcError = ctypes.POINTER (ctypes.c_char) ()
            uActivityCount = ctypes.c_uint64 ()
            uActivityType = ctypes.c_uint16 ()
            pcActivityName = ctypes.POINTER (ctypes.c_char) ()
            pcColumnMetaData = ctypes.POINTER (ctypes.c_char) ()
            goside.goResultMetaData (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError), ctypes.byref (uActivityCount), ctypes.byref (uActivityType), ctypes.byref (pcActivityName), None, ctypes.byref (pcColumnMetaData))

            if pcError:
                sErr = ctypes.string_at (pcError).decode ('utf-8')
                goside.goFreePointer (self.connection.uLog, pcError)
                raise OperationalError (sErr)

            self.rowcount = uActivityCount.value
            self.activitytype = uActivityType.value

            if pcActivityName:
                self.activityname = ctypes.string_at (pcActivityName).decode ('utf-8')
                goside.goFreePointer (self.connection.uLog, pcActivityName)

            if pcColumnMetaData:
                self.description = []
                self.columntypename = []
                i = 0
                while pcColumnMetaData [i] != b'Z': # Z=terminator
                    columnDesc = []

                    # (1) Column name
                    i = _deserializeString (pcColumnMetaData, i, columnDesc)

                    i = _deserializeString (pcColumnMetaData, i, self.columntypename)

                    # (2) Type code
                    i = _deserializeString (pcColumnMetaData, i, columnDesc)

                    if columnDesc [-1] == 'b': # typeCode b=bytes
                        columnDesc [-1] = BINARY

                    elif columnDesc [-1] == 'd': # typeCode d=double
                        columnDesc [-1] = float

                    elif columnDesc [-1] in ('i', 'l'): # typeCode i=integer (int32), l=long (int64)
                        columnDesc [-1] = int

                    elif columnDesc [-1] == 'm': # typeCode m=number
                        columnDesc [-1] = decimal.Decimal

                    elif columnDesc [-1] == 's': # typeCode s=string
                        columnDesc [-1] = STRING

                    elif columnDesc [-1] == 'u': # typeCode u=date
                        columnDesc [-1] = datetime.date

                    elif columnDesc [-1] in ('v', 'w'): # typeCode v=time, w=time with time zone
                        columnDesc [-1] = datetime.time

                    elif columnDesc [-1] in ('x', 'y'): # typeCode x=timestamp, y=timestamp with time zone
                        columnDesc [-1] = datetime.datetime

                    # (3) Display size
                    columnDesc.append (None) # not provided

                    # (4) Max byte count
                    i = _deserializeLong (pcColumnMetaData, i, columnDesc)

                    # (5) Precision
                    i = _deserializeLong (pcColumnMetaData, i, columnDesc)

                    # (6) Scale
                    i = _deserializeLong (pcColumnMetaData, i, columnDesc)

                    # (7) Nullable
                    i = _deserializeBool (pcColumnMetaData, i, columnDesc)

                    self.description.append (columnDesc)

                    # end while

                goside.goFreePointer (self.connection.uLog, pcColumnMetaData)

                # end if pcColumnMetaData

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave _obtainResultMetaData {}".format (self))

        # end _obtainResultMetaData

    def executemany (self, sOperation, seqOfParams, ignoreErrors = None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter executemany {}".format (self))
        try:
            self._stopIfClosed ()
            self._closeRows ()

            if ignoreErrors:

                if type (ignoreErrors) == int:
                    ignoreErrors = [ignoreErrors]

                if type (ignoreErrors) not in [list, tuple]:
                    raise TypeError ("ignoreErrors unexpected type {}".format (type (ignoreErrors)))

                for i in range (0, len (ignoreErrors)):
                    if type (ignoreErrors [i]) != int:
                        raise TypeError ("ignoreErrors[{}] unexpected type {}".format (i, type (ignoreErrors [i])))

                setIgnoreErrorCodes = set (ignoreErrors)
            else:
                setIgnoreErrorCodes = set () # empty set

            dStartTime = time.time ()

            with io.BytesIO (b'') as osBindValues:

                if seqOfParams is not None:

                    if dataFrameType is not None and isinstance (seqOfParams, dataFrameType):
                        iterRows = seqOfParams.itertuples (index=False, name=None)
                    elif type (seqOfParams) in [list, tuple]:
                        iterRows = seqOfParams
                    else:
                        raise TypeError ("seqOfParams unexpected type {}".format (type (seqOfParams)))

                    for i, aoRowValues in enumerate (iterRows):

                        if type (aoRowValues) not in [list, tuple]:
                            raise TypeError ("seqOfParams[{}] unexpected type {}".format (i, type (aoRowValues)))

                        if len (aoRowValues) == 0:
                            raise ValueError ("seqOfParams[{}] is zero length".format (i))

                        for j, oValue in enumerate (aoRowValues):

                            if numpyArrayType is not None and isinstance (oValue, numpyArrayType):
                                if oValue.ndim == 1:
                                    oValue = ",".join (str (x) for x in oValue) # convert numpy array to comma-separated string
                                else:
                                    raise TypeError ("seqOfParams[{}][{}] numpy array unexpected number of dimensions {}".format (i, j, oValue.ndim))


                            if isinstance (oValue, str):
                                aby = oValue.encode ("utf-8")
                                osBindValues.write (b'S')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, int):
                                osBindValues.write (b'L')
                                osBindValues.write (struct.pack (">q", oValue))
                                continue

                            if oValue is None:
                                osBindValues.write (b'N')
                                continue

                            if isinstance (oValue, float):
                                osBindValues.write (b'D')
                                osBindValues.write (struct.pack (">d", oValue))
                                continue

                            if isinstance (oValue, decimal.Decimal):
                                aby = "{:f}".format (oValue).encode ("utf-8") # avoid exponential notation
                                osBindValues.write (b'M')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.datetime): # check first because datetime is a subclass of date
                                aby = oValue.isoformat (" ").encode ("utf-8")
                                osBindValues.write (b'Y' if oValue.tzinfo else b'X')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.date):
                                aby = oValue.isoformat ().encode ("utf-8")
                                osBindValues.write (b'U')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.time):
                                aby = oValue.isoformat ().encode ("utf-8")
                                osBindValues.write (b'W' if oValue.tzinfo else b'V')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.timedelta):
                                aby = _formatTimedelta (oValue).encode ("utf-8")
                                osBindValues.write (b'S') # serialized as string
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, bytes) or isinstance (oValue, bytearray):
                                osBindValues.write (b'B')
                                osBindValues.write (struct.pack (">Q", len (oValue)))
                                osBindValues.write (oValue)
                                continue

                            raise TypeError ("seqOfParams[{}][{}] unexpected type {}".format (i, j, type (oValue)))

                            # end for j

                        osBindValues.write (b'Z') # end of row terminator

                        # end for i
                    # end if seqOfParams

                osBindValues.write (b'Z') # end of all rows terminator

                abyBindValues = osBindValues.getvalue ()

                # end with osBindValues

            if self.connection.bTimingLog:
                timingLog ("executemany serialize bind values took {} ms and produced {} bytes".format ((time.time () - dStartTime) * 1000.0, len (abyBindValues)))

            dStartTime = time.time ()

            pcError = ctypes.POINTER (ctypes.c_char) ()
            uRowsHandle = ctypes.c_uint64 ()
            goside.goCreateRows (self.connection.uLog, self.connection.uConnHandle, sOperation.encode ('utf-8'), len (abyBindValues), abyBindValues, ctypes.byref (pcError), ctypes.byref (uRowsHandle))
            if pcError:
                sErr = ctypes.string_at (pcError).decode ('utf-8')
                goside.goFreePointer (self.connection.uLog, pcError)

                setErrorCodes = { int (s) for s in re.findall (r"\[Error (\d+)\]", sErr) }
                setIntersection = setErrorCodes & setIgnoreErrorCodes
                bIgnore = len (setIntersection) > 0 # ignore when intersection is non-empty
                if self.connection.bDebugLog:
                    debugLog ("executemany bIgnore={} setIntersection={} setErrorCodes={} setIgnoreErrorCodes={}".format (bIgnore, setIntersection, setErrorCodes, setIgnoreErrorCodes))
                if bIgnore:
                    return

                raise OperationalError (sErr)

            if self.connection.bTimingLog:
                timingLog ("executemany call to goCreateRows took {} ms".format ((time.time () - dStartTime) * 1000.0))

            self.uRowsHandle = uRowsHandle.value

            self._obtainResultMetaData ()

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave executemany {}".format (self))

        # end executemany

    def fetchone(self): # Required by DBAPI 2.0

        try:
            return next(self)

        except StopIteration:
            return None

        # end fetchone

    def fetchmany(self, nDesiredRowCount=None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter fetchmany {}".format (self))
        try:
            if nDesiredRowCount is None:
                nDesiredRowCount = self.arraysize

            rows = []
            nObservedRowCount = 0
            for row in self:
                rows.append(row)
                nObservedRowCount += 1
                if nObservedRowCount == nDesiredRowCount:
                    break

            return rows

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave fetchmany {}".format (self))

        # end fetchmany

    def fetchall(self): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter fetchall {}".format (self))
        try:
            rows = []
            for row in self:
                rows.append(row)

            return rows

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave fetchall {}".format (self))

        # end fetchall

    def nextset(self): # Optional by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter nextset {}".format (self))
        try:
            self._stopIfClosed ()

            if self.uRowsHandle:

                pcError = ctypes.POINTER (ctypes.c_char)()
                cAvail = ctypes.c_char()

                goside.goNextResult (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError), ctypes.byref (cAvail))

                if pcError:
                    sErr = ctypes.string_at(pcError).decode('utf-8')
                    goside.goFreePointer (self.connection.uLog, pcError)
                    raise OperationalError(sErr)

                if cAvail.value == b'Y':
                    self._obtainResultMetaData ()
                else:
                    self.description = None
                    self.columntypename = None
                    self.rowcount = -1
                    self.activitytype = None
                    self.activityname = None

                return cAvail.value == b'Y'

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave nextset {}".format (self))

        # end nextset

    def setinputsizes(self, sizes): # Required by DBAPI 2.0
        self._stopIfClosed ()

    def setoutputsize(self, size, column=None): # Required by DBAPI 2.0
        self._stopIfClosed ()

    def __iter__(self): # Implements iterable # Optional by DBAPI 2.0
        return self

    def __next__(self): # Implements Python 3 iterator

        if self.connection.bTraceLog:
            traceLog ("> enter __next__ {}".format (self))
        try:
            self._stopIfClosed ()

            if self.uRowsHandle:

                pcError = ctypes.POINTER (ctypes.c_char)()
                nColumnValuesByteCount = ctypes.c_int32 ()
                pcColumnValues = ctypes.POINTER (ctypes.c_char)()

                goside.goFetchRow (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError), ctypes.byref (nColumnValuesByteCount), ctypes.byref (pcColumnValues))

                if pcError:
                    sErr = ctypes.string_at (pcError).decode ('utf-8')
                    goside.goFreePointer (self.connection.uLog, pcError)
                    raise OperationalError (sErr)

                if pcColumnValues:

                    if self.connection.bDebugLog and nColumnValuesByteCount:
                        debugLog ("__next__ nColumnValuesByteCount={}\n{}".format (nColumnValuesByteCount.value, _hexDump (ctypes.string_at (pcColumnValues, nColumnValuesByteCount))))

                    row = []
                    i = 0
                    while pcColumnValues [i] != b'Z': # Z=terminator

                        if pcColumnValues [i] == b'N': # N=null
                            iNew = _deserializeNull (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'B': # B=bytes
                            iNew = _deserializeBytes (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'D': # D=double
                            iNew = _deserializeDouble (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'I': # I=integer
                            iNew = _deserializeInt (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'L': # L=long
                            iNew = _deserializeLong (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'M': # M=number
                            iNew = _deserializeNumber (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'S': # S=string
                            iNew = _deserializeString (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'U': # U=date
                            iNew = _deserializeDate (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'V': # V=time
                            iNew = _deserializeTime (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'W': # W=time with time zone
                            iNew = _deserializeTimeWithTimeZone (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'X': # X=timestamp
                            iNew = _deserializeTimestamp (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'Y': # Y=timestamp with time zone
                            iNew = _deserializeTimestampWithTimeZone (pcColumnValues, i, row)

                        else:
                            raise OperationalError ('Unrecognized column type {} at byte offset {}'.format (pcColumnValues [i], i))

                        if self.connection.bDebugLog:
                            debugLog ("__next__ row[{}] typeCode={} type={} value={}".format (len (row) - 1, pcColumnValues [i], type (row [-1]), row [-1]))

                        i = iNew

                        # end while

                    goside.goFreePointer (self.connection.uLog, pcColumnValues)

                    return row

                    # end if pcColumnValues

                # end if self.uRowsHandle

            raise StopIteration ()

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave __next__ {}".format (self))

        # end __next__

    def next(self): # Implements Python 2 iterator # Optional by DBAPI 2.0
        return self.__next__()

    def __enter__(self): # Implements with-statement context manager
        return self

    def __exit__(self, t, value, traceback): # Implements with-statement context manager

        if self.connection.bTraceLog:
            traceLog ("> enter __exit__ {}".format (self))
        try:
            self.close()

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave __exit__ {}".format (self))

        # end __exit__

    def __repr__(self): # Equivalent to the toString method in Java or the String method in Go
        return "{} uRowsHandle={} bClosed={}".format (self.__class__.__name__, self.uRowsHandle, self.bClosed)

    # end class TeradataCursor

def _quoteText (o):

    return '"' + re.sub ("[\r\n]+", " ", o).replace ('"', '""') + '"' if isinstance (o, str) else "{}".format (o)

def _quoteCsvText (s):

    if s is None:
        return ""

    if not s:
        return '""'

    for c in s:
        if c < " " or c == "," or c == '"':
            return '"' + s.replace ('"', '""') + '"'

    return s

    # end _quoteCsvText

_FORMAT_TEXT, _FORMAT_RAW, _FORMAT_CSV = 1, 2, 3

def _formatValue (nFormat, bIsProp, nColumn, sKey, sValue):

    if nFormat == _FORMAT_TEXT:
        return sKey + " = " + _quoteText (sValue)

    if nFormat == _FORMAT_RAW:
        return (sKey + "=" if bIsProp else " " if nColumn > 1 else "") + ("None" if sValue is None else re.sub ("[\r\n]+", "\n", sValue))

    # else _FORMAT_CSV
    return ("," if nColumn > 1 else "") + _quoteCsvText (sValue)

    # end _formatValue

def _printValue (wCurrent, nFormat, bIsProp, nColumn, nColumnCount, sKey, sValue):

    s = _formatValue (nFormat, bIsProp, nColumn, sKey, sValue)

    bOneValuePerLine = nFormat == _FORMAT_TEXT or nFormat == _FORMAT_RAW and bIsProp
    bLastValueOnLine = nColumn >= nColumnCount

    if bOneValuePerLine or bLastValueOnLine:
        print (s, file = wCurrent, flush = True)
    else:
        print (s, file = wCurrent, flush = True, end = "") # no line ending

    # end _printValue

def _printArray (wCurrent, nFormat, bIsProp, aasData):

    asNames = aasData [0]
    iRowStart = 0 if nFormat == _FORMAT_CSV else 1

    for asRow in aasData [iRowStart : ]:
        for iColumn, sValue in enumerate (asRow):
            _printValue (wCurrent, nFormat, bIsProp, iColumn + 1, len (asRow), asNames [iColumn], sValue)

    # end _printArray

def _printNameValue (wCurrent, nFormat, sName, sValue):

    _printArray (wCurrent, nFormat, False, [ [ sName ], [ sValue ] ])

def _stripControlChars (sInput):

    sOutput = ""
    for c in sInput:
        if c == '\t' or c == '\r' or c == '\n' or c >= ' ' and c != '\x7F' and c != '\uFFFD': # DEL and Unicode replacement character
            sOutput += c

    return sOutput

    # _stripControlChars

def _printResultSet (wCurrent, nFormat, bVerboseControlChars, sTitle, cur):

    if nFormat == _FORMAT_CSV:
        for iColumn, aoColumnAttr in enumerate (cur.description):
            _printValue (wCurrent, nFormat, False, iColumn + 1, len (cur.description), None, aoColumnAttr [0])

    for iRow in itertools.count ():
        row = cur.fetchone ()
        if row is None:
            break

        for iColumn, oValue in enumerate (row):

            sKey = "{} Row {} Column {} {} {}".format (sTitle, iRow + 1, iColumn + 1, _quoteText (cur.description [iColumn][0]), cur.columntypename [iColumn])

            sValue = str (oValue) if oValue is not None else None
            if sValue and not bVerboseControlChars:
                sValue = _stripControlChars (sValue)

            _printValue (wCurrent, nFormat, False, iColumn + 1, len (row), sKey, sValue)

    # end _printResultSet

def _readLine (f):

    s = next (f, None)
    return s.rstrip ("\r\n") if s else s

def _safePeek (stack):

    return stack [-1] if stack else None

def _pushDiff (stack, o):

    if o != _safePeek (stack):
        stack.append (o)

def _popClose (stack, exclude):

    o = stack.pop ()
    if o != exclude:
        o.close ()

    # end _popClose

def main (asArgs):

    if not asArgs:
        print ("Arguments: Command...")
        print ("-i turns on interactive mode to prompt for commands from stdin")
        print ("-im turns on interactive mode and sql:multi")
        print ("-is turns on interactive mode and sql:semicolon")
        print ("# begins a comment")
        print ("autocommit:off turns off autocommit")
        print ("autocommit:on turns on autocommit")
        print ("commit calls the connection commit method") # mixed-case Commit will be executed as a SQL request
        print ("cont:message sets the continuation prompt to the specified message")
        print ("driver prints the driver name and version")
        print ("echo:message prints the specified message")
        print ("exit stops reading commands from the current input source")
        print ("format:raw avoids formatting output")
        print ("format:text (the default) formats output as text")
        print ("host= prefix begins a comma-separated list of connection parameters for a database connection")
        print ("ignore:sql:all ignores all SQL exceptions")
        print ("ignore:sql:code,code,... ignores SQL exceptions with one of the specified error codes")
        print ("ignore:sql:none stops for any SQL exceptions")
        print ("input:filename reads commands from the specified file until EOF")
        print ("input:stdin reads commands from stdin until EOF (interactive Ctrl+Z on Windows)")
        print ("jdbc: prefix begins an ignored JDBC Driver connection URL")
        print ("nativeSQL:command calls the connection nativeSQL method for the command")
        print ("output:filename sends output to specified file")
        print ("output:stdout (the default) sends output to stdout")
        print ("pause waits for a line from stdin")
        print ("pid prints the process ID of Python")
        print ("prompt:message sets the prompt to the specified message")
        print ("rollback calls the connection rollback method") # mixed-case Rollback will be executed as a SQL request
        print ("sleep:ms sleeps for the specified number of milliseconds")
        print ("sql:multi accepts multiple arguments or input lines as a SQL request up to an empty argument or input line")
        print ("sql:semicolon accepts multiple arguments or input lines as a SQL request up to an argument or input line ending with a semicolon")
        print ("sql:single (the default) accepts a single argument or input line as a SQL request")
        print ("time prints the current date and time")
        print ("verbose:connection (the default) and verbose:-connection control printing connection status")
        print ("verbose:controlchars and verbose:-controlchars (the default) control printing control characters")
        print ("verbose:sleep (the default) and verbose:-sleep control printing sleep status")
        print ("verbose:sql and verbose:-sql (the default) control printing the SQL request before executing")
        print ("verbose:transaction and verbose:-transaction (the default) control printing transaction commands")
        print ("version prints the teradatasql version")
        print ("Otherwise the SQL request is executed", flush = True)
        return

    nFormat = _FORMAT_TEXT

    stackInput = [] # empty stack means to read commands from args
    try:
        wCurrent = sys.stdout
        try:
            con = None
            try:
                MULTI, SEMICOLON, SINGLE = 1, 2, 3
                nSQLEnd = SINGLE
                sPendingCommand = None
                sContinuationPrompt = None
                sPrompt = None
                bIgnoreNonSQLErrors = False
                setIgnoreSQLErrors = None # None means ignore none
                bVerboseConnection = True
                bVerboseSleep = True
                bVerboseSQL = False
                bVerboseControlChars = False
                bVerboseTransaction = False

                iArg = 0
                while True:

                    # Obtain command

                    sCommand = None

                    if _safePeek (stackInput) == sys.stdin:

                        if sPendingCommand and sContinuationPrompt is not None:
                            print (sContinuationPrompt, flush = True, end = "")

                        elif sPendingCommand is None and sPrompt is not None:
                            print (sPrompt, flush = True, end = "")

                    while sCommand is None and _safePeek (stackInput):

                        sCommand = _readLine (_safePeek (stackInput))
                        if sCommand is None: # EOF reached
                            _popClose (stackInput, sys.stdin)

                    if sCommand is None and iArg < len (asArgs):
                        sCommand = asArgs [iArg] ; iArg += 1

                    bCompleteSQL = False
                    if sPendingCommand is not None:

                        if sCommand is None:
                            sCommand = sPendingCommand
                            sPendingCommand = None
                            bCompleteSQL = True

                        elif nSQLEnd == MULTI and sCommand == "":
                            sCommand = sPendingCommand
                            sPendingCommand = None
                            bCompleteSQL = True

                        elif nSQLEnd == SEMICOLON and sCommand.endswith (";"):
                            sCommand = sPendingCommand + " " + sCommand
                            sPendingCommand = None
                            bCompleteSQL = True

                        else:
                            sPendingCommand += " " + sCommand
                            continue # repeat for loop

                        # end if sPendingCommand

                    if sCommand is None:
                        break # out of for loop

                    # Process command

                    try:

                        if sCommand == "":

                            pass # do nothing

                        elif sCommand in [ "-i", "-im", "-is" ]:

                            _pushDiff (stackInput, sys.stdin)

                            sPrompt = ">>> "
                            sContinuationPrompt = "... "
                            bIgnoreNonSQLErrors = True
                            setIgnoreSQLErrors = set () # empty set means ignore all

                            if sCommand == "-im":
                                nSQLEnd = MULTI

                            elif sCommand == "-is":
                                nSQLEnd = SEMICOLON

                        elif sCommand == "sql:multi":

                            nSQLEnd = MULTI

                        elif sCommand == "sql:semicolon":

                            nSQLEnd = SEMICOLON

                        elif sCommand == "sql:single":

                            nSQLEnd = SINGLE

                        elif sCommand.startswith ("cont:"):

                            sContinuationPrompt = sCommand [len ("cont:") : ]

                        elif sCommand.startswith ("prompt:"):

                            sPrompt = sCommand [len ("prompt:") : ]

                        elif sCommand == "exit":

                            if stackInput:
                                _popClose (stackInput, sys.stdin)

                        elif sCommand.startswith ("#"): # is a comment

                            pass # do nothing

                        elif sCommand == "time":

                            _printNameValue (wCurrent, nFormat, sCommand, datetime.datetime.now ().strftime ("%Y-%m-%d %H:%M:%S.%f"))

                        elif sCommand == "verbose:sleep":

                            bVerboseSleep = True

                        elif sCommand == "verbose:-sleep":

                            bVerboseSleep = False

                        elif sCommand.startswith ("sleep:"):

                            nMillis = int (sCommand [len ("sleep:") : ])
                            if bVerboseSleep:
                                print ("Sleeping for " + str (nMillis) + " ms", file = wCurrent, flush = True)

                            time.sleep (nMillis / 1000.0)

                            if bVerboseSleep:
                                print ("Done sleeping for " + str (nMillis) + " ms", file = wCurrent, flush = True)

                        elif sCommand == "driver":

                            _printNameValue (wCurrent, nFormat, sCommand, "Teradata SQL Driver for Python " + __version__)

                        elif sCommand == "version":

                            _printNameValue (wCurrent, nFormat, sCommand, __version__)

                        elif sCommand == "pid":

                            _printNameValue (wCurrent, nFormat, sCommand, str (os.getpid ()))

                        elif sCommand.startswith ("echo:"):

                            s = sCommand [len ("echo:") : ]
                            print (s, file = wCurrent, flush = True)

                        elif sCommand == "pause":

                            print ("Paused. Press Enter to continue:", file = wCurrent, flush = True)
                            _readLine (sys.stdin)

                        elif sCommand == "verbose:connection":

                            bVerboseConnection = True

                        elif sCommand == "verbose:-connection":

                            bVerboseConnection = False

                        elif sCommand.startswith ("jdbc:"):

                            _printNameValue (wCurrent, nFormat, "Ignored", sCommand)

                        elif sCommand.startswith ("host="):

                            if con:
                                conToClose = con
                                con = None
                                conToClose.close ()

                            sCommand = sCommand.replace (",,", "\x01") # temporarily replace double commas (literal commas) with Ctrl+A

                            mapParams = {}
                            for sPair in sCommand.split (","):

                                sPair = sPair.replace ("\x01", ",") # restore literal commas

                                if "=" in sPair:
                                    sKey, sValue = sPair.split ("=", 1)
                                    mapParams [sKey] = sValue
                                else:
                                    raise ValueError ("Missing equal sign in connection parameter " + sPair)

                            con = connect (**mapParams)

                            if bVerboseConnection:
                                sResult    = con.nativeSQL ("{fn teradata_connected}|{fn teradata_session_number}|{fn teradata_provide(remote_address)}:{fn teradata_provide(remote_port)}|Teradata Database {fn teradata_database_version}")
                                asValues   = sResult.split ("|", 3)
                                bConnected = asValues [0] == "true"
                                sStatus    = "Connected"  if bConnected else "Closed"
                                sSession   = asValues [1] if bConnected else None
                                sRemote    = asValues [2]
                                sVersion   = asValues [3]

                                _printArray (wCurrent, nFormat, False, [ [ "Status", "Remote", "Version", "Session" ], [ sStatus, sRemote, sVersion, sSession ] ])

                                # end if bVerboseConnection

                            # end if host

                        elif sCommand.startswith ("input:"):

                            s = sCommand [len ("input:") : ]

                            _pushDiff (stackInput, sys.stdin if s == "stdin" else open (s, encoding = "utf8"))

                        elif sCommand.startswith ("output:"):

                            s = sCommand [len ("output:") : ]

                            if wCurrent != sys.stdout:
                                wCurrent.close ()

                            wCurrent = sys.stdout

                            if s != "stdout":
                                wCurrent = open (s, mode = "w", encoding = "utf8")

                        elif sCommand.startswith ("format:"):

                            s = sCommand [len ("format:") : ]

                            if s == "text":
                                nFormat = _FORMAT_TEXT
                            elif s == "raw":
                                nFormat = _FORMAT_RAW
                            elif s == "csv":
                                nFormat = _FORMAT_CSV
                            else:
                                raise ValueError ("Unknown format " + s)

                        elif sCommand == "ignore:sql:all":

                            setIgnoreSQLErrors = set () # empty set means ignore all

                        elif sCommand == "ignore:sql:none":

                            setIgnoreSQLErrors = None # None means ignore none

                        elif sCommand.startswith ("ignore:sql:"):

                            s = sCommand [len ("ignore:sql:") : ]
                            asTokens = s.split (",")
                            if not asTokens:
                                raise ValueError (sCommand)

                            setIgnoreSQLErrors = { int (s) for s in asTokens }

                        elif sCommand == "verbose:sql":

                            bVerboseSQL = True

                        elif sCommand == "verbose:-sql":

                            bVerboseSQL = False

                        elif sCommand == "verbose:controlchars":

                            bVerboseControlChars = True

                        elif sCommand == "verbose:-controlchars":

                            bVerboseControlChars = False

                        elif sCommand == "verbose:transaction":

                            bVerboseTransaction = True

                        elif sCommand == "verbose:-transaction":

                            bVerboseTransaction = False

                        elif not con:

                            print ("No connection available for", sCommand, file = wCurrent, flush = True)

                        elif sCommand == "autocommit:off":

                            if bVerboseTransaction:
                                print (sCommand, file = wCurrent, flush = True)

                            con.autocommit = False

                        elif sCommand == "autocommit:on":

                            if bVerboseTransaction:
                                print (sCommand, file = wCurrent, flush = True)

                            con.autocommit = True

                        elif sCommand == "commit":

                            if bVerboseTransaction:
                                print (sCommand, file = wCurrent, flush = True)

                            con.commit ()

                        elif sCommand == "rollback":

                            if bVerboseTransaction:
                                print (sCommand, file = wCurrent, flush = True)

                            con.rollback ()

                        elif sCommand.startswith ("nativeSQL:"):

                            _printNameValue (wCurrent, nFormat, "nativeSQL", con.nativeSQL (sCommand [len ("nativeSQL:") : ]))

                        elif nSQLEnd == MULTI and not bCompleteSQL:

                            sPendingCommand = sCommand

                        elif nSQLEnd == SEMICOLON and not bCompleteSQL and not sCommand.endswith (";"):

                            sPendingCommand = sCommand

                        else: # con is available

                            if bVerboseSQL:
                                print (sCommand, file = wCurrent, flush = True)

                            with con.cursor () as cur:
                                cur.execute (sCommand)
                                for iResult in itertools.count ():
                                    _printResultSet (wCurrent, nFormat, bVerboseControlChars, "Result {}".format (iResult + 1), cur)
                                    if not cur.nextset ():
                                        break

                                # end with cur

                            # end else con is available

                    except DatabaseError as ex:

                        if setIgnoreSQLErrors is None: # None means ignore none
                            bIgnore = False
                        elif len (setIgnoreSQLErrors) == 0: # empty set means ignore all
                            bIgnore = True
                        else:
                            setErrorCodes = { int (s) for s in re.findall (r"\[Error (\d+)\]", str (ex)) }
                            setIntersection = setErrorCodes & setIgnoreSQLErrors
                            bIgnore = len (setIntersection) > 0 # ignore when intersection is non-empty, meaning exception has at least one ignored error code

                        if bIgnore:
                            _printNameValue (wCurrent, nFormat, "Exception", str (ex))
                        else:
                            raise

                    # end while

            finally:
                if con:
                    con.close ()

        finally:
            if wCurrent != sys.stdout:
                wCurrent.close ()

    finally:
        while stackInput:
            _popClose (stackInput, sys.stdin)

    # end main
