from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTabBar,QMessageBox,QAbstractItemView,QListWidget

# QT6
try :
    Dialog = Qt.WindowType.Dialog
    WindowCloseButtonHint = Qt.WindowType.WindowCloseButtonHint
    WindowTitleHint = Qt.WindowType.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint
    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Unchecked
    ItemIsEditable = Qt.ItemFlag.ItemIsEditable
    ItemIsEnabled = Qt.ItemFlag.ItemIsEnabled
    ItemIsSelectable = Qt.ItemFlag.ItemIsSelectable
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    ItemIsUserCheckable = Qt.ItemFlag.ItemIsUserCheckable
    MatchExactly = Qt.MatchFlag.MatchExactly
    RightSide = QTabBar.ButtonPosition.RightSide
    LeftSide = QTabBar.ButtonPosition.LeftSide
    Warning = QMessageBox.Icon.Warning
    YesRole = QMessageBox.ButtonRole.YesRole
    AcceptRole = QMessageBox.ButtonRole.AcceptRole
    NoSelection = QAbstractItemView.SelectionMode.NoSelection
    CustomContextMenu = Qt.ContextMenuPolicy.CustomContextMenu
    WaitCursor = Qt.CursorShape.WaitCursor
    Horizontal = Qt.Orientation.Horizontal
    red = Qt.GlobalColor.red
    DisplayRole = Qt.ItemDataRole.DisplayRole
    WA_DeleteOnClose = Qt.WidgetAttribute.WA_DeleteOnClose
    NoEditTriggers = QAbstractItemView.EditTrigger.NoEditTriggers
# QT5
except :
    Dialog = Qt.Dialog
    WindowCloseButtonHint = Qt.WindowCloseButtonHint
    WindowTitleHint = Qt.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowStaysOnTopHint
    Checked = Qt.Checked
    Unchecked = Qt.Unchecked
    ItemIsEditable = Qt.ItemIsEditable
    ItemIsEnabled = Qt.ItemIsEnabled
    ItemIsSelectable = Qt.ItemIsSelectable
    AlignCenter = Qt.AlignCenter
    ItemIsUserCheckable = Qt.ItemIsUserCheckable
    MatchExactly = Qt.MatchFlag.MatchExactly
    RightSide = QTabBar.RightSide
    LeftSide = QTabBar.LeftSide
    Warning = QMessageBox.Warning
    YesRole = QMessageBox.YesRole
    AcceptRole = QMessageBox.AcceptRole
    NoSelection = QListWidget.NoSelection
    CustomContextMenu = Qt.CustomContextMenu
    WaitCursor = Qt.WaitCursor
    Horizontal = Qt.Horizontal
    red = Qt.red
    DisplayRole = Qt.DisplayRole
    WA_DeleteOnClose = Qt.WA_DeleteOnClose
    NoEditTriggers = QAbstractItemView.NoEditTriggers