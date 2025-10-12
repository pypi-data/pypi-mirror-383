# Fluent UI 내부 및 기본 컴포넌트

이 문서에서는 Fluent UI 라이브러리 내부에서 주로 사용되거나 다른 컴포넌트의 기반을 제공하는 기본 컴포넌트들에 대해 설명합니다. 일반적으로 애플리케이션 개발자가 이 컴포넌트들을 직접 사용할 필요는 적지만, 내부 구조를 이해하거나 Fluent UI를 확장/커스터마이징하는 데 도움이 될 수 있습니다.

다루는 컴포넌트는 다음과 같습니다:
*   `FluControl`: 기본적인 상호작용 및 포커스 처리를 위한 컨트롤 기반.
*   `FluControlBackground`: 표준화된 배경 및 테두리 스타일을 제공하는 아이템.
*   `FluDivider`: 수평 또는 수직 구분선.
*   `FluFrame`: 간단한 테두리 및 배경을 가진 컨테이너.

## 공통 임포트 방법

이 컴포넌트들의 구현을 참조하거나 내부적으로 사용할 경우, 일반적으로 다음 임포트가 필요합니다.

```qml
import QtQuick 2.15
import QtQuick.Templates as T // 기반 템플릿 사용 시
import FluentUI 1.0
```

---

## FluControl

`FluControl`은 Fluent UI 내에서 다양한 인터랙티브 요소(예: 리스트 아이템, 커스텀 버튼 영역 등)의 기반으로 사용되는 기본적인 컨트롤입니다. `QtQuick.Templates.Button`을 확장하여 기본적인 클릭 상호작용, 상태(hover, press), 그리고 Fluent UI 스타일의 포커스 표시(`FluFocusRectangle`) 및 접근성 기능을 제공합니다.

### 기반 클래스

`QtQuick.Templates.Button` (QML에서는 `T.Button`으로 사용)

### 주요 프로퍼티

| 이름                 | 타입     | 기본값          | 설명                                                                                                             |
| :------------------- | :------- | :-------------- | :--------------------------------------------------------------------------------------------------------------- |
| `contentDescription` | `string` | `""`            | 접근성(Accessibility)을 위한 컨트롤 설명 텍스트입니다.                                                               |
| `focusPolicy`        | `enum`   | `Qt.TabFocus`   | 키보드 포커스를 받을 수 있는지 여부 및 방식입니다. (상속됨)                                                            |
| `background`         | `Item`   | (기본 Item 제공) | 컨트롤의 배경 아이템입니다. 기본적으로 내부에 `FluFocusRectangle`을 포함하여 `activeFocus` 상태일 때 포커스 테두리를 표시합니다. |
| `contentItem`        | `Item`   | (빈 Item 제공)  | 컨트롤의 내용을 담는 아이템입니다. 기본적으로 비어 있으며, 이 컨트롤을 사용하는 상위 컴포넌트에서 내용을 채웁니다. (상속됨)         |
| `padding`            | `real`   | `0`             | 내부 `contentItem` 주위의 여백입니다. (상속됨)                                                                     |
| `spacing`            | `real`   | `0`             | 아이콘과 텍스트 사이의 간격 (상속된 프로퍼티이나 기본 `contentItem`에는 해당 요소 없음).                               |

*(이 외 `T.Button`으로부터 `clicked`, `pressed`, `hovered`, `activeFocus`, `text`, `icon`, `implicitWidth`, `implicitHeight` 등 다수의 프로퍼티 및 시그널 상속)*

### 주요 시그널

| 이름      | 파라미터 | 반환타입 | 설명                             |
| :-------- | :------- | :------- | :------------------------------- |
| `clicked` | 없음     | -        | 사용자가 컨트롤을 클릭했을 때 발생. (상속됨) |

### 사용 예시 (내부적)

`FluPaneItem`과 같은 컴포넌트가 `FluControl`을 사용하여 클릭 가능한 영역과 포커스 표시 기능을 구현합니다. `FluPaneItem`은 `FluControl`의 `background`와 `contentItem`을 자체 스타일과 내용으로 재정의하여 사용합니다.

### 참고 사항

*   `FluControl` 자체는 최소한의 시각적 스타일링만 제공합니다. 주로 다른 컴포넌트에서 상속받아 구체적인 배경, 내용, 스타일을 정의하여 사용합니다.
*   `FluFocusRectangle`을 통해 키보드 탐색 시 일관된 포커스 표시를 제공하는 것이 주된 역할 중 하나입니다.

---

## FluControlBackground

`FluControlBackground`는 둥근 모서리, 테두리, 배경 채우기, 그리고 미묘한 그림자 또는 그라데이션 효과를 포함하는 표준화된 Fluent UI 스타일의 배경을 제공하는 재사용 가능한 `Item`입니다. 다른 컨트롤 내부에 포함되어 시각적 배경을 구성하는 데 사용됩니다.

### 기반 클래스

`QtQuick.Item`

### 주요 프로퍼티

| 이름            | 타입       | 기본값                  | 설명                                                                                                                             |
| :-------------- | :--------- | :---------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `radius`        | `int`      | `4`                     | 배경과 테두리의 모서리 둥글기 반경입니다.                                                                                            |
| `shadow`        | `bool`     | `true`                  | 테두리 그라데이션의 하단 색상에 영향을 줍니다. `true`일 경우 미묘한 그림자 효과(어두운 테두리 색)를, `false`일 경우 밝은 색상을 사용합니다. | (`true`가 일반적인 그림자를 의미하는 것은 아님)
| `border`        | `alias`    | (내부 `border` 객체)    | 내부 테두리 `Rectangle`의 `border` 프로퍼티에 대한 별칭입니다. 주로 `border.color`를 설정하는 데 사용됩니다. (`border.width`는 내부적으로 1로 간주됨) |
| `color`         | `color`    | 테마 기반 자동 설정       | 내부 배경 채우기(`rect_back`)의 색상입니다. (기본: `FluTheme.dark` ? `#2A2A2A` : `#FEFEFE`)                                        |
| `gradient`      | `alias`    | (내부 `gradient` 객체)  | 테두리 `Rectangle`(`rect_border`)의 `gradient` 프로퍼티에 대한 별칭입니다. 기본 그라데이션을 재정의할 때 사용될 수 있습니다.              |
| `topMargin`     | `var`      | `undefined`             | 내부 배경 채우기(`rect_back`)의 상단 여백입니다. 테두리는 영향을 받지 않습니다.                                                               |
| `bottomMargin`  | `var`      | `undefined`             | 내부 배경 채우기(`rect_back`)의 하단 여백입니다. 테두리는 영향을 받지 않습니다.                                                               |
| `leftMargin`    | `var`      | `undefined`             | 내부 배경 채우기(`rect_back`)의 좌측 여백입니다. 테두리는 영향을 받지 않습니다.                                                               |
| `rightMargin`   | `var`      | `undefined`             | 내부 배경 채우기(`rect_back`)의 우측 여백입니다. 테두리는 영향을 받지 않습니다.                                                               |

### 사용 예시 (내부적)

`FluAutoSuggestBox`의 드롭다운 팝업 배경 등, `FluFrame`의 기본 배경 스타일과 다른 커스텀 배경이 필요한 내부 컴포넌트에서 사용될 수 있습니다.

### 참고 사항

*   이 컴포넌트는 두 개의 `Rectangle`로 구성됩니다: `rect_border`는 외곽선 및 그라데이션 효과를 담당하고, `rect_back`은 주 배경색 채우기를 담당합니다.
*   `border.width`는 내부적으로 1픽셀로 고정된 것처럼 동작합니다. (외부에서 설정 불가)
*   `top/bottom/left/rightMargin` 프로퍼티는 테두리를 제외한 내부 배경 영역에만 적용됩니다.

---

## FluDivider

`FluDivider`는 UI 요소들을 시각적으로 구분하기 위한 수평 또는 수직 구분선을 표시하는 간단한 컴포넌트입니다.

### 기반 클래스

`QtQuick.Item`

### 주요 프로퍼티

| 이름          | 타입   | 기본값             | 설명                                                                                                                                    |
| :------------ | :----- | :----------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| `orientation` | `enum` | `Qt.Horizontal`    | 구분선의 방향을 설정합니다 (`Qt.Horizontal` 또는 `Qt.Vertical`).                                                                             |
| `spacing`     | `int`  | `0`                | 구분선 주변의 여백입니다. 컴포넌트의 전체 너비(수직) 또는 높이(수평)는 `size + spacing * 2`가 됩니다.                                               |
| `size`        | `int`  | `1`                | 구분선 자체의 두께(수평 시 높이, 수직 시 너비)입니다.                                                                                       |
| (내부) `color`| `color`| `FluTheme.dividerColor` | 구분선의 색상입니다. 내부 `FluRectangle`을 통해 설정됩니다.                                                                               |

### 사용 예시 (내부적 또는 직접 사용)

```qml
ColumnLayout {
    spacing: 10
    FluText { text: "섹션 1 내용" }
    FluDivider { Layout.fillWidth: true }
    FluText { text: "섹션 2 내용" }
}

RowLayout {
    spacing: 10
    FluText { text: "왼쪽 내용" }
    FluDivider { orientation: Qt.Vertical; Layout.fillHeight: true }
    FluText { text: "오른쪽 내용" }
}
```

### 참고 사항

*   레이아웃 내에서 사용할 때 `Layout.fillWidth` (수평) 또는 `Layout.fillHeight` (수직)를 설정하여 부모 크기에 맞게 자동으로 확장되도록 하는 것이 일반적입니다.
*   실제 선은 내부의 `FluRectangle`에 의해 그려집니다.

---

## FluFrame

`FluFrame`은 콘텐츠를 시각적으로 그룹화하는 데 사용되는 간단한 컨테이너 컴포넌트입니다. `QtQuick.Templates.Frame`을 기반으로 하며, Fluent UI 스타일의 표준 테두리와 배경색을 제공합니다. 배경색은 애플리케이션 창의 활성 상태에 따라 변경됩니다.

### 기반 클래스

`QtQuick.Templates.Frame` (QML에서는 `T.Frame`으로 사용)

### 주요 프로퍼티

| 이름     | 타입     | 기본값                  | 설명                                                                                                                                                              |
| :------- | :------- | :---------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `radius` | `alias`  | `4`                     | 배경 `Rectangle`의 모서리 둥글기 반경입니다.                                                                                                                     |
| `border` | `alias`  | (내부 `border` 객체)    | 배경 `Rectangle`의 `border` 프로퍼티 별칭입니다. 주로 `border.color` (기본: `FluTheme.dividerColor`)를 설정하는 데 사용됩니다. (`border.width`는 기본값 1)                       |
| `color`  | `alias`  | 테마 및 활성 상태 기반    | 배경 `Rectangle`의 색상 별칭입니다. 창이 활성 상태일 때는 `FluTheme.frameActiveColor`, 비활성 상태일 때는 `FluTheme.frameColor`가 자동으로 적용됩니다.                                |
| `padding`| `real`   | `0`                     | 프레임 테두리와 내부 콘텐츠 사이의 여백입니다. (상속됨)                                                                                                               |

*(이 외 `T.Frame`으로부터 `implicitWidth`, `implicitHeight`, `contentItem`, `contentWidth`, `contentHeight`, `top/bottom/left/rightPadding` 등 다수의 프로퍼티 상속)*

### 사용 예시 (직접 사용)

`T_Settings.qml` 이나 `T_TextBox.qml`과 같은 예제 페이지에서 관련 컨트롤들을 그룹화하고 시각적으로 구분하기 위해 `FluFrame`이 사용됩니다.

```qml
FluFrame {
    Layout.fillWidth: true
    Layout.preferredHeight: 68
    padding: 10

    FluTextBox {
        // ... 내용 ...
        anchors.verticalCenter: parent.verticalCenter
    }
}
```

### 참고 사항

*   `FluControlBackground`보다 간단한 배경 스타일을 제공합니다. (그라데이션 테두리 없음)
*   주요 특징은 창 활성 상태에 따라 배경색이 자동으로 변경된다는 점입니다.
*   일반적으로 레이아웃 관리자(`ColumnLayout`, `RowLayout` 등)와 함께 사용하여 내부에 컨트롤이나 다른 레이아웃을 배치합니다. 

---

## FluItemDelegate

`FluItemDelegate`는 `ListView`, `ComboBox` 드롭다운 등과 같은 뷰(View) 내부의 개별 항목을 표시하기 위한 기본 델리게이트입니다. `QtQuick.Templates.ItemDelegate`를 기반으로 하며, Fluent UI 스타일의 텍스트, 아이콘 색상 및 기본적인 상호작용(클릭, 포커스, 하이라이트) 시 배경 표시를 제공합니다.

### 기반 클래스

`QtQuick.Templates.ItemDelegate` (QML에서는 `T.ItemDelegate`으로 사용)

### 주요 프로퍼티

| 이름            | 타입     | 기본값                    | 설명                                                                                                                      |
| :-------------- | :------- | :------------------------ | :---------------------------------------------------------------------------------------------------------------------- |
| `text`          | `string` | `""`                      | 델리게이트에 표시될 주 텍스트입니다. (상속됨)                                                                               |
| `font`          | `font`   | (컨트롤의 기본 폰트)        | 텍스트의 글꼴입니다. (상속됨)                                                                                               |
| `icon.source`   | `url`    | `""`                      | 텍스트 왼쪽에 표시될 아이콘의 소스입니다. (상속됨)                                                                            |
| `icon.color`    | `color`  | `control.palette.text`    | 아이콘의 색상입니다. 기본적으로 델리게이트 텍스트 색상(`palette.text`)을 따릅니다. (상속됨)                                     |
| `padding`       | `real`   | `0`                       | 전체 델리게이트 영역과 내부 콘텐츠 사이의 여백입니다. (상속됨)                                                              |
| `verticalPadding`| `real`  | `8`                       | 수직 내부 여백입니다.                                                                                                     |
| `horizontalPadding`| `real`| `10`                      | 수평 내부 여백입니다.                                                                                                     |
| `contentItem`   | `FluText`| (기본 `FluText` 제공)     | 텍스트를 표시하는 아이템입니다. 기본적으로 `control.text`, `control.font`를 사용하며, `down` 상태에 따라 색상이 변경됩니다.      |
| `background`    | `Rectangle`| (기본 `Rectangle` 제공) | 배경 아이템입니다. `down`(눌림), `highlighted`(호버 등), `visualFocus` 상태일 때 반투명한 배경색(`rgba(1,1,1,0.05)` 또는 `rgba(0,0,0,0.05)`)을 표시합니다. |

*(이 외 `T.ItemDelegate`으로부터 `pressed`, `down`, `highlighted`, `visualFocus`, `implicitWidth`, `implicitHeight` 등 다수의 프로퍼티 및 시그널 상속)*

### 사용 예시 (내부적)

`FluMenu`, `FluComboBox` 드롭다운 목록 등의 내부에서 각 항목을 렌더링하는 데 사용됩니다. 개발자가 `ListView` 등에서 직접 사용할 수도 있지만, 보통은 `FluMenuItem`과 같이 더 특화된 컴포넌트를 사용하는 것이 일반적입니다.

### 참고 사항

*   이 컴포넌트는 Fluent UI 스타일의 기본적인 목록 항목 모양과 상호작용 피드백을 제공합니다.
*   `contentItem`의 `FluText`는 `down` 상태일 때 약간 더 어두운 색상으로 변경됩니다.

---

## FluObject

`FluObject`는 `QtObject`를 감싸는 매우 단순한 래퍼 컴포넌트입니다. 주요 목적은 `default property list<QtObject> children` 선언을 통해 QML에서 자식 객체들을 별도의 프로퍼티 이름 없이 직접 정의할 수 있게 하는 것입니다.

### 기반 클래스

`QtQuick.QtObject`

### 주요 특징

*   **기본 프로퍼티**: `children` 이라는 이름의 `list<QtObject>` 타입 기본 프로퍼티를 가집니다. 이는 QML에서 `<FluObject>` 태그 내부에 다른 `QtObject` 기반의 비시각적 요소들(예: 모델, 바인딩, 커스텀 로직 객체)을 중첩하여 정의할 수 있게 해줍니다.

```qml
FluObject {
    // 아래 객체들은 'children' 프로퍼티의 리스트 항목으로 추가됨
    MyCustomLogic { id: logic1 }
    ListModel { id: dataModel }
}
```

### 사용 예시 (내부적)

주로 여러 비시각적 헬퍼 객체들을 그룹화하거나, 특정 컴포넌트가 자식으로 정의된 비시각적 객체들을 내부적으로 관리해야 할 때 사용될 수 있습니다.

### 참고 사항

*   시각적인 표현이 전혀 없는 유틸리티 컴포넌트입니다.

---

## FluPopup

`FluPopup`는 Fluent UI 스타일의 표준 팝업 창을 위한 기본 틀을 제공하는 컴포넌트입니다. `QtQuick.Controls.Popup`을 기반으로 하며, 자동으로 화면 중앙에 위치하고, 모달(modal) 동작, 표준 배경 스타일(`FluRectangle` + `FluShadow`), 그리고 부드러운 나타나기/사라지기 애니메이션 효과를 포함합니다.

### 기반 클래스

`QtQuick.Controls.Popup`

### 주요 프로퍼티

| 이름          | 타입       | 기본값                 | 설명                                                                                                                              |
| :------------ | :--------- | :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `padding`     | `real`     | `0`                    | 팝업 내부 여백입니다. (상속됨)                                                                                                      |
| `modal`       | `bool`     | `true`                 | 팝업이 표시될 때 다른 UI와의 상호작용을 차단할지 여부입니다. (상속됨)                                                                |
| `parent`      | `Item`     | `Overlay.overlay`      | 팝업이 속할 부모 아이템입니다. 기본적으로 최상위 오버레이에 표시됩니다. (상속됨)                                                      |
| `x`, `y`      | `real`     | (자동 중앙 계산)         | 팝업의 위치입니다. 기본적으로 `parent`의 중앙에 위치하도록 계산됩니다. (상속됨)                                                      |
| `width`, `height` | `real` | (자동 계산)            | 팝업의 크기입니다. `implicitHeight`를 기반으로 하되, `parent`의 높이를 넘지 않도록 제한됩니다. (상속됨)                                |
| `closePolicy` | `enum`     | `Popup.NoAutoClose`    | 팝업이 자동으로 닫히는 정책입니다. 기본적으로는 자동으로 닫히지 않으므로, 닫기 로직을 직접 구현해야 합니다. (상속됨)                        |
| `enter`, `exit` | `Transition` | (기본 애니메이션 제공) | 팝업이 나타나거나 사라질 때의 `Opacity` 애니메이션(`NumberAnimation`)입니다. `FluTheme.animationEnabled` 설정에 따라 활성화됩니다. |
| `background`  | `FluRectangle`| (기본 배경 제공)       | 팝업의 배경 아이템입니다. 기본적으로 둥근 모서리(radius 5), 테마 색상(`FluTheme.dark` ? `#2B2B2B` : `#FFFFFF`), 그리고 `FluShadow`를 포함합니다. |

*(이 외 `Popup`으로부터 `open()`, `close()`, `opened`, `closed` 등 다수의 프로퍼티, 메소드, 시그널 상속)*

### 사용 예시 (내부적 또는 직접 사용)

```qml
// 직접 사용 예시
FluPopup {
    id: myCustomPopup
    width: 300
    height: 200

    contentItem: ColumnLayout {
        FluText { text: "커스텀 팝업 내용" }
        FluButton { text: "닫기"; onClicked: myCustomPopup.close() }
    }
}

// 버튼 클릭 시 팝업 열기
FluButton {
    text: "팝업 열기"
    onClicked: myCustomPopup.open()
}
```

### 참고 사항

*   `FluContentDialog`, `FluMenu` 등 Fluent UI의 다른 팝업 기반 컴포넌트들이 이 `FluPopup`을 내부적으로 사용하여 일관된 모양과 동작을 구현합니다.
*   개발자가 직접 커스텀 팝업 UI를 만들 때 기본 틀로 사용할 수 있습니다. `contentItem` 프로퍼티에 원하는 내용을 채우면 됩니다.
*   기본 `closePolicy`가 `NoAutoClose`이므로, 팝업을 닫는 버튼이나 로직을 명시적으로 추가해야 합니다.

---

## FluShadow

`FluShadow`는 `Item` 주변에 부드러운 그림자 효과를 추가하는 데 사용되는 시각적 컴포넌트입니다. Qt Quick의 기본 `DropShadow` 효과보다 더 나은 성능을 제공하기 위해 `Repeater`와 여러 겹의 반투명 `Rectangle` 테두리를 사용하여 그림자를 시뮬레이션합니다.

### 기반 클래스

`QtQuick.Item`

### 주요 프로퍼티

| 이름        | 타입    | 기본값    | 설명                                                                                                |
| :---------- | :------ | :-------- | :-------------------------------------------------------------------------------------------------- |
| `color`     | `color` | 테마 기반 | 그림자의 색상입니다. (기본: `FluTheme.dark` ? `#000000` : `#999999`)                                    |
| `elevation` | `int`   | `5`       | 그림자의 깊이 또는 퍼짐 정도를 나타냅니다. 내부 `Repeater`의 모델 수가 되어 겹쳐지는 `Rectangle`의 수를 결정합니다. |
| `radius`    | `int`   | `4`       | 그림자 각 `Rectangle` 테두리의 모서리 둥글기 반경입니다.                                                    |

### 사용 예시 (내부적)

`FluPopup`, `FluMenu`, `FluFlyout` 등 떠 있는 듯한 효과가 필요한 컴포넌트의 배경 내부에 포함되어 사용됩니다.

```qml
// 예시: FluPopup 배경의 일부
FluRectangle {
    // ... 배경 속성 ...
    FluShadow {
        radius: 5 // 배경의 radius와 맞춰주는 것이 일반적
        // elevation, color 등은 기본값 사용 또는 필요시 재정의
    }
}
```

### 참고 사항

*   `anchors.fill: parent` 로 설정되어 부모 아이템의 크기에 맞춰 그림자가 생성됩니다.
*   `elevation` 값이 클수록 그림자가 더 넓고 흐릿하게 퍼져 보입니다.
*   각 `Rectangle`은 약간의 `opacity`와 함께 부모로부터 약간씩(`anchors.margins: -index`) 바깥쪽으로 그려지며, 테두리(`border`)를 사용하여 색상을 표현합니다. 