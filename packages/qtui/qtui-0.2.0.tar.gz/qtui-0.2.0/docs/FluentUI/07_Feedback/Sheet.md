# Fluent UI 시트 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluSheet` 컴포넌트에 대해 설명합니다. 시트는 화면 가장자리에서 슬라이드되어 나타나는 모달 팝업입니다.

## 공통 임포트 방법

Fluent UI 시트 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Layouts, Window 등 추가
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
```

---

## FluSheet

`FluSheet`는 애플리케이션 창의 상단, 하단, 왼쪽 또는 오른쪽 가장자리에서 부드럽게 슬라이드되어 나타나는 모달(modal) 팝업 컨테이너입니다. 임시 콘텐츠, 설정 옵션, 또는 간단한 작업 흐름을 표시하는 데 유용합니다. `Popup`을 기반으로 하며, 슬라이딩 애니메이션과 Fluent UI 스타일이 적용된 헤더 및 배경을 포함합니다.

### 기반 클래스

`Popup`

### 고유/특징적 프로퍼티

| 이름      | 타입          | 기본값                           | 설명                                                                                                                                 |
| :-------- | :------------ | :------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `title`   | `string`      | `""`                             | 시트 상단 헤더 영역에 표시될 제목 텍스트.                                                                                                 |
| `header`  | `Item`        | (닫기 버튼 + 제목 `FluText`)   | 시트의 헤더 부분을 정의하는 QML 아이템. 기본 헤더에는 닫기 버튼(`FluIconButton`)과 `title` 프로퍼티를 표시하는 `FluText`가 포함됩니다. 사용자 정의 헤더로 교체할 수 있습니다. |
| `content` | `list<Item>`  | (없음)                           | **기본 프로퍼티**. 시트의 주 내용 영역에 배치될 QML 아이템들의 리스트입니다. `FluSheet { ... }` 내부에 직접 아이템들을 배치하면 이 프로퍼티에 할당됩니다.      |
| `size`    | `int`         | `278`                            | 시트의 크기 (픽셀 단위). `open()` 메소드에서 `position`이 `Top` 또는 `Bottom`이면 시트의 높이를, `Left` 또는 `Right`이면 시트의 너비를 결정합니다.                 |
| `enter`   | `Transition`  | (방향별 슬라이드 효과)            | 시트가 화면에 나타날 때 적용될 애니메이션 트랜지션. `open()` 메소드의 `position` 값에 따라 다른 애니메이션(enter_top, enter_bottom, enter_left, enter_right)이 자동으로 선택됩니다. |
| `exit`    | `Transition`  | (방향별 슬라이드 효과)            | 시트가 화면에서 사라질 때 적용될 애니메이션 트랜지션. `position` 값에 따라 다른 애니메이션(exit_top, exit_bottom, exit_left, exit_right)이 자동으로 선택됩니다.  |
| `background`| `Rectangle`   | (Fluent 스타일 `Rectangle`)    | 시트의 배경. Fluent UI 테마(어둡거나 밝음), 테두리, `FluShadow` 효과가 적용된 `Rectangle`입니다.                                                         |

*   `FluSheet`는 `Popup`에서 상속된 `closePolicy` (기본값: `Popup.CloseOnEscape | Popup.CloseOnPressOutside`), `modal` (기본값: `true`), `padding` (기본값: 0) 등의 프로퍼티도 사용합니다.

### 고유 메소드

| 이름   | 파라미터                                    | 반환타입 | 설명                                                                                                                                        |
| :----- | :------------------------------------------ | :------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `open` | `int`: `position` (기본값: `FluSheetType.Bottom`) | `void`   | 시트를 화면에 표시합니다. `position` 파라미터는 시트가 나타날 위치를 지정하며, `FluentUI` 모듈에서 제공하는 `FluSheetType` 열거형 값(`Top`, `Bottom`, `Left`, `Right`) 중 하나를 사용합니다. | 

*   **`FluSheetType` 열거형**: `FluSheet`가 나타날 위치를 지정합니다. (`FluSheetType.Top`, `FluSheetType.Bottom`, `FluSheetType.Left`, `FluSheetType.Right`) Fluent UI 임포트를 통해 사용 가능합니다.

### 고유 시그널

`FluSheet` 자체에 고유하게 추가된 시그널은 없습니다. `Popup`에서 상속된 시그널(예: `opened()`, `closed()`)을 사용할 수 있습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import FluentUI 1.0

ColumnLayout {
    spacing: 20
    
    // FluSheet 정의
    FluSheet {
        id: mySheet
        title: qsTr("설정")
        size: 300 // 시트 크기 지정 (높이 또는 너비)
        
        // content (기본 프로퍼티) 영역
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 15
            spacing: 10
            
            FluText { text: qsTr("옵션 1") }
            FluCheckBox { text: qsTr("활성화") }
            FluSlider { Layout.fillWidth: true }
            Item { Layout.fillHeight: true } // 공간 채우기
            FluButton { 
                text: qsTr("적용")
                Layout.alignment: Qt.AlignRight
                onClicked: mySheet.close() // 시트 닫기
            }
        }
    }

    // 시트를 여는 버튼들
    RowLayout {
        spacing: 10
        FluButton { text: qsTr("상단 열기"); onClicked: mySheet.open(FluSheetType.Top) }
        FluButton { text: qsTr("하단 열기"); onClicked: mySheet.open(FluSheetType.Bottom) }
        FluButton { text: qsTr("왼쪽 열기"); onClicked: mySheet.open(FluSheetType.Left) }
        FluButton { text: qsTr("오른쪽 열기"); onClicked: mySheet.open(FluSheetType.Right) }
    }
}

```

### 참고 사항

*   **표시 및 위치**: `open()` 메소드를 호출하여 시트를 표시합니다. `position` 파라미터(`FluSheetType` 값)에 따라 시트가 나타나는 위치(상/하/좌/우)와 `size` 프로퍼티가 높이로 적용될지 너비로 적용될지가 결정됩니다.
*   **모달 동작**: `modal` 프로퍼티가 기본적으로 `true`이므로, 시트가 열려 있는 동안에는 시트 외부의 다른 UI 요소와 상호작용할 수 없습니다.
*   **닫기**: 기본적으로 사용자는 Escape 키를 누르거나 시트 외부 영역을 클릭하여 시트를 닫을 수 있습니다 (`closePolicy`). 코드 내에서는 `close()` 메소드를 호출하여 닫을 수 있습니다.
*   **애니메이션**: 시트가 나타나고 사라질 때 부드러운 슬라이드 애니메이션 효과가 적용됩니다. 