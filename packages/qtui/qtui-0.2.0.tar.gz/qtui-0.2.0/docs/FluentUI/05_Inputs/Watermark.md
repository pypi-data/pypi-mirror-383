# Fluent UI 워터마크 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluWatermark` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 Python으로 구현되었으며, 특정 영역 위에 반복되는 텍스트 워터마크를 표시하는 데 사용됩니다.

## 공통 임포트 방법

Fluent UI 워터마크 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluWatermark

`FluWatermark`는 콘텐츠 영역 위에 텍스트 워터마크를 타일 형태로 반복하여 표시하는 `QQuickPaintedItem` 기반 컴포넌트입니다. 주로 저작권 정보, 기밀 문서 표시, 또는 브랜딩 목적으로 사용되어 내용 위에 비간섭적인 텍스트 패턴을 오버레이합니다. 텍스트 내용, 색상, 크기, 회전 각도, 그리고 각 워터마크 간의 간격 및 시작 위치 오프셋을 조절하여 다양한 워터마크 패턴을 만들 수 있습니다.

### 기반 클래스

`QQuickPaintedItem` (Python 플러그인)

### 고유/특징적 프로퍼티

| 이름        | 타입     | 기본값                      | 설명                                                                                             |
| :---------- | :------- | :-------------------------- | :----------------------------------------------------------------------------------------------- |
| `text`      | `string` | `""`                        | 워터마크로 표시될 텍스트 내용.                                                                       |
| `gap`       | `QPoint` | `Qt.point(100, 100)`        | 반복되는 각 워터마크 텍스트 사이의 수평(x) 및 수직(y) 간격 (픽셀 단위).                                       |
| `offset`    | `QPoint` | `Qt.point(gap.x/2, gap.y/2)`| 워터마크 패턴의 시작 위치 오프셋. 기본값은 `gap`의 절반으로, 첫 번째 워터마크가 컴포넌트 중앙 부근에서 시작하도록 합니다. |
| `textColor` | `QColor` | `Qt.rgba(0.87, 0.87, 0.87, 0.87)` (연한 회색, 반투명) | 워터마크 텍스트의 색상. 일반적으로 낮은 알파값(투명도)을 사용하여 내용 가독성을 해치지 않도록 합니다.                   |
| `rotate`    | `int`    | `22`                        | 각 워터마크 텍스트의 회전 각도 (시계 방향, 도 단위).                                                        |
| `textSize`  | `int`    | `16`                        | 워터마크 텍스트의 글꼴 크기 (픽셀 단위).                                                               |

### 고유 시그널

`FluWatermark`는 각 프로퍼티(`text`, `gap`, `offset`, `textColor`, `rotate`, `textSize`)가 변경될 때마다 해당 프로퍼티 이름 뒤에 `Changed`가 붙는 시그널(예: `textChanged`, `gapChanged`)을 발생시킵니다.

### 고유 메소드

`FluWatermark` 자체에 QML에서 직접 호출하도록 설계된 고유한 메소드는 없습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluContentPage { // 또는 다른 컨테이너 아이템
    width: 600
    height: 400

    // 워터마크 아래에 표시될 내용 (예시)
    ColumnLayout {
        anchors.centerIn: parent
        FluText { text: "이것은 보호되는 콘텐츠입니다." }
        FluButton { text: "확인" }
    }

    // 워터마크 컴포넌트
    FluWatermark {
        id: watermarkLayer
        anchors.fill: parent // 부모 영역 전체를 덮도록 설정
        z: 1 // 다른 콘텐츠 위에 표시되도록 z-order 설정

        text: "FluentUI Demo"
        textColor: Qt.rgba(0, 0, 0, 0.08) // 매우 연한 검정색
        textSize: 24
        rotate: -30 // 반시계 방향 회전
        gap: Qt.point(150, 150) // 간격 넓게
        offset: Qt.point(20, 75) // 오프셋 조정
    }

    // 동적 제어 예시 (다른 컨트롤과 연동)
    /*
    ColumnLayout {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.margins: 10
        spacing: 5
        FluTextBox { id: txtInput; text: watermarkLayer.text; placeholderText: "워터마크 텍스트" }
        FluSlider { id: sliderRotate; from: -180; to: 180; value: watermarkLayer.rotate }
        FluColorPicker { id: colorPicker; current: watermarkLayer.textColor }
        
        Binding { target: watermarkLayer; property: "text"; value: txtInput.text }
        Binding { target: watermarkLayer; property: "rotate"; value: sliderRotate.value }
        Binding { target: watermarkLayer; property: "textColor"; value: colorPicker.current }
    }
    */
}
```

### 참고 사항

*   **Python 기반**: `FluWatermark`는 QML의 표준 아이템이 아니라 Python으로 작성된 `QQuickPaintedItem`입니다. 따라서 Python 환경 설정이 필요하며, 성능 특성이 다를 수 있습니다.
*   **배치 및 Z-order**: 일반적으로 워터마크는 다른 콘텐츠 위에 표시되어야 하므로, `anchors.fill: parent`를 사용하여 대상 영역을 덮고 `z` 프로퍼티 값을 다른 요소들보다 높게 설정하는 것이 좋습니다.
*   **`gap`과 `offset`**: `gap`은 각 텍스트 반복 사이의 빈 공간을 결정하고, `offset`은 전체 패턴의 시작 위치를 조정합니다. 이 두 값을 조절하여 워터마크 패턴의 밀도와 배치를 미세 조정할 수 있습니다.
*   **`textColor` 투명도**: 워터마크가 배경 콘텐츠를 너무 가리지 않도록 `textColor`의 알파(alpha) 값을 낮게 설정하는 것이 일반적입니다 (예: `Qt.rgba(0, 0, 0, 0.1)`). 