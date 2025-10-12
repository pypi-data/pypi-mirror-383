# Fluent UI 확장기 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluExpander` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 헤더와 숨겨진 콘텐츠 영역으로 구성되어, 헤더 클릭 시 콘텐츠 영역을 펼치거나 접을 수 있게 해줍니다.

## 공통 임포트 방법

Fluent UI 확장기 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluExpander

`FluExpander`는 사용자가 헤더 영역을 클릭하여 관련 콘텐츠를 보여주거나 숨길 수 있는 컨트롤입니다. 헤더에는 일반적으로 제목 텍스트와 현재 확장/축소 상태를 나타내는 아이콘(위/아래 방향 쉐브론)이 표시됩니다. 콘텐츠 영역은 부드러운 애니메이션과 함께 나타나거나 사라지며, 복잡한 정보를 섹션별로 구성하거나 사용자가 필요할 때만 상세 내용을 볼 수 있도록 UI를 설계하는 데 유용합니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름            | 타입        | 기본값 | 설명                                                                                                     |
| :-------------- | :---------- | :----- | :------------------------------------------------------------------------------------------------------- |
| `headerText`    | `string`    | `""`   | 확장기 헤더 영역에 표시될 텍스트.                                                                           |
| `expand`        | `bool`      | `false`| 콘텐츠 영역의 확장(펼침) 상태. `true`이면 펼쳐지고, `false`이면 접힙니다. 헤더를 클릭하면 이 값이 토글됩니다.       |
| `contentHeight` | `int`       | `300`  | 콘텐츠 영역이 펼쳐졌을 때의 높이 (픽셀 단위). 이 값은 내부에 포함될 콘텐츠의 실제 높이에 맞게 설정해야 합니다. |
| `content`       | `default alias` | -      | 확장/축소될 콘텐츠 아이템들을 배치하는 기본 프로퍼티 별칭. 여기에 QML 아이템(예: `Item`, `Rectangle`, `ColumnLayout` 등)을 정의합니다. | 

### 고유 시그널

*   `expand` 프로퍼티 값이 변경될 때 암시적으로 `onExpandChanged` 시그널 핸들러를 사용할 수 있습니다.

### 고유 메소드

`FluExpander` 자체에 외부에서 직접 호출하도록 설계된 고유한 메소드는 없습니다 (내부적으로 `toggle()` 함수 사용).

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    width: 400
    spacing: 15

    FluExpander {
        Layout.fillWidth: true
        headerText: qsTr("라디오 버튼 그룹 열기")
        contentHeight: 120 // 내부 콘텐츠 높이에 맞게 조정

        // content (기본 프로퍼티) 영역
        FluRadioButtons {
            anchors.fill: parent
            anchors.margins: 15 // 내부 여백
            spacing: 8
            FluRadioButton { text: "옵션 1" }
            FluRadioButton { text: "옵션 2" }
            FluRadioButton { text: "옵션 3" }
        }
    }

    FluExpander {
        Layout.fillWidth: true
        headerText: qsTr("긴 텍스트 영역 열기")
        contentHeight: 200 // Flickable 높이 설정

        // content (기본 프로퍼티) 영역
        Flickable {
            id: flickableArea
            anchors.fill: parent
            contentWidth: width
            contentHeight: longText.height
            clip: true
            ScrollBar.vertical: FluScrollBar {}

            FluText {
                id: longText
                width: flickableArea.width - 28 // 스크롤바 고려
                wrapMode: Text.WrapAnywhere
                padding: 14
                text: qsTr("여기에 매우 긴 텍스트 내용...") 
            }
        }
    }
}
```

### 참고 사항

*   **상호작용**: 사용자는 헤더 영역(텍스트 또는 우측의 쉐브론 아이콘 포함) 아무 곳이나 클릭하여 `expand` 상태를 토글할 수 있습니다.
*   **`contentHeight` 설정**: 이 프로퍼티는 확장될 콘텐츠 영역의 높이를 지정하므로 매우 중요합니다. 내부에 배치될 콘텐츠의 예상 높이 또는 실제 높이에 맞게 정확히 설정해야 콘텐츠가 올바르게 표시됩니다.
*   **콘텐츠 배치**: 확장/축소될 콘텐츠는 `FluExpander { ... }` 블록 내부에 직접 배치하여 기본 프로퍼티인 `content`에 할당합니다. 일반적으로 `Item`이나 `ColumnLayout` 같은 컨테이너를 먼저 배치하고 그 안에 실제 내용을 구성합니다.
*   **애니메이션**: 콘텐츠 영역이 펼쳐지거나 접힐 때 부드러운 수직 이동 애니메이션(`NumberAnimation` on `anchors.topMargin`)이 적용됩니다. 애니메이션 활성화 여부 및 속도는 `FluTheme.animationEnabled` 설정에 영향을 받을 수 있습니다. 