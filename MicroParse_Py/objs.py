from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    ''' Extension of the HTMLParser '''


    def handle_data(self, data):
        if len(data) > 1:
            htmldata.write('::DATA: ' + data + '\n')
            
    def handle_starttag(self, tag, attrs):
        htmldata.write('Item: \n')
        htmldata.write('::TAG: ' + tag + '\n')
        for attr in attrs:
            if len(attr)<2:
                htmldata.write('\t' + attr + '\n')
            else:
                st1 = attr[0]
                st2 = attr[1]
                htmldata.write('\t' + st1 + ' = ' + st2 + '\n')  