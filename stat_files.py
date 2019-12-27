# import os
# import math
# from pathlib import Path
# from typing import List
# from humanize import naturalsize as nsize


# def get_files(in_dir: Path) -> List[str]:
#     """Finds files and empty directories in the given path,
#     and collects them into a list of FileInfo objects.

#     Parameters
#     ----------
#     files : str
#         Directory of files, or text file with list of files to convert.

#     Returns
#     -------
#     file_list : List[str]
#         List of files to be converted.
#     """
#     # Type declarations
#     file_list: List[str] = []

#     # Traverse given path, collect results.
#     # tqdm is used to show progress of os.walk
#     if in_dir.is_dir():
#         for root, _, files in os.walk(in_dir, topdown=True):
#             for file in files:
#                 file_list.append(Path(root, file))

#     return file_list


# conv_files: List[str] = get_files(
#     Path("/home/jnik/Documents/archive_data/batch_3/conv_files")
# )

# org_files: List[str] = get_files(
#     Path("/home/jnik/Documents/archive_data/batch_3/org_files")
# )
# out_file: Path = Path("/home/jnik/Documents/file_sizes.csv")

# with out_file.open("w", encoding="utf-8") as f:
#     f.write("File|Original Size|Converted Size|Difference %\n")
#     for cfile in conv_files:
#         cpath = Path(cfile.parent.parent.stem, cfile.parent.stem, cfile.stem)
#         csize = cfile.stat().st_size
#         for ofile in org_files:
#             opath = Path(
#                 ofile.parent.parent.stem, ofile.parent.stem, ofile.stem
#             )
#             osize = ofile.stat().st_size
#             if cpath == opath:
#                 diff = (csize - osize) / ((osize + csize) / 2) * 100

#                 f.write(
#                     f"{opath}|{nsize(osize)}|
# {nsize(csize)}|{round(diff,2)}\n"
#                 )
