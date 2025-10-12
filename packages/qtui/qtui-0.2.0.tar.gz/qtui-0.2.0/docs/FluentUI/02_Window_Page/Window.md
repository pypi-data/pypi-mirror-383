# Fluent UI 창 컴포넌트 (FluWindow)

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluWindow` 컴포넌트에 대해 설명합니다. `FluWindow`는 `QtQuick.Controls.Window`를 기반으로 확장되었으며, Fluent Design 스타일의 애플리케이션 창을 만들기 위한 다양한 기능과 편의성을 제공합니다.

## 공통 임포트 방법

Fluent UI 창 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15 // Window 기반이므로 필요할 수 있음
import FluentUI 1.0
```

---

## FluWindow

`FluWindow`는 Fluent UI 애플리케이션의 기본 최상위 창 역할을 합니다. 표준 `Window` 기능 외에도 사용자 정의 앱 바, 프레임리스 윈도우 스타일, 테마 연동, 다양한 창 실행 모드(Launch Modes), 내장 로딩 인디케이터 및 정보 표시줄, 그리고 `FluRouter`를 통한 강력한 창 관리 및 탐색 기능을 통합하여 제공합니다.

### 기반 클래스

`Window` (from `QtQuick.Controls`)

### 주요 기능

*   **프레임리스 모드**: 전역 설정(`FluApp.useSystemAppBar`)에 따라 시스템 기본 창 테두리 대신 사용자 정의 앱 바를 포함한 커스텀 창 디자인을 적용할 수 있습니다. (기본 활성화)
*   **사용자 정의 앱 바**: `appBar` 프로퍼티를 통해 기본 `FluAppBar` 대신 원하는 컴포넌트를 창 상단에 표시할 수 있습니다.
*   **테마 연동**: `FluTheme`의 다크/라이트 모드 및 강조 색상 설정을 자동으로 반영하며, 창 활성 상태에 따라 배경색(`backgroundColor`)이 변경됩니다. `FluAcrylic`을 이용한 배경 블러 효과도 지원합니다.
*   **라우터 통합**: `FluRouter`와 연동하여 창 간의 이동, 파라미터 전달, 결과 반환, 생명 주기 관리를 효율적으로 처리합니다.
*   **실행 모드 (Launch Modes)**: `FluRouter`로 창을 열 때, `launchMode` 설정(`Standard`, `SingleTask`, `SingleInstance`)에 따라 새 창을 생성할지, 기존 창을 활성화할지 등의 동작을 제어합니다.
*   **로딩 인디케이터**: `showLoading()` / `hideLoading()` 메소드로 간편하게 모달 로딩 팝업을 표시/숨김 처리합니다.
*   **정보 표시줄 (Info Bar)**: `showSuccess()`, `showInfo()` 등의 메소드로 창 내부에 상태 메시지를 쉽게 표시할 수 있습니다.
*   **생명 주기 관리**: `autoDestroy` 프로퍼티와 `closeListener` 콜백 함수를 통해 창이 닫힐 때의 동작(파괴 또는 숨김)을 제어할 수 있습니다.

### 고유/특징적 프로퍼티

| 이름                     | 타입                    | 기본값                        | 설명                                                                                                                                      |
| :----------------------- | :---------------------- | :---------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| `contentData`            | `default alias` (list<Item>) | `[]`                          | 창의 주 콘텐츠 영역입니다. `FluWindow { ... }` 내부에 배치된 아이템들이 이 곳에 위치합니다.                                                                  |
| `launchMode`             | `FluWindowType`         | `FluWindowType.Standard`      | `FluRouter`를 통해 창을 열 때의 동작 방식을 지정합니다. (`Standard`, `SingleTask`, `SingleInstance`)                                                         |
| `argument`               | `var`                   | `{}`                          | 라우터를 통해 창으로 전달된 파라미터 객체입니다.                                                                                                |
| `background`             | `Component`             | (내부 Item+Acrylic)          | 창 배경을 그리는 컴포넌트입니다. 기본값은 `FluAcrylic` 효과를 지원합니다.                                                                            |
| `fixSize`                | `bool`                  | `false`                       | `true` 설정 시 창 크기를 초기 크기로 고정합니다.                                                                                              |
| `loadingItem`            | `Component`             | (내부 Popup+ProgressRing)    | `showLoading()` 호출 시 표시될 로딩 팝업의 내용입니다.                                                                                        |
| `appBar`                 | `Item`                  | `FluAppBar` instance          | 창 상단에 표시될 앱 바 컴포넌트입니다.                                                                                                  |
| `fitsAppBarWindows`      | `bool`                  | `false`                       | `true`이고 시스템 앱 바 미사용 시, 앱 바 영역을 확보하지 않아 콘텐츠가 앱 바 영역까지 확장될 수 있습니다.                                                              |
| `backgroundColor`        | `readonly color`        | (계산됨)                     | `FluTheme`과 창 활성 상태에 따라 동적으로 계산되는 배경색입니다.                                                                                    |
| `stayTop`                | `bool`                  | `false`                       | 창을 항상 위에 표시할지 여부 (`Qt.WindowStaysOnTopHint`)                                                                                      |
| `showDark`, `showClose`, `showMinimize`, `showMaximize`, `showStayTop` | `bool` | `false`, `true`, `true`, `true`, `false` | 기본 `FluAppBar`의 해당 버튼 표시 여부입니다.                                                                                              |
| `autoMaximize`           | `bool`                  | `false`                       | `true`일 경우 창 표시 시 자동으로 최대화됩니다.                                                                                              |
| `autoVisible`            | `bool`                  | `true`                        | `true`일 경우 창 생성 후 자동으로 화면에 표시됩니다.                                                                                           |
| `autoCenter`             | `bool`                  | `true`                        | `true`이고 시스템 앱 바 미사용 시, 창 생성 후 화면 중앙으로 이동합니다.                                                                                 |
| `autoDestroy`            | `bool`                  | `true`                        | `true`일 경우 창이 닫힐 때 객체가 파괴됩니다. `false`이면 숨겨집니다 (`FluRouter` 관리 하).                                                               |
| `useSystemAppBar`        | `bool`                  | `FluApp.useSystemAppBar`      | 시스템 기본 창 테두리 사용 여부입니다. `true`이면 `appBar`, 프레임리스 기능이 비활성화됩니다.                                                               |
| `resizeBorderColor`      | `color`                 | (계산됨)                     | 시스템 앱 바 미사용 및 최대화 아닐 때 표시되는 리사이즈 테두리 색상입니다.                                                                              |
| `resizeBorderWidth`      | `int`                   | `1`                           | 리사이즈 테두리 두께입니다.                                                                                                                  |
| `closeListener`          | `function(event)`       | (내부 함수)                   | 창이 닫히려 할 때 호출됩니다. `event.accepted = false`로 닫기 동작을 취소할 수 있습니다. 기본 동작은 `autoDestroy` 값에 따라 창을 파괴하거나 숨깁니다.                               |
| `windowIcon`             | `string`                | `FluApp.windowIcon`           | 창 아이콘 경로입니다.                                                                                                                   |

### 고유 메소드

*   `showLoading(text: string = qsTr("Loading..."), cancel: bool = true)`: 모달 로딩 팝업을 표시합니다.
*   `hideLoading()`: 로딩 팝업을 숨깁니다.
*   `showSuccess(text: string, duration: int = 2000, moremsg: string = "")`: 성공 메시지를 정보 표시줄에 표시합니다. (`showInfo`, `showWarning`, `showError`도 유사하게 사용 가능)
*   `clearAllInfo()`: 정보 표시줄의 모든 메시지를 제거합니다.
*   `moveWindowToDesktopCenter()`: 창을 화면 중앙으로 이동시킵니다.
*   `fixWindowSize()`: `fixSize` 프로퍼티에 따라 창 크기 제한을 수동으로 적용합니다.
*   `setResult(data: var)`: 이 창을 연 다른 창으로 결과 데이터를 설정합니다 (`FluWindowResultLauncher`와 함께 사용).
*   `showMaximized()`, `showMinimized()`, `showNormal()`: 창 상태를 프로그래밍 방식으로 변경합니다.
*   `setHitTestVisible(val: Item)`: 프레임리스 모드에서 마우스 상호작용(드래그 등)을 허용할 영역을 지정합니다 (주로 앱 바 내부 영역 설정에 사용).
*   `deleteLater()`: 창 객체를 안전하게 삭제 예약합니다.
*   `containerItem()`: 앱 바, 콘텐츠 영역 등을 포함하는 내부 컨테이너 `Item`을 반환합니다.

### 고유 시그널

*   `initArgument(argument: var)`: 창 컴포넌트 생성 완료 시점에 전달받은 `argument`와 함께 발생합니다.
*   `lazyLoad()`: 창이 처음으로 화면에 보여질 때 발생합니다. 지연 로딩 구현에 유용합니다.

### 예제

**1. 기본 FluWindow 정의:**

```qml
import QtQuick 2.15
import FluentUI 1.0

FluWindow {
    title: "My Fluent Window"
    width: 800
    height: 600
    
    FluText {
        anchors.centerIn: parent
        text: "Hello, Fluent UI!"
        font: FluTextStyle.Title
    }
}
```

**2. Launch Mode 및 라우터 사용 (T_MultiWindow.qml 참조):**

```qml
// StandardWindow.qml (새 창을 항상 생성)
FluWindow {
    launchMode: FluWindowType.Standard
    // ... content ...
}

// SingleTaskWindow.qml (기존 창이 있으면 활성화)
FluWindow {
    launchMode: FluWindowType.SingleTask
    // ... content ...
}

// SingleInstanceWindow.qml (기존 창 파괴 후 새 창 생성)
FluWindow {
    launchMode: FluWindowType.SingleInstance
    // ... content ...
}

// --- 다른 QML 파일에서 창 열기 ---
FluButton {
    text: "Open Standard Window"
    onClicked: FluRouter.navigate("/standardWindow")
}

FluButton {
    text: "Open SingleTask Window"
    onClicked: FluRouter.navigate("/singleTaskWindow")
}
```

**3. 파라미터 전달 및 결과 받기 (T_MultiWindow.qml 참조):**

```qml
// --- 창을 여는 쪽 (T_MultiWindow.qml) ---
FluWindowResultLauncher {
    id: loginLauncher
    path: "/login"
    onResult: (data) => {
        console.log("Login result:", data.password)
    }
}

FluButton {
    text: "Login"
    onClicked: loginLauncher.launch({ username: "guest" }) // 파라미터 전달
}

// --- 열리는 창 (예: LoginWindow.qml) ---
FluWindow {
    id: loginWindow
    // ... 로그인 UI ...

    // 초기 파라미터 받기
    onInitArgument: (arg) => {
        usernameInput.text = arg.username || ""
    }

    FluButton { // 로그인 버튼
        onClicked: {
            // 로그인 처리 후 결과 설정 및 창 닫기
            var resultData = { password: passwordInput.text }
            loginWindow.setResult(resultData)
            loginWindow.close()
        }
    }
}
```

**4. 로딩 및 정보 표시줄 사용:**

```qml
FluWindow {
    id: dataWindow
    // ...
    function loadData(){
        dataWindow.showLoading("데이터 로딩 중...")
        // 비동기 데이터 로딩 로직...
        // 로딩 완료 후
        dataWindow.hideLoading()
        dataWindow.showSuccess("데이터 로딩 완료!")
        // 에러 발생 시
        // dataWindow.showError("데이터 로딩 실패", 5000)
    }
}
```

### 관련 컴포넌트/객체

*   **`FluRouter`**: 창 탐색 및 관리를 위한 핵심 객체입니다.
*   **`FluAppBar`**: `FluWindow`의 기본 앱 바 컴포넌트입니다.
*   **`FluFrameless`**: 프레임리스 윈도우 동작을 처리하는 내부 헬퍼입니다.
*   **`FluTheme`**: 창의 색상 등 시각적 테마를 제공합니다.
*   **`FluApp`**: 시스템 앱 바 사용 여부 등 전역 애플리케이션 설정을 제공합니다.
*   **`FluWindowType`**: `launchMode`에 사용되는 열거형 (`Standard`, `SingleTask`, `SingleInstance`)을 정의합니다.
*   **`FluWindowResultLauncher`**: 다른 창을 열고 그 창으로부터 결과를 받아 처리하는 데 사용되는 컴포넌트입니다.

### 참고 사항

*   `FluWindow`는 `FluRouter`와 함께 사용할 때 가장 효과적입니다. `FluRouter`는 `launchMode`, 파라미터 전달, 창 생명 주기 관리를 처리합니다.
*   프레임리스 모드(`useSystemAppBar: false`)가 기본이며, 이 모드에서는 앱 바 내에서 창 이동 및 크기 조정을 위한 마우스 상호작용 영역을 `setHitTestVisible()`를 통해 적절히 설정하는 것이 중요합니다.
*   `autoDestroy`와 `closeListener`를 사용하여 창을 닫을 때의 동작(객체 파괴 또는 숨김)을 제어할 수 있습니다. 