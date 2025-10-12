# Fluent UI 창 결과 실행기 (FluWindowResultLauncher)

이 문서에서는 `FluentUI` 모듈의 `FluWindowResultLauncher` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 다른 `FluWindow`를 열고 그 창으로부터 결과 데이터를 비동기적으로 받아 처리하는 기능을 제공합니다.

## 공통 임포트 방법

`FluWindowResultLauncher` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluWindowResultLauncher

`FluWindowResultLauncher`는 UI를 가지지 않는 비-시각적 컴포넌트로, 특정 라우트 경로(`path`)의 `FluWindow`를 열고 해당 창이 작업을 완료한 후 반환하는 결과 데이터를 수신하는 데 사용됩니다. 예를 들어, 사용자 로그인을 처리하는 별도의 창을 열고 로그인 성공 시 사용자 정보나 토큰을 반환받거나, 파일 선택 창을 열고 선택된 파일 경로를 반환받는 등의 시나리오에 유용합니다.

작동 방식은 다음과 같습니다:
1.  `FluWindowResultLauncher` 인스턴스를 생성하고, 열고자 하는 대상 창의 라우트 경로를 `path` 프로퍼티에 설정합니다.
2.  `launch()` 메소드를 호출하여 대상 창을 엽니다. 필요시 `argument`를 통해 초기 데이터를 전달할 수 있습니다.
3.  열린 대상 `FluWindow`에서는 사용자의 작업(예: 로그인, 설정 변경, 파일 선택)을 처리합니다.
4.  대상 `FluWindow`는 작업 완료 후 반환할 결과 데이터를 준비하여 자신의 `setResult(data)` 메소드를 호출합니다.
5.  `setResult()`가 호출되면, `FluWindowResultLauncher`의 `result` 시그널이 해당 결과 데이터(`data`)와 함께 발생합니다.
6.  `FluWindowResultLauncher`가 있는 원래의 QML 코드에서는 `onResult` 핸들러를 구현하여 반환된 데이터를 처리합니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름     | 타입            | 기본값      | 설명                                                                           |
| :------- | :-------------- | :---------- | :----------------------------------------------------------------------------- |
| `path`   | `var` (string)  | `undefined` | `FluRouter.navigate()`를 통해 열고자 하는 대상 `FluWindow`의 라우트 경로 문자열입니다. **필수적으로 지정해야 합니다.** |
| `_from`  | `readonly var` (Window) | (자동 할당) | 이 `FluWindowResultLauncher` 컴포넌트를 포함하고 있는 부모 `FluWindow`에 대한 참조입니다. (내부용) |
| `_to`    | `readonly var` (FluWindow)| `undefined` | `launch()` 메소드를 통해 열린 대상 `FluWindow` 인스턴스에 대한 참조입니다. (내부용)                  |

### 고유 메소드

| 이름       | 파라미터                   | 반환타입 | 설명                                                                                                                                                                      |
| :--------- | :------------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `launch`   | `argument: var = {}`       | `void`   | `path` 프로퍼티에 지정된 라우트 경로의 `FluWindow`를 엽니다. 선택적으로 `argument` 객체를 통해 초기 데이터를 대상 창으로 전달할 수 있습니다. 내부적으로 `FluRouter.navigate()`를 호출합니다. |
| `setResult`| `data: var = {}`           | `void`   | **주의:** 이 메소드는 `FluWindowResultLauncher` 자체에서 호출하는 것이 아니라, **`launch()`를 통해 열린 대상 `FluWindow` 내에서 호출**하여 결과를 반환하는 데 사용됩니다. 이 메소드가 호출되면 `FluWindowResultLauncher`의 `result` 시그널이 발생합니다. |

### 고유 시그널

| 이름     | 파라미터        | 반환타입 | 설명                                                                                             | 
| :------- | :-------------- | :------- | :----------------------------------------------------------------------------------------------- |
| `result` | `data: var`     | -        | `launch()`를 통해 열린 대상 `FluWindow`에서 `setResult()` 메소드가 호출되었을 때 발생합니다. 파라미터 `data`는 `setResult()`에 전달된 결과 객체입니다. | 

### 예제

다음은 로그인 창을 열고 사용자 이름(`username`)을 전달한 뒤, 로그인 창에서 입력된 비밀번호(`password`)를 결과로 받아오는 예시입니다. (`T_MultiWindow.qml` 및 관련 창 파일 참조)

**1. 결과를 받을 창 (예: MainWindow.qml):**

```qml
import QtQuick 2.15
import FluentUI 1.0

FluWindow {
    property string returnedPassword: ""
    
    // 로그인 창을 열고 결과를 받을 Launcher 정의
    FluWindowResultLauncher {
        id: loginLauncher
        path: "/login" // 열 창의 라우트 경로
        
        // 결과 수신 시그널 핸들러
        onResult: (data) => {
            console.log("Login window returned:", JSON.stringify(data))
            returnedPassword = data.password || ""
            // 여기서 받은 비밀번호로 추가 작업 수행...
        }
    }
    
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10
        
        FluButton {
            text: "Login"
            onClicked: {
                // 로그인 창 열기 (초기 사용자 이름 전달)
                loginLauncher.launch({ username: "initial_user" })
            }
        }
        
        FluText {
            text: "Returned Password: " + returnedPassword
        }
    }
}
```

**2. 결과를 반환할 창 (예: LoginWindow.qml):**

```qml
import QtQuick 2.15
import FluentUI 1.0

FluWindow {
    id: loginWindow
    title: "Login"
    width: 300
    height: 200
    
    property string currentUsername: ""
    
    // 초기 파라미터 받기
    onInitArgument: (arg) => {
        currentUsername = arg.username || ""
        usernameInput.text = currentUsername
    }
    
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10
        
        FluTextBox {
            id: usernameInput
            placeholderText: "Username"
        }
        FluTextBox {
            id: passwordInput
            placeholderText: "Password"
            echoMode: TextInput.Password
        }
        
        FluButton {
            text: "OK"
            Layout.alignment: Qt.AlignRight
            onClicked: {
                // 결과 데이터 설정
                var resultData = { 
                    username: usernameInput.text, 
                    password: passwordInput.text 
                }
                loginWindow.setResult(resultData) // 결과를 설정하고
                loginWindow.close() // 창을 닫음 (결과 시그널 발생)
            }
        }
    }
}
```

### 관련 컴포넌트/객체

*   **`FluRouter`**: `FluWindowResultLauncher`는 내부적으로 `FluRouter.navigate()`를 호출하여 창을 엽니다.
*   **`FluWindow`**: 결과를 반환하기 위해 열리는 대상 창이며, `setResult()` 메소드를 포함합니다.

### 참고 사항

*   `FluWindowResultLauncher`는 화면에 표시되지 않는 비-시각적 컴포넌트입니다.
*   결과를 성공적으로 받으려면, `launch()`로 열리는 대상 `FluWindow` 내부에 `setResult(data)`를 호출하고 창을 닫는 로직이 반드시 포함되어야 합니다.
*   `launch()` 메소드는 비동기적으로 창을 엽니다. `onResult` 시그널은 사용자가 대상 창에서 작업을 완료하고 `setResult()`를 호출한 후에야 발생합니다. 