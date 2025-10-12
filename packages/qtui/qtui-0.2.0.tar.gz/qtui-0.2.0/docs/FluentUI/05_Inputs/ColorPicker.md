# Fluent UI 색상 선택 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluColorPicker` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 버튼 형태로 선택된 색상을 표시하고, 클릭 시 팝업을 통해 색상을 선택할 수 있게 합니다.

## 공통 임포트 방법

Fluent UI 색상 선택 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluColorPicker

버튼 형태로 현재 선택된 색상을 시각적으로 보여주며, 버튼 클릭 시 색상 견본(swatches), RGB/HSV 값 입력 필드, 그리고 스포이트 도구를 포함하는 팝업 메뉴를 제공하여 사용자가 색상을 선택할 수 있게 합니다. `FluButton`을 기반으로 합니다.

### 주요 상속 프로퍼티 (FluButton)

`FluColorPicker`는 `FluButton`의 스타일 관련 프로퍼티(테두리, 배경 등)를 상속받습니다. 버튼의 전반적인 모양은 `FluButton`과 유사하지만, 선택된 색상을 표시하는 영역이 추가됩니다.

### 고유/특징적 프로퍼티

| 이름         | 타입    | 기본값           | 설명                                                  |
| :----------- | :------ | :--------------- | :---------------------------------------------------- |
| `color`      | `color` | `"#0078d4"`      | 현재 선택된 색상. 이 값을 설정하면 초기 색상이 지정됩니다. |
| `cancelText` | `string`| `qsTr("Cancel")` | 팝업 내 '취소' 버튼의 텍스트.                         |
| `okText`     | `string`| `qsTr("OK")`     | 팝업 내 '확인' 버튼의 텍스트.                         |

### 고유 시그널

| 이름        | 파라미터 | 반환타입 | 설명                                               |
| :---------- | :------- | :------- | :------------------------------------------------- |
| `accepted()`| 없음     | -        | 사용자가 팝업에서 '확인' 버튼을 눌러 색상 선택을 완료했을 때 발생. |

### 예제

```qml
import QtQuick 2.15
import FluentUI 1.0
import QtQuick.Layouts 1.15

ColumnLayout {
    spacing: 10

    FluColorPicker {
        id: colorPicker
        Layout.preferredWidth: 150
        color: "#ff8c00" // 초기 색상 설정 (주황색)

        onAccepted: {
            console.log("선택된 색상:", colorPicker.color)
            displayRect.color = colorPicker.color // 선택된 색상으로 Rectangle 채우기
        }
    }

    Rectangle {
        id: displayRect
        Layout.preferredWidth: 150
        Layout.preferredHeight: 50
        color: colorPicker.color // 초기 색상 표시
        border.color: "gray"
    }
}
```

### 참고 사항

*   `color` 프로퍼티는 QML의 표준 `color` 타입을 사용합니다. (`"#RRGGBB"`, `"#AARRGGBB"`, `"red"` 등 다양한 형식 가능)
*   버튼 내부에 작은 사각형 영역으로 현재 선택된 `color`가 표시됩니다.
*   팝업 UI는 다양한 기본 색상 견본, 사용자 지정 색상 선택 영역(채도/명도 조절), RGB 및 HSV 값 직접 입력 필드, 그리고 화면의 색상을 추출하는 스포이트 도구를 제공합니다.
*   `cancelText`와 `okText` 프로퍼티를 통해 팝업 버튼의 텍스트를 지역화하거나 사용자 정의할 수 있습니다. 