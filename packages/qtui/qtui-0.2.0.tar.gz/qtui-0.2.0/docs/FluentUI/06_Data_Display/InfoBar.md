# Fluent UI 정보 표시줄(InfoBar) 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluInfoBar` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 직접적인 시각적 요소가 아니라, 애플리케이션 상태에 대한 메시지를 화면에 표시하는 기능을 제공하는 관리자(Manager) 또는 서비스(Service) 역할을 합니다.

## 공통 임포트 방법

`FluInfoBar`의 메소드를 사용하려면 먼저 해당 컴포넌트의 인스턴스를 생성해야 합니다. 일반적으로 애플리케이션의 최상위 레벨(예: `main.qml`)에서 인스턴스를 만들고 `root` 프로퍼티를 설정합니다. 사용하려는 QML 파일에서는 이 인스턴스를 참조하거나 해당 인스턴스의 메소드를 호출할 수 있어야 합니다.

```qml
// main.qml 또는 최상위 컴포넌트
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

ApplicationWindow {
    id: window
    // ...
    FluInfoBar {
        id: globalInfoBar
        root: Overlay.overlay // 필수: 정보 표시줄이 나타날 부모 설정
    }
    // ...
}

// 다른 QML 파일에서 사용 시 (globalInfoBar에 접근 가능하다고 가정)
// globalInfoBar.showInfo("메시지")
```

---

## FluInfoBar

`FluInfoBar`는 사용자에게 작업 결과나 상태 변경에 대한 피드백을 제공하기 위해 비간섭적인 메시지를 표시하는 데 사용됩니다. 메소드 호출을 통해 정보(Info), 경고(Warning), 오류(Error), 성공(Success) 상태를 나타내는 표준 스타일의 정보 표시줄이나, 사용자 정의 컴포넌트를 포함하는 정보 표시줄을 화면에 동적으로 생성하고 관리합니다. 정보 표시줄은 기본적으로 화면 상단(`layoutY` 위치)에 나타나며, 여러 개가 호출될 경우 세로로 쌓입니다. 일정 시간 후 자동으로 사라지거나, 사용자가 직접 닫기 버튼을 눌러 닫을 수 있습니다.

### 기반 클래스

`FluObject`

### 고유/특징적 프로퍼티

| 이름      | 타입   | 기본값 | 설명                                                                                                                                 | 필수 | 
| :-------- | :----- | :----- | :----------------------------------------------------------------------------------------------------------------------------------- | :--- |
| `root`    | `Item` | -      | 정보 표시줄 레이아웃이 생성될 부모 아이템. 정보 표시줄이 다른 UI 요소 위에 올바르게 표시되도록 `Overlay.overlay` 또는 최상위 뷰를 지정해야 합니다. | 예   | 
| `layoutY` | `int`  | `75`   | 정보 표시줄 스택이 처음 나타날 기준 세로(Y) 위치.                                                                                       | 아니오| 

### 고유 메소드

| 이름            | 파라미터                                                            | 반환타입 | 설명                                                                                                                                            |
| :-------------- | :------------------------------------------------------------------ | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| `showSuccess`   | `string`: `text`, `int`: `duration` (1000), `string`: `moremsg` ("?") | `Item`   | **성공** 스타일의 정보 표시줄을 표시합니다. 생성된 정보 표시줄 인스턴스를 반환합니다.                                                                 |
| `showInfo`      | `string`: `text`, `int`: `duration` (1000), `string`: `moremsg` ("?") | `Item`   | **정보** 스타일의 정보 표시줄을 표시합니다. 생성된 정보 표시줄 인스턴스를 반환합니다.                                                                 |
| `showWarning`   | `string`: `text`, `int`: `duration` (1000), `string`: `moremsg` ("?") | `Item`   | **경고** 스타일의 정보 표시줄을 표시합니다. 생성된 정보 표시줄 인스턴스를 반환합니다.                                                                 |
| `showError`     | `string`: `text`, `int`: `duration` (1000), `string`: `moremsg` ("?") | `Item`   | **오류** 스타일의 정보 표시줄을 표시합니다. 생성된 정보 표시줄 인스턴스를 반환합니다.                                                                 |
| `showCustom`    | `Component`: `itemcomponent`, `int`: `duration` (1000)              | `Item`   | 사용자 정의 QML `Component`를 내용으로 하는 정보 표시줄을 표시합니다. 생성된 정보 표시줄 인스턴스를 반환합니다.                                              |
| `clearAllInfo`  | 없음                                                                | `bool`   | 현재 화면에 표시된 모든 정보 표시줄을 즉시 제거합니다. (현재 구현상 항상 `true`를 반환)                                                               |

*   `duration`: 정보 표시줄이 표시될 시간 (밀리초). `0` 또는 음수 값을 지정하면 자동으로 사라지지 않고 닫기 버튼이 표시됩니다.
*   `moremsg`: 주 메시지(`text`) 아래에 추가로 표시할 설명 텍스트.
*   `itemcomponent`: `showCustom` 메소드에서 사용할 사용자 정의 QML `Component`.
*   **반환값**: 각 `show...` 메소드는 생성된 정보 표시줄 아이템(`Item`)을 반환합니다. 이 아이템에는 `close()` 메소드가 있어 프로그래밍 방식으로 해당 정보 표시줄을 닫을 수 있습니다.

### 고유 시그널

`FluInfoBar` 자체에 고유한 시그널은 정의되어 있지 않습니다.

### 예제

```qml
// main.qml 또는 앱의 진입점
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ApplicationWindow {
    id: window
    width: 600
    height: 400
    visible: true
    title: "FluInfoBar 예제"

    FluInfoBar {
        id: infoBar
        root: Overlay.overlay // 중요: Overlay 사용
        layoutY: 50 // 표시 위치 조정 (기본값 75)
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 15

        FluButton {
            text: qsTr("정보 메시지 (2초)")
            onClicked: {
                infoBar.showInfo(qsTr("이것은 정보 메시지입니다."), 2000)
            }
        }

        FluButton {
            text: qsTr("경고 메시지 (수동 닫기)")
            property var warningInfo: null
            onClicked: {
                if (warningInfo) {
                    warningInfo.close()
                    warningInfo = null
                    text = qsTr("경고 메시지 (수동 닫기)")
                } else {
                    warningInfo = infoBar.showWarning(qsTr("주의가 필요합니다."), 0, qsTr("이 메시지는 직접 닫아야 합니다."))
                    text = qsTr("열린 경고 메시지 닫기")
                }
            }
        }

        FluButton {
            text: qsTr("사용자 정의 메시지")
            onClicked: {
                var customComponent = Qt.createComponent("MyCustomInfoBar.qml")
                if (customComponent.status === Component.Ready) {
                    infoBar.showCustom(customComponent, 3000) // 3초 후 사라짐
                } else {
                    console.error("사용자 정의 컴포넌트 로딩 실패:", customComponent.errorString())
                    infoBar.showError(qsTr("사용자 정의 메시지 로딩 실패"))
                }
            }
        }

        FluButton {
            text: qsTr("모든 메시지 지우기")
            onClicked: {
                infoBar.clearAllInfo()
            }
        }
    }
}

// MyCustomInfoBar.qml (예시 사용자 정의 컴포넌트)
/*
import QtQuick 2.15
import FluentUI 1.0
import QtQuick.Layouts 1.15

Rectangle {
    width: 300
    height: 60
    color: FluTheme.primaryColor
    radius: 4
    border.color: Qt.darker(color)

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        FluIcon { 
            iconSource: FluentIcons.FavoriteStarFill 
            iconColor: "white"
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
        }
        FluText { 
            text: qsTr("이것은 사용자 정의 정보 표시줄입니다!")
            color: "white"
            elide: Text.ElideRight
            Layout.fillWidth: true
        }
    }
}
*/
```

### 참고 사항

*   **인스턴스 및 `root` 설정**: `FluInfoBar`는 일반적으로 애플리케이션 전역에서 접근 가능한 단일 인스턴스로 사용됩니다. 인스턴스 생성 시 `root` 프로퍼티를 반드시 설정해야 하며, 보통 `Overlay.overlay`를 사용하여 다른 모든 UI 요소 위에 정보 표시줄이 표시되도록 합니다.
*   **자동 닫기 및 수동 닫기**: `duration`을 양수로 설정하면 해당 시간(ms) 후에 정보 표시줄이 자동으로 사라집니다. `0` 또는 음수로 설정하면 닫기 버튼이 표시되며 사용자가 직접 닫거나, `show...` 메소드가 반환한 `Item`의 `close()` 메소드를 호출하여 프로그래밍 방식으로 닫아야 합니다.
*   **메시지 스택**: 여러 정보 표시줄이 호출되면 지정된 `layoutY` 위치부터 시작하여 세로 방향으로 아래로 쌓입니다.
*   **중복 메시지 방지**: 동일한 타입(`type`)과 내용(`text`, `moremsg`)의 메시지가 바로 직전에 표시된 메시지와 동일한 경우, 새 메시지를 생성하는 대신 기존 메시지의 `duration`을 갱신하고 타이머를 재시작할 수 있습니다. (정확한 동작은 내부 구현 확인 필요)
*   **사용자 정의**: `showCustom` 메소드와 QML `Component`를 사용하여 정보 표시줄의 내용을 완전히 자유롭게 구성할 수 있습니다. 