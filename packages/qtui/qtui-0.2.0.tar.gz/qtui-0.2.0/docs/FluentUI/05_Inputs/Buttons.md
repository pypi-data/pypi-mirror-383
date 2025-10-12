# Fluent UI 버튼 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 다양한 버튼 컴포넌트에 대해 설명합니다. 모든 버튼 컴포넌트는 기본 `QtQuick.Controls.Button`을 기반으로 하므로, 해당 컨트롤의 기본적인 속성, 메소드, 시그널을 상속받습니다.

## 공통 기능 및 속성

### 임포트 방법

모든 Fluent UI 버튼 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import FluentUI 1.0
import QtQuick.Controls 2.15 // Button 기본 기능 사용 시 필요할 수 있음
```

### 주요 공통 프로퍼티

대부분의 Fluent UI 버튼 컴포넌트는 다음 프로퍼티들을 공통적으로 가집니다.

| 이름                 | 타입     | 기본값              | 설명                                                                                               |
| :------------------- | :------- | :------------------ | :------------------------------------------------------------------------------------------------- |
| `text`               | `string` | `""`                | 버튼에 표시될 텍스트.                                                                              |
| `font`               | `font`   | `FluTextStyle.Body` | 버튼 텍스트의 글꼴.                                                                                |
| `disabled`           | `bool`   | `false`             | 버튼 비활성화 여부. `true`로 설정하면 버튼이 비활성화되고 `enabled`는 `false`가 됩니다.               |
| `enabled`            | `bool`   | `!disabled` 등      | 버튼 활성화 여부 (읽기 전용). `disabled` 프로퍼티나 특정 상태(`loading` 등)에 의해 제어됩니다.          |
| `focusPolicy`        | `enum`   | `Qt.TabFocus`       | 키보드 포커스를 받는 정책 (예: `Qt.TabFocus`, `Qt.StrongFocus`, `Qt.NoFocus`).                     |
| `hovered`            | `bool`   | -                   | 마우스 커서가 버튼 위에 있는지 여부 (읽기 전용).                                                      |
| `pressed`            | `bool`   | -                   | 버튼이 현재 눌려있는지 여부 (읽기 전용).                                                            |
| `activeFocus`        | `bool`   | -                   | 현재 활성 키보드 포커스를 가지고 있는지 여부 (읽기 전용). `visualFocus` 와 유사하게 사용될 수 있음. |
| `contentDescription` | `string` | `""`                | 접근성(Accessibility)을 위한 버튼 설명. 스크린 리더 등이 사용합니다.                               |
| `horizontalPadding`  | `real`   | (버튼 타입별 상이)  | 내용과 버튼 경계 사이의 좌우 여백.                                                                   |
| `verticalPadding`    | `real`   | (버튼 타입별 상이)  | 내용과 버튼 경계 사이의 상하 여백.                                                                   |

**참고:** 색상 관련 프로퍼티 (`normalColor`, `hoverColor`, `pressedColor`, `disableColor`, `textColor` 등)도 대부분의 버튼에 존재하지만, 구체적인 색상 값이나 계산 방식은 각 버튼의 타입, 상태 (`checked` 등), 그리고 `FluTheme` (다크/라이트 모드)에 따라 달라집니다. 자세한 내용은 각 버튼별 설명을 참고하세요.

### 주요 공통 메소드

`QtQuick.Controls.Button`에서 상속받는 주요 메소드입니다.

| 이름                          | 파라미터                     | 반환 타입 | 설명                                     |
| :---------------------------- | :--------------------------- | :-------- | :--------------------------------------- |
| `click()`                     | 없음                         | `void`    | 프로그램적으로 버튼 클릭을 발생시킵니다. |
| `forceActiveFocus(reason)`    | `reason`: `Qt.FocusReason` (선택) | `void`    | 버튼에 강제로 활성 포커스를 설정합니다. |

### 주요 공통 시그널

`QtQuick.Controls.Button`에서 상속받는 주요 시그널입니다.

| 이름       | 파라미터 | 반환타입 | 설명                                                     |
| :--------- | :------- | :------- | :------------------------------------------------------- |
| `clicked()`  | 없음     | -        | 버튼이 성공적으로 클릭되었을 때 (눌렀다 떼었을 때) 발생합니다. |
| `pressed()`  | 없음     | -        | 버튼이 눌렸을 때 발생합니다.                             |
| `released()` | 없음     | -        | 버튼에서 손을 떼었을 때 발생합니다.                       |
| `canceled()` | 없음     | -        | 버튼 누름이 취소되었을 때 (예: 누른 상태로 포인터 이탈) 발생. |

---

## 1. FluButton

테두리와 배경이 있는 표준 버튼입니다. 일반적으로 가장 많이 사용되는 버튼 형태입니다.

### 고유/특징적 프로퍼티

| 이름           | 타입   | 기본값                    | 설명                                            |
| :------------- | :----- | :------------------------ | :---------------------------------------------- |
| `normalColor`  | `color`  | `FluTheme` 기반 자동 계산 | 기본 상태 **배경** 색상                         |
| `hoverColor`   | `color`  | `FluTheme` 기반 자동 계산 | 마우스 호버 시 **배경** 색상                    |
| `disableColor` | `color`  | `FluTheme` 기반 자동 계산 | 비활성화 상태 **배경** 색상                     |
| `textColor`    | `color`  | 상태 및 `FluTheme` 기반   | 현재 상태에 따른 **텍스트** 색상 (읽기 전용)    |
| `horizontalPadding` | `real` | `12`                      | 좌우 내부 여백                            |
| `verticalPadding`   | `real` | `0`                       | 상하 내부 여백                            |

*(이 외 공통 프로퍼티, 메소드, 시그널 상속)*

### 예제

```qml
FluButton {
    text: qsTr("표준 버튼")
    onClicked: {
        console.log("FluButton 클릭됨")
    }
}
```

### 참고 사항

*   `FluControlBackground`를 사용하여 배경 및 그림자 효과를 구현합니다.
*   색상은 `FluTheme` (다크/라이트 모드)에 따라 동적으로 달라집니다.

---

## 2. FluTextButton

텍스트만 표시되는 기본적인 버튼입니다. 배경은 투명하며, 마우스 호버 및 클릭 시에만 배경색이 나타납니다.

### 고유/특징적 프로퍼티

| 이름                     | 타입   | 기본값                     | 설명                                 |
| :----------------------- | :----- | :------------------------- | :----------------------------------- |
| `normalColor`            | `color`  | `FluTheme.primaryColor`    | 기본 상태 **텍스트** 색상            |
| `hoverColor`             | `color`  | `FluTheme` 기반 자동 계산  | 마우스 호버 시 **텍스트** 색상       |
| `pressedColor`           | `color`  | `FluTheme` 기반 자동 계산  | 버튼 눌렀을 때 **텍스트** 색상       |
| `disableColor`           | `color`  | `FluTheme` 기반 자동 계산  | 비활성화 상태 **텍스트** 색상        |
| `backgroundNormalColor`  | `color`  | `FluTheme.itemNormalColor` | 기본 상태 배경 색상 (보통 투명)      |
| `backgroundHoverColor`   | `color`  | `FluTheme.itemHoverColor`  | 마우스 호버 시 배경 색상             |
| `backgroundPressedColor` | `color`  | `FluTheme.itemPressColor`  | 버튼 눌렀을 때 배경 색상             |
| `backgroundDisableColor` | `color`  | `FluTheme.itemNormalColor` | 비활성화 상태 배경 색상              |
| `horizontalPadding`      | `real`   | `6`                        | 좌우 내부 여백                     |

*(이 외 공통 프로퍼티, 메소드, 시그널 상속)*

### 예제

```qml
FluTextButton {
    text: qsTr("확인")
    onClicked: {
        console.log("FluTextButton 클릭됨")
    }
}
```

### 참고 사항

*   가장 기본적인 형태의 버튼으로, 강조 효과 없이 간단한 액션에 사용하기 적합합니다.
*   배경은 기본적으로 투명하며, 상호작용 시에만 `backgroundHoverColor` 또는 `backgroundPressedColor`가 적용됩니다.

---

## 3. FluFilledButton

주요 동작(Primary Action)을 나타내는 데 사용되는 채워진 스타일의 버튼입니다. 배경색이 `FluTheme.primaryColor`로 강조됩니다.

### 고유/특징적 프로퍼티

| 이름           | 타입   | 기본값                  | 설명                                     |
| :------------- | :----- | :---------------------- | :--------------------------------------- |
| `normalColor`  | `color`  | `FluTheme.primaryColor` | 기본 상태 **배경** 색상                  |
| `hoverColor`   | `color`  | `FluTheme` 기반 자동 계산 | 마우스 호버 시 **배경** 색상             |
| `pressedColor` | `color`  | `FluTheme` 기반 자동 계산 | 버튼 눌렀을 때 **배경** 색상             |
| `disableColor` | `color`  | `FluTheme` 기반 자동 계산 | 비활성화 상태 **배경** 색상              |
| `textColor`    | `color`  | 상태 및 `FluTheme` 기반 | 현재 상태에 따른 **텍스트** 색상 (읽기 전용) |
| `horizontalPadding` | `real` | `12`                    | 좌우 내부 여백                       |
| `verticalPadding`   | `real` | `0`                     | 상하 내부 여백                       |

*(이 외 공통 프로퍼티, 메소드, 시그널 상속)*

### 예제

```qml
FluFilledButton {
    text: qsTr("채워진 버튼")
    onClicked: {
        console.log("FluFilledButton 클릭됨")
    }
}
```

### 참고 사항

*   페이지나 다이얼로그 등에서 가장 중요한 긍정적 액션(예: 저장, 확인)에 사용하는 것이 좋습니다.
*   활성화 상태에서는 약간의 그림자와 테두리가 표시될 수 있습니다.

---

## 4. FluToggleButton

선택/해제 상태를 가지는 토글 버튼입니다. `checked` 프로퍼티로 상태를 제어하고 확인할 수 있습니다.

### 고유/특징적 프로퍼티

| 이름            | 타입     | 기본값                           | 설명                                                                     |
| :-------------- | :------- | :------------------------------- | :----------------------------------------------------------------------- |
| `checked`       | `bool`   | `false` (상속됨)                 | 버튼의 선택(체크) 상태. `checkable` 프로퍼티는 `true`로 고정됩니다.        |
| `clickListener` | `function`| `function(){ checked = !checked }` | 클릭 시 실행될 사용자 정의 함수. 기본적으로 `checked` 상태를 토글합니다. |
| `normalColor`   | `color`  | `checked` 및 `FluTheme` 기반     | `checked` 상태에 따른 기본 **배경** 색상                                 |
| `hoverColor`    | `color`  | `checked` 및 `FluTheme` 기반     | `checked` 상태에 따른 마우스 호버 시 **배경** 색상                       |
| `pressedColor`  | `color`  | `FluTheme` 기반 자동 계산        | `checked` 상태에 따른 버튼 눌렀을 때 **배경** 색상                       |
| `disableColor`  | `color`  | `checked` 및 `FluTheme` 기반     | `checked` 상태에 따른 비활성화 상태 **배경** 색상                        |
| `textColor`     | `color`  | 상태 및 `FluTheme` 기반          | 현재 상태(`checked` 포함)에 따른 **텍스트** 색상 (읽기 전용)               |
| `horizontalPadding` | `real` | `12`                             | 좌우 내부 여백                                                           |
| `verticalPadding`   | `real` | `0`                              | 상하 내부 여백                                                           |

*(이 외 공통 프로퍼티, 메소드, 시그널 상속)*

### 고유 시그널

| 이름       | 파라미터 | 반환타입 | 설명                           |
| :--------- | :------- | :------- | :----------------------------- |
| `toggled()`  | 없음     | -        | `checked` 상태가 변경될 때 발생. |

### 예제

```qml
FluToggleButton {
    id: toggleBtn
    text: qsTr("토글 버튼")
    checked: false
    onToggled: { // checked 상태 변경 시 호출됨
        console.log("토글 상태:", checked)
    }
    // onClicked: { /* 기본 토글 동작 외 추가 작업 */ }
}
```

### 참고 사항

*   클릭 시 기본적으로 `checked` 상태가 반전됩니다. `clickListener`를 재정의하여 이 동작을 변경할 수 있습니다.
*   버튼의 시각적 스타일(색상, 테두리, 그림자 등)은 `checked` 상태와 `FluTheme`에 따라 동적으로 변경됩니다.

---

## 5. FluProgressButton

클릭 후 진행 상태를 시각적으로 표시할 수 있는 버튼입니다. `FluButton`을 기반으로 합니다.

### 고유/특징적 프로퍼티

| 이름         | 타입   | 기본값                  | 설명                                                                     |
| :----------- | :----- | :---------------------- | :----------------------------------------------------------------------- |
| `progress`   | `real` | `0.0`                   | 진행 상태 (0.0 ~ 1.0). 1.0이 되면 버튼 모양이 완료 상태(채워짐)로 변경됩니다. |
| `normalColor`| `color`| 진행 상태 및 `FluTheme` 기반 | 진행 완료(`progress`=1) 여부에 따른 기본 **배경** 색상                     |
| `hoverColor` | `color`| 진행 상태 및 `FluTheme` 기반 | 진행 완료 여부에 따른 마우스 호버 시 **배경** 색상                         |
| `pressedColor`| `color`| `FluTheme` 기반 자동 계산 | 진행 완료 여부에 따른 버튼 눌렀을 때 **배경** 색상                         |
| `disableColor`| `color`| 진행 상태 및 `FluTheme` 기반 | 진행 완료 여부에 따른 비활성화 상태 **배경** 색상                          |
| `textColor`  | `color`| 상태 및 `FluTheme` 기반 | 현재 상태(진행 완료 여부 포함)에 따른 **텍스트** 색상 (읽기 전용)          |

*(이 외 `FluButton` 및 공통 프로퍼티, 메소드, 시그널 상속)*

### 예제

```qml
FluProgressButton {
    id: progressBtn
    text: qsTr("진행 시작")
    progress: 0.0
    onClicked: {
        // 예: Timer 등을 사용하여 progress 값을 0.0에서 1.0으로 변경
        progress = 0.0;
        // progressTimer.start();
    }
    // progress 값 변화 감지 (Component.onCompleted 또는 Connections 사용)
    Connections {
        target: progressBtn
        function onProgressChanged() {
            if (progressBtn.progress === 1.0) {
                progressBtn.text = qsTr("완료");
            } else if (progressBtn.progress === 0.0) {
                progressBtn.text = qsTr("진행 시작");
            }
        }
    }
}
```

### 참고 사항

*   `progress` 값이 0에서 1로 증가함에 따라 버튼 하단에 진행 바(파란색)가 표시되고, 1이 되면 배경 전체가 채워지며 시각적으로 완료 상태를 나타냅니다.
*   진행 상태에 따라 버튼의 시각적 스타일(색상, 테두리 등)이 변경됩니다.

---

## 6. FluLoadingButton

작업 진행 중임을 나타내는 로딩 인디케이터(`FluProgressRing`)를 표시할 수 있는 버튼입니다. `FluButton`을 기반으로 합니다.

### 고유/특징적 프로퍼티

| 이름       | 타입   | 기본값      | 설명                                                                               |
| :--------- | :----- | :---------- | :--------------------------------------------------------------------------------- |
| `loading`  | `bool` | `false`     | 로딩 상태 여부. `true` 이면 로딩 인디케이터가 표시되고 버튼은 자동으로 비활성화됩니다. |
| `disabled` | `bool` | `loading`   | 버튼 비활성화 여부. `loading`이 `true`이면 자동으로 `true`가 됩니다.                 |
| `enabled`  | `bool` | `!loading`  | 버튼 활성화 여부 (읽기 전용). `loading` 프로퍼티에 의해 제어됩니다.                  |

*(이 외 `FluButton` 및 공통 프로퍼티, 메소드, 시그널 상속)*

### 예제

```qml
FluLoadingButton {
    id: loadingBtn
    text: qsTr("작업 시작")
    loading: false
    onClicked: {
        if (!loading) { // 로딩 중이 아닐 때만 작업 시작
            loading = true // 작업 시작 시 로딩 상태로 변경
            // 실제 비동기 작업 수행...
            // 작업 완료 후 콜백 등에서: loading = false
        }
    }
}
```

### 참고 사항

*   `loading` 프로퍼티를 `true`로 설정하면 버튼 텍스트 옆에 `FluProgressRing`이 나타나고 버튼은 상호작용할 수 없도록 비활성화됩니다.
*   네트워크 요청, 파일 처리 등 시간이 걸리는 작업을 사용자에게 알릴 때 유용합니다.

---

## 7. FluDropDownButton

클릭 시 드롭다운 메뉴(`FluMenu`)를 표시하는 버튼입니다. `FluButton`을 기반으로 합니다.

### 고유/특징적 프로퍼티

| 이름          | 타입         | 기본값              | 설명                                                                                |
| :------------ | :----------- | :------------------ | :---------------------------------------------------------------------------------- |
| `contentData` | `list<Object>`| `[]`                | **기본 프로퍼티**. 드롭다운 메뉴에 표시될 아이템 리스트. `FluMenuItem` 등을 자식으로 추가합니다. |
| `rightPadding`| `real`       | `35`                | 오른쪽 내부 여백. 드롭다운 화살표 아이콘 공간 확보를 위해 기본값이 조정됨.           |
| `menu`        | `FluMenu`    | -                   | 내부적으로 사용하는 드롭다운 메뉴 객체 (읽기 전용). 메뉴의 속성에 접근할 때 사용 가능. |
| `textColor`   | `color`      | `FluTheme` 기반     | 현재 상태에 따른 **텍스트 및 드롭다운 화살표** 색상 (읽기 전용)                    |

*(이 외 `FluButton` 및 공통 프로퍼티, 메소드, 시그널 상속)*

### 예제

```qml
FluDropDownButton {
    text: qsTr("옵션 선택")
    // contentData 프로퍼티에 FluMenuItem들이 추가됨
    FluMenuItem { text: qsTr("옵션 1") }
    FluMenuItem { text: qsTr("옵션 2") }
    FluMenuSeparator {} // 구분선
    FluMenuItem {
        text: qsTr("옵션 3 (클릭)")
        onClicked: { // 메뉴 아이템의 클릭 시그널 처리
            console.log("옵션 3 선택됨")
        }
    }
}
```

### 참고 사항

*   버튼 내부에 `FluMenuItem`, `FluMenuSeparator` 등을 직접 자식 요소로 추가하면 `contentData` 프로퍼티에 자동으로 할당됩니다.
*   버튼 클릭 시 `FluMenu`가 열리고, 메뉴의 위치는 버튼 아래 또는 위에 공간이 충분한지에 따라 자동으로 결정됩니다.
*   버튼 오른쪽에는 드롭다운 메뉴가 있음을 나타내는 아래쪽 화살표 아이콘(`FluentIcons.ChevronDown`)이 표시됩니다.
*   메뉴 항목 자체의 클릭 이벤트는 각 `FluMenuItem`의 `onClicked` 핸들러에서 처리해야 합니다.

---

## 8. FluImageButton

버튼의 상태(기본, 호버, 눌림)에 따라 다른 이미지를 배경으로 표시하는 버튼입니다. `QtQuick.Controls.Button`을 기반으로 하며, 배경으로 `BorderImage`를 사용합니다.

### 고유/특징적 프로퍼티

| 이름           | 타입     | 기본값 | 설명                                              |
| :------------- | :------- | :----- | :------------------------------------------------ |
| `normalImage`  | `string` | `""`   | 기본 상태일 때 표시될 배경 이미지의 URL 또는 경로.    |
| `hoveredImage` | `string` | `""`   | 마우스 호버 상태일 때 표시될 배경 이미지의 URL 또는 경로. |
| `pushedImage`  | `string` | `""`   | 버튼이 눌린 상태일 때 표시될 배경 이미지의 URL 또는 경로. |

*(이 외 공통 프로퍼티, 메소드, 시그널 상속. 단, `text` 프로퍼티는 직접 사용되지 않으며, 배경 이미지 설정이 주요 기능입니다.)*

### 예제

```qml
FluImageButton {
    width: 32
    height: 32
    normalImage: "qrc:/images/button_normal.png"
    hoveredImage: "qrc:/images/button_hover.png"
    pushedImage: "qrc:/images/button_pressed.png"

    onClicked: {
        console.log("Image Button Clicked!")
    }
}
```

### 참고 사항

*   이 버튼은 주로 아이콘 버튼과 같이 상태에 따라 시각적 피드백이 이미지로 변경되어야 하는 경우에 사용됩니다.
*   배경으로 `BorderImage`를 사용하므로, 이미지 소스는 9분할(nine-patch) 이미지 형식을 지원하여 크기 조절 시 왜곡을 방지할 수 있습니다 (이미지 자체에 테두리 정보가 있는 경우).
*   `text` 프로퍼티를 직접 설정해도 화면에 표시되지 않으므로, 텍스트가 필요한 경우 `FluIconButton` 사용을 고려하세요.