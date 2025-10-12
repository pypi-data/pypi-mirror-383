# Fluent UI 이벤트 버스 시스템 (FluEventBus & FluEvent)

이 문서에서는 `FluentUI` 모듈에서 제공하는 이벤트 버스 시스템에 대해 설명합니다. 이 시스템은 QML 컴포넌트 간의 분리된(decoupled) 통신을 위한 매커니즘을 제공하며, `FluEventBus` 싱글톤과 `FluEvent` 컴포넌트로 구성됩니다.

## 개요

애플리케이션이 복잡해지면 서로 다른 부분에 위치한 컴포넌트들이 직접적인 참조 없이 상호작용해야 하는 경우가 많습니다. 예를 들어, 백그라운드 작업이 완료되었을 때 여러 UI 컴포넌트에게 알리거나, 설정 변경 사항을 애플리케이션 전역에 전파하는 경우입니다. 이벤트 버스 시스템은 이러한 시나리오를 해결하기 위해 설계되었습니다.

*   **`FluEventBus`**: 애플리케이션 전역에서 단 하나만 존재하는 싱글톤 객체입니다. 모든 이벤트의 등록과 전달을 관리하는 중앙 허브 역할을 합니다.
*   **`FluEvent`**: 특정 이름의 이벤트를 수신(listen)하기 위한 비시각적 `QtObject`입니다. QML 컴포넌트 내부에 선언되어 특정 이벤트가 발생했을 때 특정 동작(시그널 핸들러 실행)을 수행하도록 합니다.

이 시스템을 사용하면 이벤트를 발송하는 컴포넌트(Publisher)와 이벤트를 수신하는 컴포넌트(Subscriber)가 서로를 직접 알 필요가 없어 컴포넌트 간의 의존성을 낮추고 코드의 유연성과 유지보수성을 향상시킬 수 있습니다.

## 공통 임포트 방법

이벤트 버스 시스템을 사용하기 위해 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import FluentUI 1.0
```

---

## FluEventBus (싱글톤)

`FluEventBus`는 애플리케이션의 모든 이벤트 흐름을 관리하는 중심점입니다. 싱글톤이기 때문에 애플리케이션 어디서든 동일한 인스턴스에 접근할 수 있습니다.

### 접근 방법

QML 코드 내에서 `FluEventBus`의 메소드를 호출하려면 싱글톤 객체 이름인 `FluEventBus`를 직접 사용하면 됩니다.

```qml
FluEventBus.post("myCustomEvent", { message: "Hello from Publisher!" })
```

### 고유 메소드

| 이름         | 파라미터                          | 반환타입 | 설명                                                                                                                                                                                             |
| :----------- | :-------------------------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `register`   | `event: FluEvent`                 | `void`   | (주로 내부용) `FluEvent` 컴포넌트가 생성될 때 이 메소드를 호출하여 자신을 이벤트 버스에 등록합니다. 개발자가 직접 이 메소드를 호출할 필요는 거의 없습니다.                                                            |
| `unregister` | `event: FluEvent`                 | `void`   | (주로 내부용) `FluEvent` 컴포넌트가 소멸될 때 이 메소드를 호출하여 자신을 이벤트 버스에서 등록 해제합니다. 개발자가 직접 이 메소드를 호출할 필요는 거의 없습니다.                                                            |
| `post`       | `name: string`, `data: var = {}`  | `void`   | 지정된 `name`의 이벤트를 시스템 전체에 발송(publish)합니다. 선택적으로 `data` 파라미터(JavaScript 객체)를 통해 이벤트 관련 데이터를 전달할 수 있습니다. 이 메소드가 호출되면, 버스는 등록된 `FluEvent` 중 동일한 `name`을 가진 모든 인스턴스를 찾아 해당 인스턴스의 `triggered` 시그널을 발생시킵니다. |

### 고유 프로퍼티 / 시그널

`FluEventBus`에는 개발자가 직접 상호작용하는 고유 프로퍼티나 시그널은 없습니다.

---

## FluEvent

`FluEvent`는 특정 이벤트를 구독(subscribe)하고 해당 이벤트가 발생했을 때 반응하기 위한 컴포넌트입니다. 비시각적(`QtObject` 기반)이므로 UI 레이아웃에 영향을 주지 않습니다.

### 기반 클래스

`QtObject` (from `QtQuick`)

### 고유 프로퍼티

| 이름   | 타입     | 기본값 | 설명                                                                     |
| :----- | :------- | :----- | :----------------------------------------------------------------------- |
| `name` | `string` | `""`   | 이 `FluEvent` 인스턴스가 수신하고자 하는 이벤트의 고유한 이름입니다. `FluEventBus.post()` 호출 시 사용된 `name`과 일치해야 이벤트가 수신됩니다. |

### 고유 시그널

| 이름        | 파라미터     | 반환타입 | 설명                                                                                                                               |
| :---------- | :----------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `triggered` | `data: var`  | -        | `FluEventBus.post()`를 통해 이 `FluEvent`의 `name`과 일치하는 이벤트가 발송되었을 때 발생하는 시그널입니다. `data` 파라미터는 `post()` 호출 시 전달된 데이터 객체입니다. | `data`가 전달되지 않았다면 빈 JavaScript 객체(`{}`)가 됩니다. |

### 생명주기 관리

`FluEvent` 컴포넌트는 생성될 때(`Component.onCompleted`) 자동으로 `FluEventBus.register(this)`를 호출하여 자신을 버스에 등록하고, 소멸될 때(`Component.onDestruction`) 자동으로 `FluEventBus.unregister(this)`를 호출하여 등록을 해제합니다. 따라서 개발자는 등록 및 해제 로직을 직접 관리할 필요가 없습니다.

---

## 예제

다음은 `T_Settings.qml`에서 이벤트 버스를 활용하는 예제입니다.

**1. 이벤트 수신 (`FluEvent` 사용)**

설정 페이지(`T_Settings.qml`)에는 '업데이트 확인' 작업이 완료되었음을 알리는 이벤트를 수신하는 `FluEvent`가 있습니다.

```qml
// T_Settings.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

FluScrollablePage {
    // ... 다른 UI 요소들 ...

    // "checkUpdateFinish" 이벤트를 수신하기 위한 FluEvent 인스턴스
    FluEvent {
        name: "checkUpdateFinish"
        // 이벤트가 발생했을 때 실행될 핸들러
        onTriggered: (data) => {
            // 로딩 상태인 버튼의 로딩 상태를 해제
            btn_checkupdate.loading = false
            // data 파라미터를 통해 추가 정보 수신 가능 (예: data.success, data.message)
            console.log("Update check finished:", JSON.stringify(data))
        }
    }

    FluLoadingButton {
        id: btn_checkupdate
        text: qsTr("Check for Updates")
        onClicked: {
            loading = true // 버튼 로딩 상태 시작
            // "checkUpdate" 이벤트를 발송하여 업데이트 확인 로직 실행 요청
            FluEventBus.post("checkUpdate") 
        }
    }
    
    // ...
}
```

*   `FluEvent`는 `name` 프로퍼티를 `"checkUpdateFinish"`로 설정하여 해당 이름의 이벤트를 기다립니다.
*   `onTriggered` 핸들러는 이 이벤트가 발생하면 연결된 로직(여기서는 `btn_checkupdate` 버튼의 `loading` 상태를 `false`로 변경)을 실행합니다.
*   `data` 파라미터를 통해 이벤트 발송 시 함께 전달된 추가 정보를 받을 수 있습니다.

**2. 이벤트 발송 (`FluEventBus.post` 사용)**

*   **업데이트 확인 요청**: 사용자가 `btn_checkupdate` 버튼을 클릭하면, `onClicked` 핸들러 내에서 `FluEventBus.post("checkUpdate")`가 호출됩니다. 이는 애플리케이션의 다른 부분(예: `MainWindow.qml` 또는 백그라운드 로직)에 있는 `FluEvent { name: "checkUpdate" }` 리스너에게 업데이트 확인 작업을 시작하라는 신호를 보냅니다.

*   **업데이트 확인 완료 알림**: 업데이트 확인 작업이 (성공적으로든 실패로든) 완료되면, 해당 작업을 수행한 컴포넌트는 다음과 같이 `"checkUpdateFinish"` 이벤트를 발송하여 결과를 알립니다.

    ```qml
    // 업데이트 확인 로직이 있는 다른 컴포넌트 (예: MainWindow.qml 또는 Python 코드)
    function performUpdateCheck() {
        // ... 실제 업데이트 확인 로직 수행 ...
        var resultData = { success: true, message: "Update check complete." };
        // 작업 완료 후 "checkUpdateFinish" 이벤트를 발송하여 T_Settings.qml에 알림
        FluEventBus.post("checkUpdateFinish", resultData)
    }
    ```
    이렇게 `post()`를 호출하면 `T_Settings.qml`의 `FluEvent { name: "checkUpdateFinish" }`가 `triggered` 시그널을 발생시키고, `resultData` 객체가 `data` 파라미터로 전달됩니다.

---

## 참고 사항

*   **디커플링 (Decoupling)**: 이벤트 버스 시스템의 가장 큰 장점은 컴포넌트 간의 결합도를 낮추는 것입니다. 이벤트를 보내는 쪽과 받는 쪽은 서로의 존재나 구현 세부사항을 알 필요가 없습니다. 오직 약속된 이벤트 이름(`name`)만 공유하면 됩니다.
*   **자동 생명주기 관리**: `FluEvent` 컴포넌트는 생성 및 소멸 시 자동으로 이벤트 버스에 등록/해제되므로, 메모리 누수나 불필요한 리스너가 남는 문제를 걱정할 필요가 적습니다.
*   **데이터 전달**: `post()` 메소드의 두 번째 인자를 사용하여 이벤트와 함께 임의의 데이터를 JavaScript 객체 형태로 전달할 수 있습니다. 이는 이벤트 발생 시점의 상태나 결과를 수신 측에 알리는 데 유용합니다.
*   **싱글톤**: `FluEventBus`는 애플리케이션 전역에서 유일한 인스턴스임을 기억해야 합니다. 이는 모든 이벤트가 단일 채널을 통해 관리된다는 의미입니다.
*   **사용 사례**: 이 시스템은 다음과 같은 다양한 시나리오에 유용합니다.
    *   네트워크 요청, 파일 처리 등 비동기 작업의 완료 또는 진행 상태 알림.
    *   애플리케이션 설정 변경(예: 테마, 언어) 전파.
    *   모델 데이터 변경 시 여러 뷰(View) 동기화.
    *   UI 레이아웃 상 멀리 떨어져 있어 직접 참조하기 어려운 컴포넌트 간의 상호작용. 