import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0
import "../component"

FluScrollablePage{

    title: qsTr("Image")

    FluFrame{
        Layout.fillWidth: true
        Layout.preferredHeight: 260
        padding: 10
        Column{
            spacing: 15
            anchors{
                verticalCenter: parent.verticalCenter
                left:parent.left
            }
            FluImage{
                width: 384
                height: 240
                source: "qrc:/example/res/image/banner_1.jpg"
                onStatusChanged:{
                    if(status === Image.Error){
                        showError(qsTr("The image failed to load, please reload"))
                    }
                }
                clickErrorListener: function(){
                    source = "qrc:/example/res/image/banner_1.jpg"
                }
            }
        }
    }
    CodeExpander{
        Layout.fillWidth: true
        Layout.topMargin: -6
        code:'FluImage{
    width: 400
    height: 300
    source: "qrc:/example/res/image/banner_1.jpg"
}'
    }

}
