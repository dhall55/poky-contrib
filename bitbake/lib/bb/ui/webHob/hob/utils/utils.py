def _size_to_string(size):
    try:
        if not size:
            size_str = "0 B"
        else:
            if len(str(int(size))) > 6:
                size_str = '%.1f' % (size*1.0/(1024*1024)) + ' MB'
            elif len(str(int(size))) > 3:
                size_str = '%.1f' % (size*1.0/1024) + ' KB'
            else:
                size_str = str(size) + ' B'
    except:
        size_str = "0 B"
    return size_str

def _string_to_size(str_size):
    try:
        if not str_size:
            size = 0
        else:
            unit = str_size.split()
            if len(unit) > 1:
                if unit[1] == 'MB':
                    size = float(unit[0])*1024*1024
                elif unit[1] == 'KB':
                    size = float(unit[0])*1024
                elif unit[1] == 'B':
                    size = float(unit[0])
                else:
                    size = 0
            else:
                size = float(unit[0])
    except:
        size = 0
    return size