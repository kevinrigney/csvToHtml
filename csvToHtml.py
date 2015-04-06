#! /usr/bin/env python
'''
    Here we have a simple CSV to HTML table maker.
    You come across CSV's a lot in business applications
    and it can be handy to turn them into a reasonably 
    readable format without using Excel or other tools.
    
    It even runs on Windows!
    
    Written by Kevin Rigney
    Last edit 2015-04-05
    Tested and working on:
    Linux (Ubuntu 14.04), Python 2.7.6, Python 3.4.0
    Windows 7, Python 2.7.9    
'''
    
import argparse
import sys
from os import sep

class ColumnError(Exception):
    pass

def htmlHeader(body,title='Table',use_color=False):
    
    html_header = '''
<!DOCTYPE html>
<html>
<head>
\t<title>'''+title+'''</title>\n
<style>
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
th, td {
    padding: 5px;
    text-align: left;
}'''   
   
    if use_color == True:
        html_header = html_header + '''
table#t01 tr:nth-child(even) {
    background-color: #eee;
}
table#t01 tr:nth-child(odd) {
   background-color:#fff;
}
table#t01 th    {
    background-color: #fff;
    color: black;
}
'''
    
    html_header = html_header + '''</style></head>\n<body>\n'''
    
    html_footer = '\n</body>\n</html>\n\n'
    
    return html_header + body + html_footer

def tableItem(item):
    
    item_begin = '\t<td>'
    item_end = '</td>\n' 
    
    return item_begin + str(item) + item_end

def tableColumnName(item):
    
    item_begin = '\t<th>'
    item_end = '</th>\n' 
    
    return item_begin + str(item) + item_end

def tableRow(row):
    
    row_begin = '<tr>\n'
    row_end = '</tr>\n'
    
    return row_begin + str(row) + row_end

def table(rows,title='',style=''):
    
    table_begin = '\n<table id="t01">\n<!-- Table Begin -->\n'
    
    if str(title) != '':
        table_begin = table_begin + '\n<caption style="font-size:30px"><b>'+ str(title) + '</b></caption>\n'
    
    table_end = '\n</table><!-- Table End -->\n'
    
    return table_begin + str(rows) + table_end


def csvToTable(filename,first_row_names = True, field_sep = ',', string_sep = '"',row_format=[],table_name='',comment='#'):    
        
   
    csv_lines = [] # We're going to append to this array
    html_out='' # We're going to append to this string
    
    csv_handle = open(filename)
    
    for line in csv_handle.readlines():
        # Throw out comments
        if not line.startswith(comment):
            csv_lines.append(line)
    csv_handle.close()
  
    
    # Figure out how may columns there are. 
    # TODO This breaks if there is only one row.
    num_columns = len(csv_lines[0].split(string_sep+field_sep+string_sep))
    
    # If the user doesn't specify a custom layout just go across the row.
    # Parse out the first row just for analysis
    if row_format == []:        
        row_format = range(0,num_columns)
        
    # Make sure the user (and our logic above) hasn't specified
    # any row that doesn't exist
    if max(row_format) > (num_columns - 1):
        raise IndexError("Column index " + str(max(row_format)) + " is out-of-bounds")     
        
    if first_row_names == True:
        # Pop is perfect here because the for loop after this iterates over the list.
        # We don't want to have to put extra logic in that loop to handle this case.
        # Check out the comments of the next loop for details on what's goin on here.
        
        first_row = csv_lines.pop(0)        
        this_row = ''        
        split_up = first_row.split(string_sep+field_sep+string_sep) 
                        
        for row_location in row_format:            
            item = split_up[row_location]
            item = item.strip()
            item = item.strip(string_sep)
            this_row = this_row + tableColumnName(item) # THIS IS THE ONLY DIFFERENCE            
        # Make a whole row out of the items    
        html_out = html_out + tableRow(this_row)
        
            
    for row in csv_lines:
        
        this_row = '' # This will be filled with items before a row header is added
        
        # A more robust way of splitting entries. If there is a field_sep
        # somewhere in an entry then it would get split again making
        # too many fields. But if the whitespace is inconsistent between fields
        # this won't work very well... or at all.
        split_up = row.split(string_sep+field_sep+string_sep) 
                
        for row_location in row_format:
            
            # Get the item we need
            item = split_up[row_location]
            # Remove any whitespace
            item = item.strip()
            #Now remove our seperator if it got left over (happens on first and last every time)
            item = item.strip(string_sep)
            
            # Add it to the string
            this_row = this_row + tableItem(item)
            
        # Make a whole row out of the items    
        html_out = html_out + tableRow(this_row)
        
        
    html_out = table(html_out,title=table_name)
    return html_out

if __name__ == '__main__':
    
    ap_epilog='''
    Known Bugs:
    When using stdin the number of columns can never change. It must always be the
    same as the first row''' 
    
    parser = argparse.ArgumentParser(description='Convert a CSV file to a HTML table',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog=ap_epilog)
    
    parser.add_argument('--page-title',default='Table',help='The title of the wepbage (not printed on the actual page)')
    parser.add_argument('--table-title',default=None,nargs='*',help='List of titles of the tables. If no title is specified the table filename is used. If titles are specified there must be as many titles as there are tables.')
    parser.add_argument('--no-color',action='store_true',help='Turn off colors')
    parser.add_argument('--field-sep',default=',',help='The character seperating values')
    parser.add_argument('--string-sep',default='"',help='The character surrounding a value')
    parser.add_argument('--comment-char',default='#',help='''If a line in the file leads with this character it's ignored''')
    parser.add_argument('--extension',default='.csv',help='If you use --use-title with no arguments this extension will be removed from the title of the table')

    parser.add_argument('--row-format',default=[],nargs='+',type=int,help='The layout of a row. You can map csv columns to different html table \
                        columns. Start at 0. An example: If your csv has 5 columns and you want the table to print them backward you would \
                         type "--row-format 4 3 2 1 0"')

    # With linux we have pipes. With windows... we don't
    if sys.platform.startswith('linux'):
        parser.add_argument('--output-file',default='/dev/stdout',help='Where to save the table')
        parser.add_argument('input',nargs='*',default='/dev/stdin',help='List of input files')
    else:
        parser.add_argument('--output-file',required=True,help='Where to save the table')
        parser.add_argument('input',nargs='*',help='List of input files')
        
    args = parser.parse_args()        
    table_out = ''
   
    # If you don't specify an input file args.input
    # won't be a list, it will be a string. Then the for loop
    # will iterate over every character of the string and that's no good.
    # So we make it a list.
    if type(args.input) != list:
        args.input = [args.input]
            
    num_files = len(args.input)
        
    if args.table_title == []:
        # Make sure we can actually figure out a meaningful file name
        if args.input != '/dev/stdin':        
            # Figure out what the file name is            
            for filename in args.input:                       
                # If they set it to '' then they don't want us stripping an extension
                if args.extension != '':
                    extension_location = filename.rfind(args.extension)
                    # Make sure we found it at the end
                    if extension_location != -1 and (len(args.extension) == (len(filename) - extension_location)):
                        filename = filename[0:extension_location]
                
                # Now only take the last part
                filename = filename.split(sep)[-1]
                
                # And add it to the list
                args.table_title.append(filename)
        else:
            # Because they are using a pipe we can't get a worthwile name.
            # Don't make table titles
            args.table_title = None
            
    elif args.table_title is None:
        # Use ''
        args.table_title = []
        while num_files > len(args.table_title):
            args.table_title.append('')
    
    # Make sure there are as many titles as there are files    
    if len(args.input) > len(args.table_title):
        raise IndexError('''Either you didn't specify enough titles or something went wrong in the program logic''')

    for item in range(0,num_files):

        table_out = table_out + csvToTable(args.input[item],
                                           field_sep=args.field_sep,
                                           string_sep=args.string_sep,
                                           row_format=args.row_format,
                                           comment=args.comment_char,
                                           table_name=args.table_title[item])
        table_out = table_out + '<br><!-- Table line break -->\n'
        
    output_handle = open(args.output_file,'w') # TODO Build in nicer handling if the output file can't be created. Maybe write to /tmp or the console
    output_handle.write(htmlHeader(table_out,title=args.page_title,use_color=(not args.no_color)))
    output_handle.close()
        
        

    
    
