# Fluent UI 사각형 및 포커스 표시 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 사각형 관련 컴포넌트인 `FluRectangle`과 포커스 표시를 위한 `FluFocusRectangle`에 대해 설명합니다.

## 공통 임포트 방법

Fluent UI 사각형 및 포커스 표시 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluRectangle

`FluRectangle`은 사각형 영역을 그리는 데 사용되는 컴포넌트로, Python의 `QQuickPaintedItem`을 기반으로 구현되었습니다. 이 컴포넌트의 주요 특징은 각 네 모서리의 둥글기(radius)를 개별적으로 지정할 수 있다는 것입니다.

### 기반 클래스

`QQuickPaintedItem` (Python 플러그인)

### 고유/특징적 프로퍼티

| 이름     | 타입         | 기본값           | 설명                                                                                                   |
| :------- | :----------- | :--------------- | :----------------------------------------------------------------------------------------------------- |
| `color`  | `QColor`     | `Qt.rgba(1,1,1,1)` | 사각형 내부를 채울 색상.                                                                                  |
| `radius` | `list[int]`  | `[0, 0, 0, 0]`   | 각 모서리의 둥글기 반경을 지정하는 정수 리스트. 순서는 **[top-left, top-right, bottom-right, bottom-left]** 입니다. |

### 고유 시그널

| 이름            | 파라미터 | 반환타입 | 설명                         |
| :-------------- | :------- | :------- | :--------------------------- |
| `colorChanged`  | 없음     | -        | `color` 프로퍼티 값이 변경될 때 발생. |
| `radiusChanged` | 없음     | -        | `radius` 프로퍼티 값이 변경될 때 발생. |

### 고유 메소드

`FluRectangle` 자체에 QML에서 직접 호출할 수 있는 고유한 메소드는 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

RowLayout {
    spacing: 10

    FluRectangle {
        width: 50; height: 50
        color: "#0078d4"
        radius: [0, 0, 0, 0] // 모든 모서리 직각
    }
    FluRectangle {
        width: 50; height: 50
        color: "#744da9"
        radius: [15, 15, 15, 15] // 모든 모서리 둥글게 (반경 15)
    }
    FluRectangle {
        width: 50; height: 50
        color: "#ffeb3b"
        radius: [15, 0, 0, 0] // 좌측 상단만 둥글게
    }
    FluRectangle {
        width: 50; height: 50
        color: "#f7630c"
        radius: [0, 15, 0, 0] // 우측 상단만 둥글게
    }
    FluRectangle {
        width: 50; height: 50
        color: "#e71123"
        radius: [0, 0, 15, 0] // 우측 하단만 둥글게
    }
    FluRectangle {
        width: 50; height: 50
        color: "#b4009e"
        radius: [0, 0, 0, 15] // 좌측 하단만 둥글게
    }
}
```

### 참고 사항

*   `FluRectangle`은 Python으로 구현된 `QQuickPaintedItem`이므로, 성능이 중요한 경우 사용에 주의가 필요할 수 있습니다.
*   가장 큰 장점은 `radius` 프로퍼티를 통해 각 모서리의 둥근 정도를 독립적으로 제어할 수 있다는 점입니다.

--- 

## FluFocusRectangle

`FluFocusRectangle`은 다른 컨트롤이나 아이템이 키보드 포커스를 받았을 때 시각적인 테두리를 표시하여 포커스 상태를 나타내는 데 사용되는 간단한 컴포넌트입니다.

### 설명

이 컴포넌트는 주로 다른 UI 요소(예: 버튼, 입력 필드)의 내부에 배치되어 해당 요소가 현재 활성 포커스를 가지고 있음을 사용자에게 명확하게 보여주는 역할을 합니다. 테마(어둡거나 밝거나)에 따라 테두리 색상이 자동으로 조정됩니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름     | 타입   | 기본값 | 설명                        |
| :------- | :----- | :----- | :-------------------------- |
| `radius` | `int`  | `4`    | 포커스 테두리의 모서리 둥글기 반경. | 

*   내부 `Rectangle`의 `border.width`는 `2`로 고정되어 있습니다.
*   내부 `Rectangle`의 `z` 값은 `65535`로 매우 높아 다른 요소 위에 그려지도록 합니다.

### 고유 시그널 / 메소드

`FluFocusRectangle` 자체에 고유한 시그널이나 메소드는 정의되어 있지 않습니다.

### 예제

`FluFocusRectangle`은 일반적으로 다른 컴포넌트의 내부에 사용됩니다. 예를 들어, 사용자 정의 버튼 내에서 다음과 같이 사용할 수 있습니다:

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

Button { // 또는 다른 포커스 가능한 컨트롤
    id: myButton
    text: "포커스 가능한 버튼"
    focusPolicy: Qt.StrongFocus // 포커스를 받을 수 있도록 설정

    background: Rectangle {
        color: myButton.down ? "lightgrey" : "white"
        border.color: "grey"
        radius: 4
    }

    FluFocusRectangle { 
        // visible 속성을 부모의 activeFocus에 바인딩
        visible: myButton.activeFocus 
        radius: 4 // 부모 배경과 동일한 radius 설정
    }
}

// 참고: 많은 FluentUI 컨트롤들(예: FluButton, FluTextBox, FluShortcutPicker 등)은
// 내부적으로 FluFocusRectangle 또는 유사한 메커니즘을 사용하여 포커스를 표시합니다.
```

### 참고 사항

*   이 컴포넌트의 주 목적은 시각적인 포커스 피드백을 제공하는 것입니다.
*   `anchors.fill: parent`를 사용하여 부모 아이템의 크기에 맞춰 자동으로 크기가 조절되도록 설계되었습니다.
*   테두리 색상은 현재 `FluTheme`의 `dark` 속성 값에 따라 자동으로 흰색 또는 검은색으로 설정됩니다. 