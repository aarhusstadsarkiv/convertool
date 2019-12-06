"""Tool for reading and converting ods files.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# import pyexcel_ods
# import pyexcel
import subprocess
import pyautogui
import time

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


# def read_ods(input: None) -> None:
#     """Description

#     Parameters
#     ----------
#     param : type
#         desc

#     Returns
#     -------
#     return : type
#         desc

#     Raises
#     ------
#     BadError

#     """
#     recs = pyexcel_ods.get_data(
#         "/home/jnik/Documents/test_data/test_sheet.ods"
#     )
#     for rec in recs:
#         print(rec)
#     print(recs["Daglig"])
subprocess.Popen(
    "libreoffice /home/jnik/Documents/test_data/test_3.ods", shell=True
)
time.sleep(3)
pyautogui.press("f3")
time.sleep(2)
scale_coords = pyautogui.locateOnScreen(
    "/home/jnik/Documents/scaling_mode.png"
)
print(scale_coords)
time.sleep(1)
scale_x = scale_coords.left + scale_coords.width + 10
scale_y = pyautogui.center(scale_coords).y
pyautogui.click(scale_x, scale_y)
print(pyautogui.center(scale_coords))
pyautogui.moveTo(scale_x, scale_y - 100)
