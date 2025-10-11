import ctypes
import sys,os
import platform
'''

int tinyfd_notifyPopup(
	char const * aTitle, /* NULL or "" */
	char const * aMessage, /* NULL or "" may contain \n \t */
	char const * aIconType); /* "info" "warning" "error" */
		/* return has only meaning for tinyfd_query */


'''
__all__ = [
    "message_box",
    "beep",
    "select_folder",
    "input_box",
    "color_chooser",
    "select_file",
    "save_file",
    "test",
    "dirname"
]
def dirname():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)
plat = platform.system()
if plat == "Darwin":
    tfd = ctypes.CDLL(dirname() + "/tinyfiledialogsAppleSilicon.dylib")
elif plat == "Windows":
    tfd = ctypes.CDLL(dirname() + "/tinyfiledialogs64.dll")
elif plat == "Linux":
    tfd = ctypes.CDLL(dirname() + "/tinyfiledialogsLinux86.so")
else:
    raise OSError("idk what dylib i should load")
def message_box(title, message, type="yesno", icon="info", default_button=0):
    """
    Types: ok, okcancel, yesno, yesnocancel
    Icons: info, warning, error, question
    Default button: 0 for cancel/no , 1 for ok/yes , 2 for no in yesnocancel
    """
    return tfd.tinyfd_messageBox(title.encode('utf-8'), message.encode('utf-8'), type.encode(), icon.encode(), default_button)
def beep():
    "sleeps for some time i guess"
    tfd.tinyfd_beep()

tfd.tinyfd_selectFolderDialog.restype = ctypes.c_char_p
def select_folder(title="Select A Folder", defaultpath="/"):
    ada = tfd.tinyfd_selectFolderDialog(title.encode(), defaultpath.encode())
    if ada:
        return ada.decode()
    else:
        return ada
tfd.tinyfd_inputBox.restype = ctypes.c_char_p
def input_box(title="Enter Text", message="Hi", defaultinput=""):
    ada = tfd.tinyfd_inputBox(title.encode(), message.encode(), defaultinput.encode())
    if ada:
        return ada.decode()
    else:
        return ada
def color_chooser(title="Choose", defaulthexrgb="#FF0000", defaultrgb=[255,0,0]):
    # 1. Define the required C type: an array of 3 unsigned bytes (c_ubyte)
    UByte3Array = ctypes.c_ubyte * 3
    
    # 2. Convert the Python list (defaultrgb) into a ctypes array
    #    The '*' unpacks the list elements into the array constructor
    defaultrgb_ctypes = UByte3Array(*defaultrgb)
    
    # 3. Create an empty ctypes array to hold the result (resultrgb)
    #    This array is passed by reference to be filled by the C function
    resultrgb_ctypes = UByte3Array()
    
    # The defaultrgb_ctypes is argument 3 (the one that caused the error)
    # and resultrgb_ctypes is argument 4
    tfd.tinyfd_colorChooser(
        title.encode(),
        defaulthexrgb.encode(),
        defaultrgb_ctypes,  # Correctly formatted ctypes array
        resultrgb_ctypes    # Correctly formatted ctypes array
    )
    
    # OPTIONAL: You may want to return the result as a standard Python list
    return list(resultrgb_ctypes)
# Assuming 'tfd' is the loaded tinyfiledialogs library
tfd.tinyfd_openFileDialog.restype = ctypes.c_char_p
def select_file(title="Select A File", defaultpath="/", filters=["*.png"], singlefilterdesc="All", allowmultipleselects=True):
    # 1. ENCODE the Python strings in the 'filters' list to a list of 'bytes'
    encoded_filters = [f.encode() for f in filters]

    # 2. Define the ctypes array type: Array of Pointers to Character Strings (char *[])
    #    UBytedyArray will now be an array type capable of holding len(filters) pointers
    PCHAR_ARRAY = ctypes.c_char_p * len(encoded_filters)
    
    # 3. Instantiate the array. The constructor accepts a sequence of 'bytes' objects
    #    because c_char_p can be constructed from Python 'bytes'
    filters_ctypes = PCHAR_ARRAY(*encoded_filters)
    
    # 4. Call the C function with the correct arguments
    a = tfd.tinyfd_openFileDialog(
        title.encode(),
        defaultpath.encode(),
        len(encoded_filters),        # Number of filters
        filters_ctypes,              # Array of c_char_p (the pointers)
        singlefilterdesc.encode(),
        allowmultipleselects
    )
    return a.decode().split("|") if a else a
tfd.tinyfd_saveFileDialog.restype = ctypes.c_char_p
def save_file(title="Select A File", defaultpath="/", filters=["*.png"], singlefilterdesc="All"):
    encoded_filters = [f.encode() for f in filters]

    # 2. Define the ctypes array type: Array of Pointers to Character Strings (char *[])
    #    UBytedyArray will now be an array type capable of holding len(filters) pointers
    PCHAR_ARRAY = ctypes.c_char_p * len(encoded_filters)
    
    # 3. Instantiate the array. The constructor accepts a sequence of 'bytes' objects
    #    because c_char_p can be constructed from Python 'bytes'
    filters_ctypes = PCHAR_ARRAY(*encoded_filters)
    return tfd.tinyfd_saveFileDialog(title.encode(), defaultpath.encode(), len(encoded_filters), filters_ctypes, singlefilterdesc.encode())
def test():
    print(save_file())
    print(select_file())
    print(input_box())
    print(select_folder())
    print(color_chooser())
    message_box("Hello", "This is a test message box from tinyfiledialogs.")

if __name__ == "__main__":
    test()