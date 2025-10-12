# Fluent UI 툴팁 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTooltip` 컴포넌트에 대해 설명합니다. 툴팁은 사용자가 특정 UI 요소 위에 마우스를 올렸을 때 나타나는 작은 정보 팝업입니다.

## 공통 임포트 방법

Fluent UI 툴팁 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluTooltip

`FluTooltip`은 사용자가 마우스를 특정 컨트롤 위에 올렸을 때(hover) 해당 컨트롤에 대한 간단한 설명이나 힌트를 제공하는 작은 팝업 창을 표시합니다. 일반적으로 잠시 후에 나타나며, 마우스가 컨트롤 밖으로 나가면 사라집니다. `QtQuick.Templates.ToolTip`을 기반으로 하며 Fluent UI 스타일이 적용되었습니다.

### 기반 클래스

`QtQuick.Templates.ToolTip` (T.ToolTip)

### 주요 상속 프로퍼티 (T.ToolTip)

`FluTooltip`은 `T.ToolTip`의 모든 표준 프로퍼티를 상속받습니다. 자주 사용되는 멤버는 다음과 같습니다:

*   `text`: `string` - 툴팁에 표시될 텍스트 내용.
*   `delay`: `int` - 마우스가 컨트롤 위에 머무르기 시작한 후 툴팁이 나타나기까지의 지연 시간 (밀리초 단위, 기본값은 보통 0 또는 테마 설정값).
*   `timeout`: `int` - 툴팁이 자동으로 사라지기까지 표시되는 시간 (밀리초 단위, 기본값은 -1로 자동 숨김 비활성화).
*   `visible`: `bool` - 툴팁의 현재 표시 상태. 일반적으로 직접 제어하기보다는 부모 컨트롤의 상태(예: `hovered`)에 바인딩하여 사용합니다.

### 고유/스타일링 프로퍼티

`FluTooltip`은 Fluent UI 스타일을 적용하기 위해 내부 아이템과 배경을 재정의합니다:

| 이름          | 타입        | 기본값              | 설명                                                                             |
| :------------ | :---------- | :------------------ | :------------------------------------------------------------------------------- |
| `contentItem` | `FluText`   | (커스텀 `FluText`)  | 툴팁의 `text` 프로퍼티 내용을 표시하는 내부 텍스트 아이템. `FluTextStyle.Body` 폰트를 사용합니다. |
| `background`  | `Rectangle` | (커스텀 `Rectangle`) | 툴팁의 배경. Fluent UI 테마(어둡거나 밝음)에 맞는 색상, 둥근 모서리(`radius: 3`), `FluShadow` 효과가 적용됩니다. |
| `font`        | `font`      | `FluTextStyle.Body` | 툴팁 텍스트에 적용될 기본 글꼴.                                                       |

### 고유 메소드 / 시그널

`FluTooltip` 자체에 고유하게 추가된 메소드나 시그널은 없습니다.

### 예제

**1. `FluButton`에 툴팁 추가하기:**

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

FluButton {
    id: myButton
    text: qsTr("삭제")
    
    // 버튼 위에 마우스를 올리면 툴팁이 보이도록 설정
    FluTooltip {
        visible: myButton.hovered
        text: qsTr("이 버튼을 클릭하면 항목이 삭제됩니다.")
        delay: 500 // 0.5초 후에 툴팁 표시
    }
    
    onClicked: {
        // 삭제 로직...
    }
}
```

**2. `FluIconButton`의 내장 툴팁 활용:**

`FluIconButton`은 `text` 프로퍼티를 설정하면 자동으로 해당 텍스트를 내용으로 하는 `FluTooltip`을 표시합니다. 별도로 `FluTooltip` 컴포넌트를 추가할 필요가 없습니다.

```qml
import QtQuick 2.15
import FluentUI 1.0

FluIconButton {
    iconSource: FluentIcons.Delete
    text: qsTr("삭제") // 이 텍스트가 툴팁으로 표시됨
    
    onClicked: {
        // 삭제 로직...
    }
}
```

### 참고 사항

*   **표시 제어**: `FluTooltip`의 `visible` 속성을 부모 컨트롤의 `hovered` 속성에 바인딩하는 것이 가장 일반적인 사용 방식입니다.
*   **위치**: 기본적으로 툴팁은 부모 컨트롤의 위쪽 중앙에 약간의 간격을 두고 표시됩니다 (`y: -implicitHeight - 3`).
*   **자동 숨김 정책**: `closePolicy` 프로퍼티는 `T.Popup`에서 상속받으며, 기본적으로 Escape 키를 누르거나 툴팁 외부 영역을 클릭/릴리스하면 툴팁이 닫히도록 설정되어 있습니다.
*   **`FluIconButton` 통합**: `FluIconButton`을 사용하는 경우, 간단한 툴팁은 `text` 프로퍼티 설정만으로 충분합니다. 더 복잡한 제어(예: `delay` 변경)가 필요하다면 예제 1과 같이 직접 `FluTooltip`을 추가할 수 있습니다. 