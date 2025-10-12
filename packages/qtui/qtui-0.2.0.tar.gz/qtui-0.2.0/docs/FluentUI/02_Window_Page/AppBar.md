# Fluent UI 앱 바 (FluAppBar)

이 문서에서는 `FluentUI` 모듈의 `FluAppBar` 컴포넌트에 대해 설명합니다. `FluAppBar`는 `FluWindow`의 상단에 위치하여 창 제목, 아이콘 및 표준 창 제어 버튼들을 제공하는 기본 앱 바(제목 표시줄)입니다.

## 공통 임포트 방법

`FluAppBar`는 일반적으로 `FluWindow` 내에서 자동으로 사용되므로 직접 임포트할 필요는 적지만, 만약 별도로 사용하거나 커스터마이징한다면 다음 임포트가 필요할 수 있습니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluAppBar

`FluAppBar`는 Fluent Design 스타일의 창 제목 표시줄을 제공합니다. 창 제목 텍스트, 애플리케이션 아이콘, 그리고 운영체제 스타일에 맞는 창 제어 버튼(최소화, 최대화/복원, 닫기)을 포함합니다. 추가적으로 '항상 위' 토글 버튼과 다크/라이트 모드 전환 버튼을 표시하는 옵션도 제공합니다. `FluWindow`의 `appBar` 프로퍼티의 기본값으로 설정되어 있으며, 프레임리스 윈도우 모드에서 창 이동 및 제어를 위한 핵심적인 역할을 수행합니다.

### 기반 클래스

`Rectangle`

### 고유/특징적 프로퍼티

| 이름                   | 타입     | 기본값                    | 설명                                                                                                  |
| :--------------------- | :------- | :------------------------ | :---------------------------------------------------------------------------------------------------- |
| `title`                | `string` | ""                      | 앱 바에 표시될 창 제목 텍스트입니다.                                                                       |
| `darkText`, `lightText`, `minimizeText`, `restoreText`, `maximizeText`, `closeText`, `stayTopText`, `stayTopCancelText` | `string` | (국제화된 문자열)         | 각 제어 버튼 위에 마우스를 올렸을 때 표시되는 툴팁 텍스트입니다. `qsTr`을 통해 국제화를 지원합니다.                                |
| `textColor`            | `color`  | `FluTheme.fontPrimaryColor`| 제목 텍스트 및 기본 아이콘 버튼의 색상입니다.                                                                   |
| `minimizeNormalColor`, `minimizeHoverColor`, `minimizePressColor` | `color` | (테마 기반 색상)         | 최소화 버튼의 상태(기본, 호버, 누름)에 따른 배경색입니다.                                                             |
| `maximizeNormalColor`, `maximizeHoverColor`, `maximizePressColor` | `color` | (테마 기반 색상)         | 최대화/복원 버튼의 상태에 따른 배경색입니다.                                                                  |
| `closeNormalColor`, `closeHoverColor`, `closePressColor` | `color` | (테마/상태 기반 색상)     | 닫기 버튼의 상태에 따른 배경색입니다. 호버/누름 시에는 강조를 위해 일반적으로 빨간색 계열이 사용됩니다.                                      |
| `showDark`             | `bool`   | `false`                   | 다크/라이트 모드 전환 버튼 표시 여부입니다.                                                                    |
| `showClose`            | `bool`   | `true`                    | 닫기 버튼 표시 여부입니다.                                                                            |
| `showMinimize`         | `bool`   | `true`                    | 최소화 버튼 표시 여부입니다.                                                                          |
| `showMaximize`         | `bool`   | `true`                    | 최대화/복원 버튼 표시 여부입니다. 창 크기 조절이 불가능하면(`fixSize: true`) 자동으로 숨겨질 수 있습니다.                                |
| `showStayTop`          | `bool`   | `true`                    | '항상 위' 토글 버튼 표시 여부입니다.                                                                     |
| `titleVisible`         | `bool`   | `true`                    | 창 제목 텍스트 표시 여부입니다.                                                                        |
| `icon`                 | `url`    | `undefined`               | 제목 텍스트 왼쪽에 표시될 아이콘 이미지의 URL입니다. `FluWindow`의 `windowIcon` 프로퍼티를 통해 전달받는 경우가 많습니다.                                |
| `iconSize`             | `int`    | `20`                      | 아이콘의 너비와 높이입니다.                                                                            |
| `isMac`                | `readonly bool` | (계산됨)                 | 현재 운영체제가 macOS인지 여부를 나타냅니다. `true`이면 macOS 스타일의 버튼 레이아웃(좌측 정렬)이 사용됩니다.                                    |
| `buttonStayTop`, `buttonMinimize`, `buttonMaximize`, `buttonClose`, `buttonDark` | `alias` | (내부 버튼 아이템)        | 각 제어 버튼(`FluIconButton` 또는 `FluImageButton`) 아이템에 대한 읽기 전용 별칭입니다.                                                     |
| `layoutMacosButtons`, `layoutStandardbuttons` | `alias` | (내부 레이아웃 아이템)    | macOS 및 표준(Windows 등) 스타일의 버튼들을 담는 레이아웃 아이템에 대한 읽기 전용 별칭입니다. `FluWindow`의 `setHitTestVisible`과 함께 사용될 수 있습니다. |

### 고유 시그널

`FluAppBar` 자체에는 공개적인 시그널이 없습니다. 사용자가 각 제어 버튼을 클릭하면, 내부적으로 `FluWindow`의 해당 동작을 수행하는 JavaScript 함수(`minClickListener`, `maxClickListener`, `closeClickListener`, `stayTopClickListener`, `darkClickListener`)들이 호출됩니다.

### 고유 메소드

`FluAppBar`에는 사용자가 직접 호출할 공개 메소드가 없습니다.

### 예제

`FluAppBar`는 주로 `FluWindow` 내부에서 사용됩니다. `FluWindow`의 프로퍼티를 통해 `FluAppBar`의 일부 속성을 제어할 수 있습니다.

```qml
import QtQuick 2.15
import FluentUI 1.0

FluWindow {
    title: "Custom AppBar Window" // FluAppBar의 title로 전달됨
    windowIcon: "qrc:/res/my_icon.png" // FluAppBar의 icon으로 전달됨
    width: 800
    height: 600
    
    // FluAppBar의 특정 버튼 숨기기 예시
    showDark: true     // 다크 모드 버튼 표시
    showStayTop: false // 항상 위 버튼 숨김
    
    // appBar 프로퍼티를 통해 직접 접근하여 커스터마이징 (권장되지는 않음)
    Component.onCompleted: {
        // appBar.minimizeText = "최소화"
    }
    
    FluText {
        anchors.centerIn: parent
        text: "Window with customized AppBar settings"
    }
}
```

### 관련 컴포넌트/객체

*   **`FluWindow`**: `FluAppBar`를 기본 앱 바로 사용하는 주 컨테이너입니다.
*   **`FluTheme`**: 앱 바의 색상과 아이콘 색상 등에 영향을 줍니다.
*   **`FluTools`**: 운영체제(`isMac`)를 감지하는 데 사용됩니다.
*   **`FluentIcons`**: 제어 버튼들에 사용되는 아이콘 글꼴을 제공합니다.
*   **`FluIconButton` / `FluImageButton`**: 제어 버튼들의 기반 컴포넌트입니다.

### 참고 사항

*   `FluAppBar`는 `FluWindow`와 긴밀하게 통합되어 있으며, `FluWindow`의 상태(최대화 여부, 항상 위 설정 등)에 따라 버튼의 아이콘이나 상태가 변경됩니다.
*   운영체제에 따라 버튼의 레이아웃과 모양이 다릅니다 (macOS vs Windows/Linux).
*   프레임리스 모드(`useSystemAppBar: false`)에서 `FluAppBar`의 빈 영역을 마우스로 드래그하면 창을 이동시킬 수 있으며, 더블 클릭하면 창을 최대화하거나 복원할 수 있습니다. 