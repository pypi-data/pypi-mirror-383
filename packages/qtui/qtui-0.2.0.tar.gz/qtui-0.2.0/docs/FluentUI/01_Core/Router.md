# Fluent UI 라우터 (FluRouter)

이 문서에서는 `FluentUI` 모듈의 `FluRouter` 전역 싱글톤 객체에 대해 설명합니다. `FluRouter`는 `FluWindow` 기반의 다중 창 애플리케이션에서 창 간의 탐색, 파라미터 전달, 창 실행 모드(`launchMode`) 제어 및 창 생명 주기 관리를 위한 핵심 기능을 제공합니다.

## `FluRouter` 접근 방법

`FluRouter`는 QML 환경에 전역 싱글톤으로 등록되어 있으므로, 어떤 QML 파일에서든 별도의 import 없이 `FluRouter` 식별자를 사용하여 직접 접근할 수 있습니다.

```qml
import FluentUI 1.0

FluButton {
    text: "Open Settings"
    onClicked: {
        // "/settings" 경로로 등록된 FluWindow 열기
        FluRouter.navigate("/settings") 
    }
}

FluButton {
    text: "Open User Profile"
    onClicked: {
        // "/profile" 경로로 파라미터와 함께 창 열기
        FluRouter.navigate("/profile", { userId: 123, mode: "edit" })
    }
}
```

Python 코드에서 직접 `FluRouter`를 조작하는 것은 일반적이지 않으며, 주로 QML을 통해 상호작용합니다.

---

## FluRouter

`FluRouter`는 애플리케이션 내에서 정의된 문자열 경로(route)를 기반으로 해당 경로에 매핑된 `FluWindow` 컴포넌트를 찾아 화면에 표시하는 역할을 합니다. 개발자는 애플리케이션 초기화 시점에 `routes` 프로퍼티에 각 경로와 QML 파일 URL의 매핑 정보를 설정해야 합니다. `navigate()` 메소드를 호출하면, `FluRouter`는 요청된 경로와 대상 `FluWindow`의 `launchMode` 설정을 고려하여 새 창을 생성하거나 기존 창을 재사용(활성화 또는 재 생성)합니다.

### 기반 클래스

`QtObject` (싱글톤)

### 주요 프로퍼티

| 이름    | 타입         | 기본값 | 설명                                                                                                                                  |
| :------ | :----------- | :----- | :------------------------------------------------------------------------------------------------------------------------------------ |
| `routes`| `var` (object) | `{}`   | 라우트 경로(문자열 키)와 해당 경로에 대응하는 QML 파일 URL(문자열 값)을 매핑하는 자바스크립트 객체입니다. **애플리케이션 시작 시점에 반드시 설정해야 합니다.** | 
| `windows`| `readonly var` (array)| `[]`   | 현재 `FluRouter`가 관리하고 있는 활성 `FluWindow` 인스턴스들의 배열입니다. (주로 내부 관리용이며 직접 조작하는 것은 권장되지 않습니다.)                               |

**`routes` 설정 예시 (main.qml 또는 Python 초기화):**

```qml
// main.qml 등 애플리케이션 진입점에서
import FluentUI 1.0

FluApp {
    // ...
    Component.onCompleted: {
        FluRouter.routes = {
            "/home": "qrc:/qml/HomePage.qml",       // 메인 페이지 (FluPage 상속 가정)
            "/settings": "qrc:/qml/SettingsWindow.qml", // 설정 창 (FluWindow 상속)
            "/login": "qrc:/qml/LoginWindow.qml",       // 로그인 창 (FluWindow 상속)
            "/profile": "qrc:/qml/UserProfileWindow.qml" // 사용자 프로필 창 (FluWindow 상속)
        }
    }
}
```

### 주요 메소드

| 이름        | 파라미터                                                        | 반환타입 | 설명                                                                                                                                                                                                                                                                                                                        |
| :---------- | :-------------------------------------------------------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `navigate`  | `route: string`, `argument: var = {}`, `windowRegister: var = undefined` | `void`   | 지정된 `route`에 해당하는 창으로 이동합니다.                                                                                                                                                                                                                                                                   |
|             | `route`: `routes` 객체에 정의된 경로 문자열.                        |          |                                                                                                                                                                                                                                                                                                                 |
|             | `argument`: 대상 창으로 전달할 데이터 객체 (선택 사항).               |          | 대상 창의 `argument` 프로퍼티 및 `initArgument` 시그널로 전달됩니다.                                                                                                                                                                                                                                                   |
|             | `windowRegister`: `FluWindowResultLauncher` 인스턴스 (선택 사항).     |          | 이 값을 전달하면, 열린 창에서 `setResult()` 호출 시 `windowRegister`의 `result` 시그널이 발생합니다.                                                                                                                                                                                                            |
| `addWindow` | `window: FluWindow`                                             | `void`   | (주로 내부용) `FluWindow` 인스턴스를 관리 목록에 추가합니다. `FluWindow` 생성 시 자동으로 호출됩니다.                                                                                                                                                                                                        |
| `removeWindow`| `window: FluWindow`                                             | `void`   | (주로 내부용) 관리 목록에서 `FluWindow` 인스턴스를 제거하고 삭제합니다. `FluWindow` 소멸 시 자동으로 호출됩니다.                                                                                                                                                                                               |
| `exit`      | `retCode: int = 0`                                              | `void`   | `FluRouter`가 관리하는 모든 창을 닫고 `Qt.exit(retCode)`를 호출하여 애플리케이션을 종료합니다.                                                                                                                                                                                                              |

**`navigate()` 동작 방식 (`launchMode` 기준):**

`navigate()` 메소드의 정확한 동작은 대상 `FluWindow` 컴포넌트의 `launchMode` 프로퍼티 값에 따라 결정됩니다.

*   **`FluWindowType.Standard` (기본값):** 호출될 때마다 항상 지정된 `route`의 새 `FluWindow` 인스턴스를 생성합니다.
*   **`FluWindowType.SingleTask`:** 지정된 `route`에 해당하는 `FluWindow` 인스턴스가 이미 존재하면, 새 인스턴스를 생성하지 않고 기존 인스턴스를 활성화(화면 맨 앞으로 가져오고 포커스 요청)하고 `argument`를 업데이트합니다. 존재하지 않으면 새 인스턴스를 생성합니다.
*   **`FluWindowType.SingleInstance`:** 지정된 `route`에 해당하는 `FluWindow` 인스턴스가 이미 존재하면, 기존 인스턴스를 먼저 닫고(파괴) 새로운 인스턴스를 생성합니다. 존재하지 않으면 새 인스턴스를 생성합니다.

### 고유 시그널

`FluRouter` 자체에는 공개적인 시그널이 없습니다. 창 탐색 결과나 상태 변경은 각 `FluWindow`의 시그널(예: `initArgument`, `lazyLoad`) 또는 `FluWindowResultLauncher`의 `result` 시그널을 통해 처리합니다.

### 예제

(예제 코드는 `FluWindow.md` 문서의 예제 섹션과 `T_MultiWindow.qml` 파일을 참조하십시오. `navigate` 호출, 파라미터 전달(`launch`), 결과 수신(`onResult`) 방법이 포함되어 있습니다.)

### 관련 컴포넌트/객체

*   **`FluWindow`**: `FluRouter`가 관리하고 탐색하는 대상 창 컴포넌트입니다.
*   **`FluWindowType`**: `FluWindow`의 `launchMode` 프로퍼티에 사용될 열거형(`Standard`, `SingleTask`, `SingleInstance`)을 제공합니다.
*   **`FluWindowResultLauncher`**: 다른 `FluWindow`를 열고 그 창으로부터 결과 데이터를 받아 처리하기 위한 보조 컴포넌트입니다.
*   **`FluApp`**: 애플리케이션 전역 설정(`routes` 설정 포함)을 관리하며, `FluRouter` 초기화에 사용될 수 있습니다.

### 참고 사항

*   `FluRouter`는 싱글톤 객체이므로 애플리케이션 전체에서 단 하나의 인스턴스만 존재하며, QML 코드 어디서든 `FluRouter` 식별자로 접근 가능합니다.
*   `FluRouter`를 사용하기 전에, 애플리케이션 초기화 과정에서 `FluRouter.routes` 프로퍼티에 모든 라우트 경로와 해당 QML 파일 URL 매핑을 반드시 설정해야 합니다.
*   `navigate()` 메소드의 동작은 대상 창으로 지정된 QML 파일 내 `FluWindow` 컴포넌트의 `launchMode` 프로퍼티 설정에 크게 의존합니다. 