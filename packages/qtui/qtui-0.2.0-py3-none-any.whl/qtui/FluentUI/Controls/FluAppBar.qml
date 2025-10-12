pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import FluentUI

Rectangle{
    property string title: ""
    property string darkText : qsTr("Dark")
    property string lightText : qsTr("Light")
    property string minimizeText : qsTr("Minimize")
    property string restoreText : qsTr("Restore")
    property string maximizeText : qsTr("Maximize")
    property string closeText : qsTr("Close")
    property string stayTopText : qsTr("Sticky on Top")
    property string stayTopCancelText : qsTr("Sticky on Top cancelled")
    property color textColor: FluTheme.fontPrimaryColor
    property color minimizeNormalColor: FluTheme.itemNormalColor
    property color minimizeHoverColor: FluTheme.itemHoverColor
    property color minimizePressColor: FluTheme.itemPressColor
    property color maximizeNormalColor: FluTheme.itemNormalColor
    property color maximizeHoverColor: FluTheme.itemHoverColor
    property color maximizePressColor: FluTheme.itemPressColor
    property color closeNormalColor: Qt.rgba(0,0,0,0)
    property color closeHoverColor: Qt.rgba(251/255,115/255,115/255,1)
    property color closePressColor: Qt.rgba(251/255,115/255,115/255,0.8)
    property bool showDark: false
    property bool showClose: true
    property bool showMinimize: true
    property bool showMaximize: true
    property bool showStayTop: true
    property bool titleVisible: true
    property url icon
    property int iconSize: 20
    property bool isMac: FluTools.isMacos()
    property color borerlessColor : FluTheme.primaryColor
    property alias buttonStayTop: btn_stay_top
    property alias buttonMinimize: btn_minimize
    property alias buttonMaximize: btn_maximize
    property alias buttonClose: btn_close
    property alias buttonDark: btn_dark
    property alias layoutMacosButtons: layout_macos_buttons
    property alias layoutStandardbuttons: layout_standard_buttons
    property var maxClickListener : function(){
        if(FluTools.isMacos()){
            if (d.win.visibility === Window.FullScreen)
                d.win.showNormal()
            else
                d.win.showFullScreen()
        }else{
            if (d.win.visibility === Window.Maximized)
                d.win.showNormal()
            else
                d.win.showMaximized()
            d.hoverMaxBtn = false
        }
    }
    property var minClickListener: function(){
        if(d.win.transientParent != null){
            d.win.transientParent.showMinimized()
        }else{
            d.win.showMinimized()
        }
    }
    property var closeClickListener : function(){
        d.win.close()
    }
    property var stayTopClickListener: function(){
        if(d.win instanceof FluWindow){
            d.win.stayTop = !d.win.stayTop
        }
    }
    property var darkClickListener: function(){
        if(FluTheme.dark){
            FluTheme.darkMode = FluThemeType.Light
        }else{
            FluTheme.darkMode = FluThemeType.Dark
        }
    }
    id:control
    color: Qt.rgba(0,0,0,0)
    height: visible ? 30 : 0
    opacity: visible
    z: 65535
    Item{
        id:d
        property var hitTestList: []
        property bool hoverMaxBtn: false
        property var win: Window.window
        property bool stayTop: {
            if(d.win instanceof FluWindow){
                return d.win.stayTop
            }
            return false
        }
        property bool isRestore: win && Window.Maximized === win.visibility
        property bool resizable: win && !(win.height === win.maximumHeight && win.height === win.minimumHeight && win.width === win.maximumWidth && win.width === win.minimumWidth)
        function containsPointToItem(point,item){
            var pos = item.mapToGlobal(0,0)
            var rect = Qt.rect(pos.x,pos.y,item.width,item.height)
            if(point.x>rect.x && point.x<(rect.x+rect.width) && point.y>rect.y && point.y<(rect.y+rect.height)){
                return true
            }
            return false
        }
    }
    Row{
        anchors{
            verticalCenter: parent.verticalCenter
            left: control.isMac ? undefined : parent.left
            leftMargin: control.isMac ? undefined : 10
            horizontalCenter: control.isMac ? parent.horizontalCenter : undefined
        }
        spacing: 10
        Image{
            width: control.iconSize
            height: control.iconSize
            visible: status === Image.Ready ? true : false
            source: control.icon
            anchors.verticalCenter: parent.verticalCenter
        }
        FluText {
            text: control.title
            visible: control.titleVisible
            color:control.textColor
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    Component{
        id:com_macos_buttons
        RowLayout{
            FluImageButton{
                Layout.preferredHeight: 12
                Layout.preferredWidth: 12
                normalImage: "../Image/btn_close_normal.png"
                hoveredImage: "../Image/btn_close_hovered.png"
                pushedImage: "../Image/btn_close_pushed.png"
                visible: control.showClose
                onClicked: control.closeClickListener()
            }
            FluImageButton{
                Layout.preferredHeight: 12
                Layout.preferredWidth: 12
                normalImage: "../Image/btn_min_normal.png"
                hoveredImage: "../Image/btn_min_hovered.png"
                pushedImage: "../Image/btn_min_pushed.png"
                onClicked: control.minClickListener()
                visible: control.showMinimize
            }
            FluImageButton{
                Layout.preferredHeight: 12
                Layout.preferredWidth: 12
                normalImage: "../Image/btn_max_normal.png"
                hoveredImage: "../Image/btn_max_hovered.png"
                pushedImage: "../Image/btn_max_pushed.png"
                onClicked: control.maxClickListener()
                visible: d.resizable && control.showMaximize
            }
        }
    }
    RowLayout{
        id:layout_standard_buttons
        height: parent.height
        anchors.right: parent.right
        spacing: 0
        FluIconButton{
            id:btn_dark
            Layout.preferredWidth: 40
            Layout.preferredHeight: 30
            padding: 0
            verticalPadding: 0
            horizontalPadding: 0
            rightPadding: 2
            iconSource: FluTheme.dark ? FluentIcons.Brightness : FluentIcons.QuietHours
            Layout.alignment: Qt.AlignVCenter
            iconSize: 15
            visible: control.showDark
            text: FluTheme.dark ? control.lightText : control.darkText
            radius: 0
            iconColor:control.textColor
            onClicked:()=> control.darkClickListener(btn_dark)
        }
        FluIconButton{
            id:btn_stay_top
            Layout.preferredWidth: 40
            Layout.preferredHeight: 30
            padding: 0
            verticalPadding: 0
            horizontalPadding: 0
            iconSource : FluentIcons.Pinned
            Layout.alignment: Qt.AlignVCenter
            iconSize: 14
            visible: {
                if(!(d.win instanceof FluWindow)){
                    return false
                }
                return control.showStayTop
            }
            text:d.stayTop ? control.stayTopCancelText : control.stayTopText
            radius: 0
            iconColor: d.stayTop ? FluTheme.primaryColor : control.textColor
            onClicked: control.stayTopClickListener()
        }
        FluIconButton{
            id:btn_minimize
            Layout.preferredWidth: 40
            Layout.preferredHeight: 30
            padding: 0
            verticalPadding: 0
            horizontalPadding: 0
            iconSource : FluentIcons.ChromeMinimize
            Layout.alignment: Qt.AlignVCenter
            iconSize: 11
            text:control.minimizeText
            radius: 0
            visible: !control.isMac && control.showMinimize
            iconColor: control.textColor
            color: {
                if(pressed){
                    return control.minimizePressColor
                }
                return hovered ? control.minimizeHoverColor : control.minimizeNormalColor
            }
            onClicked: control.minClickListener()
        }
        FluIconButton{
            id:btn_maximize
            property bool hover: btn_maximize.hovered
            Layout.preferredWidth: 40
            Layout.preferredHeight: 30
            padding: 0
            verticalPadding: 0
            horizontalPadding: 0
            iconSource : d.isRestore  ? FluentIcons.ChromeRestore : FluentIcons.ChromeMaximize
            color: {
                if(down){
                    return control.maximizePressColor
                }
                return btn_maximize.hover ? control.maximizeHoverColor : control.maximizeNormalColor
            }
            Layout.alignment: Qt.AlignVCenter
            visible: d.resizable && !control.isMac && control.showMaximize
            radius: 0
            iconColor: control.textColor
            text:d.isRestore?control.restoreText:control.maximizeText
            iconSize: 11
            onClicked: control.maxClickListener()
        }
        FluIconButton{
            id:btn_close
            Layout.preferredWidth: 40
            Layout.preferredHeight: 30
            padding: 0
            verticalPadding: 0
            horizontalPadding: 0
            iconSource : FluentIcons.ChromeClose
            Layout.alignment: Qt.AlignVCenter
            text:control.closeText
            visible: !control.isMac && control.showClose
            radius: 0
            iconSize: 10
            iconColor: hovered ? Qt.rgba(1,1,1,1) : control.textColor
            color:{
                if(pressed){
                    return control.closePressColor
                }
                return hovered ? control.closeHoverColor : control.closeNormalColor
            }
            onClicked: control.closeClickListener()
        }
    }
    FluLoader{
        id:layout_macos_buttons
        anchors{
            verticalCenter: parent.verticalCenter
            left: parent.left
            leftMargin: 10
        }
        sourceComponent: control.isMac ? com_macos_buttons : undefined
    }
}
