# Fluent UI 메뉴 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 메뉴 관련 컴포넌트들(`FluMenuBar`, `FluMenu`, `FluMenuBarItem`, `FluMenuItem`, `FluMenuSeparator`)에 대해 설명합니다. 이 컴포넌트들을 사용하여 애플리케이션의 주 메뉴 표시줄이나 컨텍스트 메뉴를 구성할 수 있습니다.

## 공통 임포트 방법

Fluent UI 메뉴 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Action, Layouts 등 추가
import QtQuick.Controls 2.15 // Action 사용 시
import QtQuick.Layouts 1.15 
```

---

## FluMenuBar

`FluMenuBar`는 일반적으로 애플리케이션 창의 상단에 위치하여 최상위 메뉴들을 가로로 나열하는 컨테이너입니다. 각 최상위 메뉴는 `FluMenu` 컴포넌트로 정의됩니다.

### 기반 클래스

`QtQuick.Templates.MenuBar` (T.MenuBar)

### 주요 사용법

`FluMenuBar` 내부에 하나 이상의 `FluMenu` 인스턴스를 배치합니다. 각 `FluMenu`의 `title` 프로퍼티가 메뉴바에 표시될 텍스트가 됩니다.

### 스타일링/고유 프로퍼티

| 이름          | 타입             | 기본값              | 설명                                                                      |
| :------------ | :--------------- | :------------------ | :------------------------------------------------------------------------ |
| `delegate`    | `Component`      | `FluMenuBarItem`    | 메뉴바에 표시될 각 메뉴(`FluMenu`)를 위한 시각적 아이템 컴포넌트입니다.        |
| `contentItem` | `Row`            | (내부 `Row`)        | `delegate`로 생성된 메뉴 아이템들을 가로로 배열하는 컨테이너입니다.           |
| `background`  | `Item`           | (내부 `Item`)       | 메뉴바의 배경 아이템입니다. 기본 높이는 30px입니다.                           |
| `spacing`     | `real`           | (템플릿 기본값)      | 메뉴 아이템(`FluMenuBarItem`) 간의 간격입니다.                             |

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

FluMenuBar {
    FluMenu {
        title: qsTr("파일(&F)") // 단축키(&F) 사용 가능
        Action { text: qsTr("새로 만들기") }
        Action { text: qsTr("열기...") }
        FluMenuSeparator {}
        Action { text: qsTr("종료") }
    }
    FluMenu {
        title: qsTr("편집(&E)")
        Action { text: qsTr("잘라내기") }
        Action { text: qsTr("복사") }
        Action { text: qsTr("붙여넣기") }
    }
}
```

---

## FluMenuBarItem

`FluMenuBarItem`은 `FluMenuBar` 내에서 각 최상위 메뉴(`FluMenu`)의 제목을 나타내는 시각적 컴포넌트입니다. 클릭하면 연결된 `FluMenu`가 드롭다운 형태로 표시됩니다. 일반적으로 직접 사용하기보다는 `FluMenuBar`의 `delegate`로 자동 생성됩니다.

### 기반 클래스

`QtQuick.Templates.MenuBarItem` (T.MenuBarItem)

### 스타일링/고유 프로퍼티

| 이름          | 타입        | 기본값              | 설명                                                                    |
| :------------ | :---------- | :------------------ | :---------------------------------------------------------------------- |
| `disabled`    | `bool`      | `false`             | 메뉴바 아이템 비활성화 여부 (`enabled = !disabled`).                         |
| `textColor`   | `color`     | (상태별 색상)        | 텍스트 색상. 활성화, 비활성화, 눌림 상태에 따라 자동으로 변경됩니다.                |
| `contentItem` | `FluText`   | (내부 `FluText`)    | 메뉴 제목 텍스트를 표시하는 아이템.                                            |
| `background`  | `Rectangle` | (커스텀 `Rectangle`) | 배경. 호버 상태(`highlighted`) 시 색상이 변경됩니다. 둥근 모서리(`radius: 3`) 적용. |
| `padding`     | `real`      | 6                   | 내부 여백.                                                               |
| `leftPadding` | `real`      | 12                  | 왼쪽 내부 여백.                                                          |
| `rightPadding`| `real`      | 16                  | 오른쪽 내부 여백.                                                         |

---

## FluMenu

`FluMenu`는 메뉴 항목(`Action`, `FluMenuItem`), 구분선(`FluMenuSeparator`), 그리고 다른 `FluMenu`(서브 메뉴)를 포함할 수 있는 컨테이너입니다. `FluMenuBar` 내에서 드롭다운 메뉴로 사용되거나, `popup()` 메소드를 호출하여 컨텍스트 메뉴로 표시될 수 있습니다.

### 기반 클래스

`QtQuick.Templates.Menu` (T.Menu)

### 주요 사용법

*   `FluMenuBar`의 자식으로 배치하여 드롭다운 메뉴를 구성합니다.
*   독립적으로 정의한 후 `popup()` 메소드를 호출하여 특정 위치(예: 마우스 클릭 위치)에 컨텍스트 메뉴를 표시합니다.
*   내부에 `Action`, `FluMenuItem`, `FluMenuSeparator`, 또는 다른 `FluMenu`를 배치하여 메뉴 구조를 정의합니다.

### 스타일링/고유 프로퍼티

| 이름               | 타입        | 기본값              | 설명                                                                                           |
| :----------------- | :---------- | :------------------ | :--------------------------------------------------------------------------------------------- |
| `animationEnabled` | `bool`      | `true`              | 메뉴가 나타나고 사라질 때 페이드 애니메이션 사용 여부.                                                     |
| `delegate`         | `Component` | `FluMenuItem`       | 메뉴 내 각 항목(`Action` 등)을 위한 기본 시각적 아이템 컴포넌트.                                            |
| `enter` / `exit`   | `Transition`| (페이드 효과)        | 메뉴 표시/숨김 시 적용되는 애니메이션 트랜지션.                                                         |
| `contentItem`      | `ListView`  | (내부 `ListView`)   | 메뉴 항목들을 수직으로 나열하고 스크롤 기능을 제공하는 컨테이너.                                                 |
| `background`       | `Rectangle` | (커스텀 `Rectangle`) | 메뉴의 배경. Fluent UI 테마 색상, 둥근 모서리(`radius: 5`), `FluShadow` 효과가 적용됩니다.                  |
| `overlap`          | `real`      | 1                   | `FluMenuBarItem` 또는 부모 `FluMenuItem`과 겹치는 정도(픽셀 단위).                                |
| `spacing`          | `real`      | 0                   | `ListView` 내의 메뉴 항목(`FluMenuItem`) 간의 수직 간격.                                           |

### 고유 메소드

*   `popup()`: 메뉴를 컨텍스트 메뉴로 표시합니다. 위치는 호출 시점의 컨텍스트에 따라 결정됩니다 (예: `MouseArea`의 `onClicked`에서 호출 시 마우스 위치 근처).

### 예제 (컨텍스트 메뉴)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

Item {
    width: 200; height: 100

    FluMenu {
        id: contextMenu
        Action { text: qsTr("항목 1") }
        Action { text: qsTr("항목 2") }
        FluMenuSeparator {}
        Action { text: qsTr("체크 항목"); checkable: true }
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.RightButton
        onClicked: (mouse) => {
            if (mouse.button === Qt.RightButton) {
                contextMenu.popup() // 오른쪽 클릭 시 메뉴 팝업
            }
        }
    }
}
```

---

## FluMenuItem

`FluMenuItem`은 `FluMenu` 내의 개별 항목을 나타냅니다. 텍스트와 아이콘을 가질 수 있으며, 클릭 시 `triggered` 시그널을 발생시켜 특정 동작을 수행하거나, `checkable` 속성을 통해 체크 상태를 가질 수 있고, `subMenu` 프로퍼티를 통해 서브 메뉴를 열 수도 있습니다. `Action` QML 타입을 사용하면 더 간결하게 메뉴 항목을 정의할 수 있으며, 내부적으로 `FluMenuItem`으로 렌더링됩니다.

### 기반 클래스

`QtQuick.Templates.MenuItem` (T.MenuItem)

### 주요 사용법

*   `FluMenu` 내부에 배치하여 메뉴 항목을 정의합니다.
*   `text` 프로퍼티로 표시될 텍스트를 설정합니다.
*   `iconSource` 프로퍼티에 `FluentIcons` 값을 지정하여 아이콘을 추가합니다.
*   `onTriggered` 핸들러나 `Action`의 `onTriggered`를 사용하여 항목 클릭 시 실행될 코드를 정의합니다.
*   `checkable: true`로 설정하여 체크 가능한 항목을 만듭니다.
*   내부에 다른 `FluMenu`를 정의하여 서브 메뉴를 만듭니다 (`arrow`가 자동으로 표시됨).

### 스타일링/고유 프로퍼티

| 이름           | 타입        | 기본값              | 설명                                                                                              |
| :------------- | :---------- | :------------------ | :------------------------------------------------------------------------------------------------ |
| `iconDelegate` | `Component` | `FluIcon`           | 아이콘을 렌더링하는 컴포넌트.                                                                        |
| `iconSpacing`  | `int`       | 5                   | 아이콘과 텍스트 사이의 간격.                                                                          |
| `iconSource`   | `int`       | -                   | 표시할 아이콘의 `FluentIcons` 열거형 값.                                                              |
| `iconSize`     | `int`       | 16                  | 아이콘 크기.                                                                                   |
| `textColor`    | `color`     | (상태별 색상)        | 텍스트 색상. 활성화, 비활성화, 눌림 상태에 따라 자동 변경.                                                   |
| `contentItem`  | `Item`      | (커스텀 `Item`)     | 아이콘(`FluLoader` 사용)과 텍스트(`FluText`)를 `Row` 레이아웃으로 배치하여 내용을 구성하는 아이템.                 |
| `indicator`    | `FluIcon`   | (체크 아이콘)        | `checkable: true`이고 `checked: true`일 때 표시되는 체크 마크 아이콘 (`FluentIcons.CheckMark`).           |
| `arrow`        | `FluIcon`   | (오른쪽 화살표 아이콘) | `subMenu`가 있을 때 표시되는 오른쪽 방향 화살표 아이콘 (`FluentIcons.ChevronRightMed`).                  |
| `background`   | `Item`      | (커스텀 `Item`)     | 배경. 호버 상태(`highlighted`) 시 색상이 변경되는 `Rectangle`을 포함.                                |
| `font`         | `font`      | `FluTextStyle.Body` | 텍스트 글꼴.                                                                                   |

### 예제 (FluMenuItem 직접 사용)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

FluMenu {
    id: myMenu
    FluMenuItem {
        text: qsTr("검색")
        iconSource: FluentIcons.Zoom
        onTriggered: console.log("검색 실행")
    }
    FluMenuItem {
        text: qsTr("체크")
        checkable: true
        checked: true 
        onTriggered: console.log("체크 상태:", checked)
    }
    FluMenuSeparator {}
    FluMenuItem {
        text: qsTr("비활성화 항목")
        enabled: false 
    }
}
```

---

## FluMenuSeparator

`FluMenuSeparator`는 `FluMenu` 내에서 항목들을 시각적으로 구분하기 위해 사용되는 수평선입니다.

### 기반 클래스

`QtQuick.Templates.MenuSeparator` (T.MenuSeparator)

### 주요 사용법

`FluMenu` 내에서 구분선을 표시하고 싶은 위치에 `FluMenuSeparator {}`를 추가합니다.

### 스타일링/고유 프로퍼티

| 이름          | 타입        | 기본값              | 설명                                                              |
| :------------ | :---------- | :------------------ | :---------------------------------------------------------------- |
| `contentItem` | `Rectangle` | (커스텀 `Rectangle`) | 구분선 역할을 하는 얇은 `Rectangle`. Fluent UI 테마 색상이 적용됩니다. |
| `padding`     | `real`      | 0                   | 내부 여백.                                                         |

---

## 종합 예제 (MenuBar 및 Context Menu)

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ApplicationWindow {
    visible: true
    width: 600
    height: 400
    title: "Fluent UI 메뉴 예제"

    menuBar: FluMenuBar {
        FluMenu {
            title: qsTr("파일")
            Action { text: qsTr("새로 만들기"); onTriggered: console.log("새로 만들기") }
            Action { text: qsTr("열기..."); onTriggered: console.log("열기") }
            FluMenu {
                title: qsTr("최근 파일")
                Action { text: "file1.txt" }
                Action { text: "file2.png" }
            }
            FluMenuSeparator {}
            Action { text: qsTr("종료"); onTriggered: Qt.quit() }
        }
        FluMenu {
            title: qsTr("도움말")
            Action { text: qsTr("정보"); onTriggered: console.log("정보") }
        }
    }

    // 컨텍스트 메뉴 정의
    FluMenu {
        id: myContextMenu
        FluMenuItem { text: qsTr("복사"); iconSource: FluentIcons.Copy }
        FluMenuItem { text: qsTr("붙여넣기"); iconSource: FluentIcons.Paste }
        FluMenuSeparator {}
        Action { text: qsTr("옵션 설정..."); checkable: true }
    }

    // 컨텍스트 메뉴 트리거 영역
    Rectangle {
        anchors.centerIn: parent
        width: 200; height: 150
        color: "lightgrey"
        border.color: "grey"
        
        FluText { 
            anchors.centerIn: parent
            text: qsTr("오른쪽 클릭") 
        }

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.RightButton
            onClicked: (mouse) => {
                if (mouse.button === Qt.RightButton) {
                    myContextMenu.popup() // 오른쪽 클릭 시 팝업
                }
            }
        }
    }
}
```

### 참고 사항

*   **`Action` vs `FluMenuItem`**: `Action` QML 타입은 메뉴 항목을 정의하는 더 간결한 방법이며, `text`, `iconSource`, `checkable`, `checked`, `enabled`, `onTriggered` 등의 프로퍼티를 지원합니다. 내부적으로 `FluMenu`의 `delegate` (기본값 `FluMenuItem`)를 사용하여 렌더링됩니다. 더 세밀한 제어(예: `iconSize` 변경)가 필요하면 `FluMenuItem`을 직접 사용합니다.
*   **서브 메뉴**: `FluMenu` 내부에 다른 `FluMenu`를 배치하면 자동으로 서브 메뉴 구조가 생성되고, 해당 `FluMenuItem`에는 오른쪽 화살표 아이콘이 표시됩니다.
*   **컨텍스트 메뉴 위치**: `popup()` 메소드는 호출되는 컨텍스트에 따라 적절한 위치에 메뉴를 표시합니다. 예를 들어 `MouseArea` 내에서 호출되면 마우스 커서 근처에 나타납니다. 