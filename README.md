This script takes a zip file as input and creates a tree of files containing
the same raw data as they have in the zip file, but in a way that is usable.
So for example if a file is compressed with deflate, it will take that raw
deflate data and slap a gzip header and footer around it.
