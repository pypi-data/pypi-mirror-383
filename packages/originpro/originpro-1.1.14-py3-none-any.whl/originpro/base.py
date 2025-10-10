"""
originpro
A package for interacting with Origin software via Python.
Copyright (c) 2020 OriginLab Corporation
"""
# pylint: disable=C0103,C0301,R0913
import abc
import xml.etree.ElementTree as ET
from .config import po, oext, _EXIT, _OBJS_COUNT
from .utils import origin_class, get_file_ext, _tree_to_dict, lt_empty_tree, ocolor, to_rgb
from .dc import Connector

def _DC_from_ext(ext):
    if ext in ['.csv', '.asc', '.txt', '.dat']:
        return 'csv'
    if ext in ['.xls', '.xlsx']:
        return 'excel'

    raise ValueError('file type not supported, must be text or Excel files')


class BaseObject:
    """base class for all Origin objects"""
    def __init__(self, obj):
        if oext:
            _OBJS_COUNT[0] += 1
        if obj is None:
            raise TypeError
        self.obj = obj
        #print('constructor for ' + str(type(self.obj).__name__))
    def __del__(self):
        if oext:
            _OBJS_COUNT[0] -= 1
            if _EXIT[0] and not _OBJS_COUNT[0]:
                po.Detach()
    def __str__(self):
        return self.obj.GetName()
    def __bool__(self):
        if self.obj is None:
            return False
        return self.obj.IsValid()
    def index(self):
        """
        interal index in corresponding collection of the object
        Parameters:
            none
        Returns:
            interal index
        Examples:
            wks1 = op.new_sheet()
            print(wks1.index())
        """
        return self.obj.GetIndex()
    def get_str(self, prop):
        """
        Get object's LabTalk string property
        Parameters:
            prop(string): string prop like
            [cmap.palette, colorlist,  name], details on Origin objects' reference pages
        Returns:
            object's string property
        Examples:
            wks1 = op.new_sheet()
            print(wks1.get_str('name'))
        """
        return self.obj.GetStrProp(prop)
    def get_int(self, prop):
        """
        Get object's LabTalk int property
        Parameters:
            prop(string):int prop like
            [cmap.stretchpal, cmap.linkpal symbol.kind], details on Origin objects' reference pages
        Returns:
            object's int property
        Examples:
            wks1 = op.new_sheet()
            print(wks1.get_int('nrows'))
        """
        try:
            return int(self.get_float(prop))
        except ValueError:
            return 0
    def get_float(self, prop):
        """
        Get object's LabTalk float property
        Parameters:
            prop(string): float prop like symbol.size, details on Origin objects' reference pages
        Returns:
            object's float property
        Examples:
            p=op.find_graph()[0].plot_list()[0]
            print(p.get_float('symbol.size'))
        """
        return self.obj.GetNumProp(prop)
    def set_str(self, prop, value):
        """
        Set object's LabTalk string property
        Parameters:
            prop(string):can be int/float/string property, details on Origin objects' reference pages
            value:property value
        Returns:
            none
        Examples:
            wks1 = op.new_sheet()
            wks1.set_str('name','test_set_str')
        """
        self.obj.SetStrProp(prop, value)
    def set_int(self, prop, value):
        """
        Set object's LabTalk int property
        Parameters:
            prop(string):prop string, details on Origin objects' reference pages
            value:property value
        Returns:
            none
        Examples:
            wks1 = op.new_sheet()
            wks1.set_int('nrows', 10)

        """
        self.obj.SetNumProp(prop, int(value))
    def set_float(self, prop, value):
        """
        Set object's LabTalk float property
        Parameters:
            prop(string):prop string, details on Origin objects' reference pages
            value:property value
        Returns:
            none
        Examples:
            p=op.find_graph()[0].plot_list()[0]
            p.set_float('symbol.size', 4.5)
        """
        self.obj.SetNumProp(prop, value)
    def method_int(self, name, arg=''):
        """
        execute object's LabTalk method that has an int return
        Parameters:
            name(string):prop string, details on Origin objects' reference pages
            arg:property value
        Returns:
            (int)LabTalk method's return value
        Examples:
            wks1 = op.find_sheet()
            issel = wks1.method_int('isColSel', '3') #return if 3rd col is selected
        """
        try:
            return int(self.method_float(name, arg))
        except ValueError:
            return 0
    def method_float(self, name, arg=''):
        """
        execute object's LabTalk method that has a float return
        Parameters:
            name(string):prop string, details on Origin objects' reference pages
            arg:property value
        Returns:
            (float)LabTalk method's return value
        Examples:
            wks1 = op.new_sheet()
            rowid=wks1.method_float('UserParam', '++test') #add user parameter row "test", and return its index on worksheet

        """
        return self.obj.DoMethod(name, arg)
    def method_str(self, name, arg=''):
        """
        execute object's LabTalk method that has a string return
        Parameters:
            name(string):prop string, details on Origin objects' reference pages
            arg:property value
        Returns:
            (string)LabTalk method's return value
        Examples:
            wks = op.new_sheet()
            row, col = 1,1
            wks.set_cell_note(row,col,'test Note')
            cnote = wks.method_str('GetNote',f'{row+1},{col+1}')

        """
        return self.obj.DoStrMethod(name, arg)

    def lt_exec(self, labtalk):
        r"""
        executes a LabTalk statement.

        Parameters:
            labtalk (str): LabTalk statement

        Returns:
            None

        Examples:
            wb.lt_exec('page.longname$="lt_exec example"')
            wks.lt_exec(r'expASC path:="c:\test\signal.csv";') #you can execute X-Function here

        """
        self.obj.LT_execute(labtalk)

    @property
    def name(self):
        """
        short name of the object
        Parameters:
            none
        Returns:
            Origin object name
        Examples:
            gl=op.find_graph()[0]
            print(gl.name)
        """
        return self.obj.GetName()
    @name.setter
    def name(self, value):
        """
        change the short name of an object, if there is a conflict,
        Origin will change to next available name automatically
        Examples:
            gp=op.new_graph()
            gp.name='Test'
            gp=op.new_graph()
            gp.name='Test'
            print(gp)#Test1
        """
        self.obj.SetName(value)
    @property
    def lname(self):
        """
        Property getter returns long name of object.

        Parameters:

        Returns:
            (str)

        Examples:
            print(wb.lname)
        """
        return self.obj.GetLongName()
    @lname.setter
    def lname(self, value):
        """
        Property setter sets long name of object.

        Parameters:
            value (str): long name

        Returns:
            None

        Examples:
            wb.lname = 'My Data'
        """
        self.obj.SetLongName(value)
    @property
    def comments(self):
        """
        Property getter returns long name of object.
        Parameters:
            none
        Returns:
            long name of object.
        Examples:
            wb.comments='My labs data'
            print(wb.comments)
        """
        return self.get_str('comments')
    @comments.setter
    def comments(self, value):
        """
        Property setter sets the comments of an object.
        Parameters:
            value(string):content of comments
        Returns:
            none
        Examples:
            wb.comments='My labs data'
            print(wb.comments)
        """
        self.set_str('comments', value)
    @property
    def show(self):
        """
        Property getter returns show state of object.

        Parameters:

        Returns:
            (bool)

        Examples:
            print(wb.show)
        """
        return bool(self.obj.GetShow())
    @show.setter
    def show(self, value):
        """
        Property setter sets show state of object.

        Parameters:
            value (bool): True to show object

        Returns:
            None

        Examples:
            wb.show = True
        """
        self.obj.SetShow(value)

    @property
    def usertree(self):
        """
            Return User Tree as ElementTree
        Parameters:
            none
        Returns:
            ElementTree
        Examples:
            wks = op.new_sheet()
            wks.set_str('tree.data.name', 'Larry')
            wks.set_int('tree.data.age', 37)
            wks.set_float('tree.data.mean', 23.56)

            trWks = wks.usertree
            trData = trWks.find('data')
            for child in trData:
                print(f'{child.tag} = {child.text}')
        """
        s = self.get_str('tree')
        if not s:
            return lt_empty_tree()
        return ET.fromstring(s)

    @usertree.setter
    def usertree(self, tr):
        """
            Set User Tree

        Parameters:
            tr (ElementTree): tree to set
        Returns:
            none
        Examples:
            import xml.etree.ElementTree as ET
            wks = op.new_sheet()
            tr = wks.usertree
            data = ET.SubElement(tr, 'data')
            version = ET.SubElement(data, 'Version')
            version.set('Label', 'Origin Version')
            version.text = '9.8b'
            wks.usertree = tr
        """
        self.set_str('tree', ET.tostring(tr, encoding='unicode'))

    @property
    def userprops(self):
        """
        Parameters:
            none
        Returns:
            Return User Tree as dict
        Examples:
            wks = op.new_sheet()
            wks.set_str('tree.data.name', 'Larry')
            wks.set_int('tree.data.age', 37)
            wks.set_float('tree.data.mean', 23.56)

            dd = wks.userprops['data']
            print(dd)

        """
        dd = {}
        tr = self.usertree
        if tr:
            for node in tr:
                _tree_to_dict(dd, node)
        return dd

    #@userprops.setter
    #def userprops(self, value):
        #pass


class GObject(BaseObject):
    """
    This class represents an instance of a text object on a GLayer.
    """
    def __init__(self, obj, layer):
        self.layer=layer
        super().__init__(obj)

    def remove(self):
        """
        Deletes label.
        Parameters:
            none
        Returns:
            None
        Examples:
            gl=op.find_graph()[0]
            label = gl.label('xb')
            label.remove()
        """
        self.obj.Destroy()

    # def __repr__(self) -> str:
        # if self.obj.IsValid():
            # return f'Label named {self.name} in [{self.layer.GetParent().Name}]{self.layer.Name}'
        # else:
            # raise RuntimeError('label no longer exists')

    @property
    def color(self):
        """
        Property getter returns the RGB color of the text object as a tuple (Red, Green, Blue)

        Parameters:

        Returns:
            (tuple) r,g,b

        Examples:
            label = g[0].label('text')
            red, green, blue = label.color
        """
        orgb = self.get_int('color')
        return to_rgb(orgb)

    @color.setter
    def color(self, rgb):
        """
        Property setter for the RGB color of the text object

        Parameters:
            rgb(int, str, tuple): various way to specify color, see function ocolor(rgb) in op.utils

        Returns:
            None

        Examples:
            label = g[0].label('text')
            label.color = 'Red'
            label.color = 3            # 'Green'
            label.color = '#00f'       # 'blue'
            label.color = '#0000ff'    # 'blue'
            label.color = [0, 255, 0]  # 'green'
        """
        self.set_int('color', ocolor(rgb))


class Label(GObject):
    @property
    def text(self) -> str:
        """
        Property getter for object text.

        Parameters:

        Returns:
            (str) Object text
        Examples:
            gl=op.find_graph()[0]
            label = gl.label('xb')
            print(label.text)
        """
        return self.obj.Text

    @text.setter
    def text(self, text: str) -> str:
        """
        Property setter for object text.

        Parameters:
            value (str): Text

        Returns:
            (str) Object text
        Examples:
            gl=op.find_graph()[0]
            label = gl.label('yl')
            label.text='123'
        """
        self.obj.Text = text
        return self.text


class Line(GObject):
    @property
    def width(self):
        return self.get_float('linewidth')

    @width.setter
    def width(self, val):
        return self.set_float('linewidth', val)

    @property
    def type(self):
        return self.get_int('linetype')

    @type.setter
    def type(self, val):
        return self.set_int('linetype', val)


class BaseLayer(BaseObject):
    """base class for all Origin layers"""
    def __str__(self):
        graph = self.obj.GetParent()
        return f'[{graph.GetName()}]{self.obj.GetName()}'

    def activate(self):
        """
        make layer/sheet active
        Parameters:
            none
        Returns:
            last_active layer index
        Examples:
            wks = op.find_sheet()
            wb = wks.get_book()
            wb.add_sheet()
            wks.activate()
        """
        page = BasePage(self.obj.GetParent())
        if not page.is_active():
            page.activate()
        last_act = page.get_int('Active')
        page.set_int('Active', self.index()+1)
        return last_act

    def destroy(self):
        """
        delete the sheet/layer
        Parameters:
            none
        Returns:
            none
        Examples:
            wks1=op.new_sheet()
            wks1.destroy()

        """
        self.obj.Destroy()

    def label(self, name):
        """
        Get a Label instance by name.

        Parameters:
            name (str): name of the label to be attached
        Returns:
            (Label)

        Examples:
            g = op.new_graph()
            g[0].label('XB').remove()
        """
        lb = self.obj.GraphObjects(name)
        if lb is None:
            return None
        return Label(lb, self.obj)

    def remove_label(self, label):
        """
        Remove a label from a layer.

        Parameters:
            label (Label or str): Instance of Label or name of label to remove

        Returns:
            None

        Examples:
            g = op.new_graph()
            g[0].remove_label('xb') # g[0] is 1st layer.
        """
        if isinstance(label, Label):
            label.remove()
        elif isinstance(label, str):
            self.remove_label(self.label(label))
        else:
            raise TypeError('"label"" must ba an instance of either str or Label.')

    def add_label(self, text, x=None, y=None):
        """
        Add a label to a layer.

        Parameters:
            text (str): The text of a text label
            x(float or None): The X coordinate of the left of the object
            y(float or None): The Y coordinate of the top of the object

        Returns:
            (Label)

        Examples:
            gp = op.new_graph()
            gl = gp[0]
            text = gl.add_label("hello", 4, 8)
            text.text = 'world'
        """
        textobj = self.obj.GraphObjects.Add(2)
        if textobj:
            label = Label(textobj, self.obj)
            label.set_int('attach', 0)
            label.text = text
            x1 = x if x else (self.get_float('x.from') + self.get_float('x.to')) /2
            y1 = y if y else (self.get_float('y.from') + self.get_float('y.to')) /2
            label.set_float('x1', x1)
            label.set_float('y1', y1)
            return label
        return None

    def add_line(self, x1, y1, x2, y2):
        """
        Add a line to a layer.

        Parameters:
            x1(float or None): The begin X coordinate
            y1(float or None): The brgin Y coordinate
            x2(float or None): The end X coordinate
            y2(float or None): The end Y coordinate

        Returns:
            (Line)

        Examples:
            gp = op.new_graph()
            gl = gp[0]
            line = gl.add_line(5, 5, 6, 8)
            line.width = 5
            line.set_int('arrowendshape', 2)
        """
        lineobj = self.obj.GraphObjects.Add(4)
        if lineobj:
            line = Line(lineobj, self.obj)
            line.set_int('attach', 2)
            line.set_float('x1', x1)
            line.set_float('y1', y1)
            line.set_float('x2', x2)
            line.set_float('y2', y2)
            return line
        return None

class BasePage(BaseObject):
    """
    base class for all Origin books and graph, it holds a PyOrigin Page
    """
    def __len__(self):
        return self.obj.Layers.GetCount()

    def is_open(self):
        """
        Returns whether book is neither hidden, nor minimized.

        Parameters:

        Returns:
            (bool)

        Examples:
            b = wb.is_open()
        """
        return self.get_int('Win') > 2

    def is_active(self):
        """
        Returns whether book is currently active
        Parameters:
            none
        Returns:
            bool that indicate if the book is active
        Examples:
            wb=op.new_book()
            print(wb.is_active())

        """
        act_name = po.LT_get_str('%H')
        return act_name == self.name

    def lt_range(self):
        """
        Parameters:
            none
        Returns:
            return the Origin Range String that iddentify page object
        Examples:
            wb=op.new_book()
            print(wb.lt_range())

        """
        return f'[{self.obj.GetName()}]'

    def activate(self):
        """
        make page active
        Parameters:
            none
        Returns:
            none
        Examples:
            wb = op.find_book('w', 'Book2')
            wb.activate()
        """
        po.LT_execute(f'win -a {self.obj.GetName()}')

    def destroy(self):
        """
        Destroy the window
        Parameters:
            none
        Returns:
            none
        Examples:
            wb=op.new_book()
            wb.destroy()
        """
        po.LT_execute(f'win -cd {self.obj.GetName()}')

    def duplicate(self):
        """
        duplicate the window
        Parameters:
            none
        Returns:
            the newly created window object
        Examples:
            wb=op.new_book()
            wbDuplicate=wb.duplicate()

        """
        self.lt_exec('win -d')
        return self.__class__(list(po.GetPages())[-1])


class DBook(BasePage):
    """base class for data books, like workbook and matrix book"""
    def __repr__(self):
        return f'{type(self).__name__}: ' + self.lt_range()

    def _get_book_type(self):
        if isinstance(self.obj, origin_class('WorksheetPage')):
            return 'w'
        if isinstance(self.obj, origin_class('MatrixPage')):
            return 'm'
        raise ValueError('wrong object type')

    def __getitem__(self, index):
        return self._sheet(self.obj.Layers(index))

    def __iter__(self):
        for elem in self.obj.Layers:
            yield self._sheet(elem)

    def _add_sheet(self, name, active):
        obj1 = self.obj.AddLayer(name)
        if active:
            self.set_int("active", obj1.GetIndex()+1)
        return obj1

    @abc.abstractmethod
    def _sheet(self, obj):
        raise ValueError(f'{self.lt_range()} Derived class must define its own _sheet method!')

def _layer_range(obj, use_name):
    return f'[{obj.GetParent().GetName()}]{obj.GetName() if use_name else obj.GetIndex() + 1}'

class DSheet(BaseLayer):
    """base class for data sheets, like worksheets and matrix sheets"""
    def __str__(self):
        return self.lt_range()
    def __repr__(self):
        return f'{type(self).__name__}: ' + self.lt_range()
    def _get_book(self):
        return self.obj.GetParent()

    @property
    def shape(self):
        """
        Parameters:
            none
        Returns:
            (tuple) return the rows and columns of a sheet
        Examples:
            wks=op.find_sheet()
            print(wks.shape)
        """
        return self.obj.GetRowCount(), self.obj.GetColCount()
    @shape.setter
    def shape(self, val):
        """
        setting the number of rows and columns in a sheet
        Parameters:
            val (tuple): rows, cols, 0 = unchanged
        Returns:
            (tuple) the new shape
        Examples:
            wks=op.find_sheet()
            #leave rows unchanged and set to 3 columns
            wks.shape=0,3
        """
        if not isinstance(val, (tuple, list)) or len(val) != 2:
            raise ValueError('must set by rows, cols')
        rows, cols = val

        if isinstance(self.obj, origin_class('Matrixsheet')):
            if cols <= 0 or rows <= 0:
                raise ValueError('setting matrix sheet shape must provde both rows and cols')
            self.obj.SetShape(rows,cols)
        else:
            if cols > 0:
                self.obj.SetColCount(cols)
            if rows > 0:
                self.obj.SetRowCount(rows)

        return self.shape

    def remove_DC(self):
        """
        Removes Data Connector from a sheet.

        Parameters:

        Returns:
            None

        Examples:
            wks.remove_DC()
        """
        self.obj.LT_execute('wbook.dc.Remove()')

    def has_DC(self):
        """
        Returns whether a sheet has a Data Connector.

        Parameters:

        Returns:
            (str) name of the Data Connector, like 'csv', 'excel'

        Examples:
            dc = wb.has_DC()
            if len(dc):
                print(f'sheet is connected using {dc}')
        """
        if self.obj.GetNumProp('HasDC')==0:
            return ''
        dc_file = self.get_book().get_str('DC.Type')
        type_ = dc_file.split('_',2)[0]
        return type_.lower()

    def from_file(self, fname, keep_DC=True, dctype='', sel='', sparks=False):
        r"""
        Imports data from a file using a Data Connector.

        Parameters:
            fname (str): File path and name to import.
            keep_DC (bool): Keep the Data Connector in the book after import
            dctype (str): Data Connector name, like "Import Filter", "MATLAB", "NetCDF", if not specified, CSV or Excel connector will be used based on file name
            sel (str): selection in the file, this will depend on the connector
            sparks (bool): Allows sparklines or not, True will follow GUI setting to add sparklines, False will disable it completely
        Returns:
            None

        Examples:
            wks=op.find_sheet()
            fn=op.path('e') + 'Samples\\Import and Export\donations.csv'
            wks.from_file(fn, False)#remove connector after import to allow further edit of data
            wks2=op.new_sheet()
            wks2.from_file(op.path()+'test.xlsx')#assuming you have this in UFF(user files folder)
        """
        ext = get_file_ext(fname)
        DC = dctype if dctype else _DC_from_ext(ext)
        dc = Connector(self, DC, keep_DC)
        return dc.imp(fname, sel, sparks)

    def lt_range(self, use_name=True):
        """
        Parameters:
            use_name(bool):
        Returns:
            Return the Origin Range String that identify Data Sheet object
        Examples:
            ws=op.find_sheet()
            print(ws.lt_range())

        """
        return _layer_range(self.obj, use_name)

    @abc.abstractmethod
    def get_book(self):
        'Must be implemented by dervied methods'
        raise ValueError(f'{self.lt_range()} Derived class must define its own get_book method!')

    @abc.abstractmethod
    def get_labels(self, type_ = 'L'):
        'get_labels'

    @abc.abstractmethod
    def set_labels(self, labels, type_ = 'L', offset=0):
        'set_labels'

    @property
    def tabcolor(self):
        """
        Parameters:
            none
        Returns:
            returns the LabTalk color code of the sheet tab
            If sheet tab has no custom color 0 will be returned
        Examples:
            cc = wks.tabcolor
            if cc:
                r, g, b = op.to_rgb(cc)
        """
        ltcolor = self.get_int('TabColor')
        return ltcolor

    @tabcolor.setter
    def tabcolor(self, rgb):
        """
        Property setter for the sheet tab color, use 0 to clear

        Parameters:
            rgb(int, str, tuple): various way to specify color, see function ocolor(rgb) in op.utils

        Returns:
            None

        Examples:
            wks.tabcolor = 'Red'
            wks.tabcolor = '#00f'
            wks.tabcolor = 0
        """
        self.set_int('TabColor', ocolor(rgb))
