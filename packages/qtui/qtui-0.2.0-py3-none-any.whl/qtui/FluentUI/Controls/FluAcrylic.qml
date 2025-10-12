import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: control
    property color tintColor: Qt.rgba(1, 1, 1, 1)
    property real tintOpacity: 0.65
    property real luminosity: 0.01
    property real noiseOpacity: 0.02
    property var target
    property int blurRadius: 32
    property rect targetRect: Qt.rect(control.x, control.y, control.width,control.height)
    ShaderEffectSource {
        id: effect_source
        anchors.fill: parent
        visible: false
        sourceRect: control.targetRect
        sourceItem: control.target
    }
    FastBlur {
        id: fast_blur
        anchors.fill: parent
        source: effect_source
        radius: control.blurRadius
    }
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(1, 1, 1, control.luminosity)
    }
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(control.tintColor.r, control.tintColor.g, control.tintColor.b, control.tintOpacity)
    }
    Image {
        anchors.fill: parent
        source: "qrc:/Image/noise.png"
        fillMode: Image.Tile
        opacity: control.noiseOpacity
    }
}
