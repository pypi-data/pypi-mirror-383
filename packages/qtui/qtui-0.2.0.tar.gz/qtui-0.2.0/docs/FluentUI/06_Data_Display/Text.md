# Fluent UI 텍스트 및 입력 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 텍스트 표시 및 입력 관련 컴포넌트들을 설명합니다. 각 컴포넌트는 기본적인 Qt Quick 컨트롤 (`Text`, `TextEdit`, `TextField`, `TextArea`)을 기반으로 확장되었습니다.

## 공통 임포트 방법

Fluent UI 텍스트 관련 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가하는 것이 일반적입니다.

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15 // TextField, TextArea 등 기본 컨트롤 사용 시
import FluentUI 1.0
```

---

## 텍스트 표시 컴포넌트

### 1. FluText

가장 기본적인 텍스트 표시 컴포넌트입니다. `QtQuick.Controls.Text`를 기반으로 하며, Fluent UI 테마에 맞는 기본 스타일(색상, 렌더링 타입, 폰트)을 제공합니다.

#### 고유/특징적 프로퍼티

| 이름        | 타입   | 기본값                  | 설명                                           |
| :---------- | :----- | :---------------------- | :--------------------------------------------- |
| `textColor` | `color`  | `FluTheme.fontPrimaryColor` | 텍스트 색상.                                     |
| `color`     | `color`  | `textColor`             | `textColor`와 동일하게 연결됩니다. (상속됨)        |
| `renderType`| `enum`   | `FluTheme.nativeText` 기반 | 텍스트 렌더링 방식 (`Text.NativeRendering` 또는 `Text.QtRendering`). |
| `font`      | `font`   | `FluTextStyle.Body`     | 텍스트 글꼴. (상속됨)                          |

*(이 외 `QtQuick.Controls.Text`의 프로퍼티, 메소드, 시그널 상속. 예: `text`, `wrapMode`, `elide` 등)*

#### 예제

```qml
FluText {
    text: qsTr("기본 텍스트입니다.")
    font.pixelSize: 14
}
```

#### 참고 사항

*   단순히 Fluent UI 테마에 맞는 스타일로 텍스트를 표시할 때 사용합니다.
*   `textColor` 프로퍼티를 통해 테마 색상과 다른 색을 지정할 수 있습니다.

### 2. FluCopyableText

사용자가 내용을 복사할 수 있는 읽기 전용 텍스트 컴포넌트입니다. `QtQuick.Controls.TextEdit`를 기반으로 합니다.

#### 고유/특징적 프로퍼티

| 이름                | 타입   | 기본값                          | 설명                                                        |
| :------------------ | :----- | :------------------------------ | :---------------------------------------------------------- |
| `textColor`         | `color`  | `FluTheme.dark` 기반 자동 계산  | 텍스트 색상.                                                |
| `color`             | `color`  | `textColor`                     | `textColor`와 동일하게 연결됩니다. (상속됨)                 |
| `readOnly`          | `bool`   | `true`                          | 읽기 전용 여부. 항상 `true`입니다. (상속됨)                  |
| `selectByMouse`     | `bool`   | `true`                          | 마우스로 텍스트 선택 가능 여부. 항상 `true`입니다. (상속됨) |
| `selectionColor`    | `color`  | `FluTheme.primaryColor` (반투명) | 텍스트 선택 시 배경 색상. (상속됨)                          |
| `selectedTextColor` | `color`  | `color` (현재 텍스트 색상)        | 텍스트 선택 시 글자 색상. (상속됨)                          |
| `font`              | `font`   | `FluTextStyle.Body`             | 텍스트 글꼴. (상속됨)                                       |
| `renderType`        | `enum`   | `FluTheme.nativeText` 기반      | 텍스트 렌더링 방식.                                         |

*(이 외 `QtQuick.Controls.TextEdit`의 프로퍼티 (예: `text`), 메소드 (`copy`, `selectAll`), 시그널 (`selectedTextChanged`) 상속)*

#### 예제

```qml
FluCopyableText {
    text: qsTr("이 텍스트는 마우스로 드래그하여 복사할 수 있습니다.")
    width: 300
}
```

#### 참고 사항

*   `TextEdit`를 기반으로 하지만 `readOnly`가 `true`로 고정되어 편집은 불가능합니다.
*   마우스 오른쪽 버튼 클릭 시 복사 메뉴(`FluTextBoxMenu`)가 나타납니다.
*   마우스 커서는 I-Beam 형태로 표시되어 선택 가능한 텍스트임을 나타냅니다.

---

## 텍스트 입력 컴포넌트 (TextBox)

텍스트 입력 필드는 사용자가 텍스트를 입력하고 편집할 수 있는 컨트롤입니다. `FluTextBox`와 `FluMultilineTextBox`는 각각 `QtQuick.Controls.TextField`와 `QtQuick.Controls.TextArea`를 기반으로 합니다.

### 주요 공통 기능 (TextBox 계열)

*   **기반 클래스**: `TextField` (단일 라인), `TextArea` (여러 라인). 이 클래스들의 속성, 메소드, 시그널을 대부분 상속받습니다.
*   **컨텍스트 메뉴**: 마우스 오른쪽 클릭 시 복사, 붙여넣기, 잘라내기, 모두 선택 등을 수행할 수 있는 `FluTextBoxMenu`가 기본 제공됩니다 (Password 모드 제외).
*   **플레이스홀더 텍스트**: 입력 필드가 비어 있을 때 표시되는 안내 문구 (`placeholderText`)를 지원합니다.
*   **색상 테마**: `FluTheme`(다크/라이트 모드) 및 포커스 상태에 따라 텍스트, 플레이스홀더, 배경 색상이 동적으로 변경됩니다.
*   **렌더링 타입**: `FluTheme.nativeText` 설정에 따라 네이티브 또는 Qt 렌더링을 사용합니다.
*   **비활성화**: `disabled` 프로퍼티를 `true`로 설정하여 입력을 막을 수 있습니다.

### 주요 공통 프로퍼티 (TextBox 계열)

| 이름                   | 타입    | 기본값                  | 설명                                                                           |
| :--------------------- | :------ | :---------------------- | :----------------------------------------------------------------------------- |
| `text`                 | `string`| `""`                    | 입력 필드의 현재 텍스트 내용. (상속됨)                                             |
| `font`                 | `font`  | `FluTextStyle.Body`     | 입력 텍스트의 글꼴. (상속됨)                                                   |
| `color`                | `color` | `FluTheme` 기반 자동 계산 | 활성/비활성 상태에 따른 텍스트 색상. (상속됨)                                    |
| `placeholderText`      | `string`| `""`                    | 입력 필드가 비어 있고 포커스가 없을 때 표시되는 텍스트. (상속됨)                 |
| `placeholderTextColor` | `color` | `FluTheme` 기반 자동 계산 | 포커스 및 활성 상태에 따른 플레이스홀더 텍스트 색상. (상속됨)                      |
| `readOnly`             | `bool`  | `false`                 | 읽기 전용 모드 설정. `true`이면 편집 불가. (상속됨)                             |
| `disabled`             | `bool`  | `false`                 | 컴포넌트 비활성화 여부.                                                          |
| `enabled`              | `bool`  | `!disabled`             | 컴포넌트 활성화 여부 (읽기 전용). `disabled`에 의해 제어됨.                      |
| `selectionColor`       | `color` | `FluTheme.primaryColor` (반투명) | 텍스트 선택 시 배경 색상. (상속됨)                                             |
| `selectedTextColor`    | `color` | `color` (현재 텍스트 색상) | 텍스트 선택 시 글자 색상. (상속됨)                                             |
| `selectByMouse`        | `bool`  | `true`                  | 마우스로 텍스트 선택 가능 여부. (상속됨)                                         |

### 주요 공통 메소드 (TextBox 계열)

`TextInput`에서 상속받는 주요 메소드입니다.

| 이름        | 파라미터                             | 반환 타입 | 설명                                                   |
| :---------- | :----------------------------------- | :-------- | :----------------------------------------------------- |
| `copy()`    | 없음                                 | `void`    | 현재 선택된 텍스트를 클립보드에 복사합니다.             |
| `cut()`     | 없음                                 | `void`    | 현재 선택된 텍스트를 잘라내어 클립보드에 복사합니다.   |
| `paste()`   | 없음                                 | `void`    | 클립보드의 텍스트를 현재 커서 위치에 붙여넣습니다.       |
| `selectAll()`| 없음                               | `void`    | 입력 필드의 모든 텍스트를 선택합니다.                   |
| `clear()`   | 없음                                 | `void`    | 입력 필드의 모든 텍스트를 지웁니다 (`TextField` 기반). |
| `insert(position, text)` | `position`: `int`, `text`: `string` | `void`    | 지정된 위치에 텍스트를 삽입합니다 (`TextArea` 기반).   |

### 주요 공통 시그널 (TextBox 계열)

`TextInput` 등에서 상속받는 주요 시그널입니다.

| 이름                 | 파라미터 | 반환타입 | 설명                                                       |
| :------------------- | :------- | :------- | :--------------------------------------------------------- |
| `textChanged()`        | 없음     | -        | `text` 프로퍼티의 내용이 변경될 때마다 발생합니다.         |
| `selectionChanged()`   | 없음     | -        | 텍스트 선택 영역이 변경될 때 발생합니다.                   |
| `accepted()`           | 없음     | -        | 사용자가 Enter/Return 키를 눌러 입력 완료를 나타낼 때 발생. |
| `editingFinished()`    | 없음     | -        | 사용자가 입력을 마치고 포커스를 잃었을 때 발생합니다.       |

---

### 3. FluTextBox

단일 라인 텍스트 입력을 위한 컨트롤입니다. `QtQuick.Controls.TextField`를 기반으로 합니다.

#### 고유/특징적 프로퍼티

| 이름                   | 타입    | 기본값                  | 설명                                                         |
| :--------------------- | :------ | :---------------------- | :----------------------------------------------------------- |
| `iconSource`           | `int`   | `0`                     | 입력 필드 오른쪽에 표시할 아이콘 소스 (예: `FluentIcons.Search`). 0이면 표시 안 함. |
| `normalColor`          | `color` | `FluTheme` 기반 자동 계산 | 활성 상태 텍스트 색상.                                       |
| `disableColor`         | `color` | `FluTheme` 기반 자동 계산 | 비활성 상태 텍스트 색상.                                     |
| `placeholderNormalColor`| `color`| `FluTheme` 기반 자동 계산 | 포커스 없을 때 플레이스홀더 색상.                            |
| `placeholderFocusColor`| `color`| `FluTheme` 기반 자동 계산 | 포커스 있을 때 플레이스홀더 색상.                            |
| `placeholderDisableColor`| `color`| `FluTheme` 기반 자동 계산 | 비활성 상태 플레이스홀더 색상.                               |
| `cleanEnabled`         | `bool`  | `true`                  | 텍스트 입력 시 오른쪽에 '지우기(X)' 버튼 표시 여부.          |

#### 고유 시그널

| 이름          | 파라미터       | 반환타입 | 설명                                                  |
| :------------ | :------------- | :------- | :---------------------------------------------------- |
| `commit(text)`| `text`: `string` | -        | 사용자가 Enter 또는 Return 키를 눌렀을 때 발생합니다. 현재 텍스트를 전달합니다. |

*(이 외 `TextField` 및 공통 프로퍼티, 메소드, 시그널 상속)*

#### 예제

```qml
FluTextBox {
    placeholderText: qsTr("이름 입력...")
    cleanEnabled: true
    iconSource: FluentIcons.Contact // 오른쪽에 아이콘 표시
    width: 200
    onCommit: (text) => {
        console.log("입력 완료:", text)
    }
}
```

#### 참고 사항

*   `FluPasswordBox`는 `FluTextBox`를 기반으로 `echoMode: TextInput.Password`가 설정된 컴포넌트입니다. (별도 문서 참고)
*   `cleanEnabled`가 `true`이고 `readOnly`가 `false`이며 텍스트가 있을 때, 오른쪽에 X 버튼이 나타나 클릭 시 내용을 지울 수 있습니다.
*   Enter/Return 키를 누르면 `commit` 시그널이 발생하며, 이는 `accepted` 시그널과 유사하게 동작합니다.

---

### 4. FluPasswordBox

비밀번호 입력을 위한 컨트롤입니다. `QtQuick.Controls.TextField`를 기반으로 하며, 입력된 문자를 마스킹 처리하고 비밀번호를 일시적으로 볼 수 있는 기능을 제공합니다.

#### 기반 클래스

`TextField` (from `QtQuick.Controls.Basic`) - `FluTextBox`와 동일한 기반 클래스를 사용하며 유사한 스타일링 및 공통 기능을 공유합니다.

#### 고유/특징적 프로퍼티

| 이름                   | 타입    | 기본값                  | 설명                                                         |
| :--------------------- | :------ | :---------------------- | :----------------------------------------------------------- |
| `echoMode`             | `enum`  | `TextField.Password`    | 텍스트 표시 모드. 기본적으로 비밀번호 마스킹(*) 처리됩니다. (상속됨) |
| `disabled`             | `bool`  | `false`                 | 컴포넌트 비활성화 여부.                                      |
| `normalColor`          | `color` | `FluTheme` 기반 자동 계산 | 활성 상태 텍스트 색상.                                       |
| `disableColor`         | `color` | `FluTheme` 기반 자동 계산 | 비활성 상태 텍스트 색상.                                     |
| `placeholderNormalColor`| `color`| `FluTheme` 기반 자동 계산 | 포커스 없을 때 플레이스홀더 색상.                            |
| `placeholderFocusColor`| `color`| `FluTheme` 기반 자동 계산 | 포커스 있을 때 플레이스홀더 색상.                            |
| `placeholderDisableColor`| `color`| `FluTheme` 기반 자동 계산 | 비활성 상태 플레이스홀더 색상.                               |
| (내부) `btn_reveal`    | `FluIconButton` | -                   | 텍스트가 있을 때 오른쪽에 표시되는 '비밀번호 보기' 버튼 (`FluentIcons.RevealPasswordMedium`). 이 버튼을 누르고 있는 동안 `echoMode`가 `TextField.Normal`로 변경되어 비밀번호가 표시됩니다. |

#### 고유 시그널

| 이름          | 파라미터       | 반환타입 | 설명                                                  |
| :------------ | :------------- | :------- | :---------------------------------------------------- |
| `commit(text)`| `text`: `string` | -        | 사용자가 Enter 또는 Return 키를 눌렀을 때 발생합니다. 현재 텍스트를 전달합니다. |

*(이 외 `TextField` 및 `FluTextBox`와 공유하는 공통 프로퍼티, 메소드, 시그널 상속)*

#### 예제

```qml
FluPasswordBox {
    placeholderText: qsTr("비밀번호를 입력하세요")
    width: 240
    onCommit: (text) => {
        // 주의: 실제 비밀번호를 로그로 남기지 마세요!
        console.log("비밀번호 입력 완료 (길이):", text.length)
        // 여기에 비밀번호 처리 로직 추가 (예: 로그인 시도)
    }
}

// 비활성화 예제 (T_TextBox.qml 참조)
FluToggleSwitch { id: passwordSwitch }
FluPasswordBox {
    // ...
    disabled: passwordSwitch.checked
}
```

#### 참고 사항

*   `FluPasswordBox`는 `FluTextBox`와 매우 유사하지만, `echoMode`가 기본적으로 `Password`로 설정되어 있고, '비밀번호 보기' 기능이 내장되어 있습니다.
*   '비밀번호 보기' 버튼(`btn_reveal`)은 입력 필드에 텍스트가 있을 때만 나타납니다. 버튼을 누르고 있는 동안만 비밀번호가 표시되고, 떼면 다시 마스킹 처리됩니다.
*   `FluTextBoxMenu` (복사/붙여넣기 등 컨텍스트 메뉴)가 포함되어 있습니다. 보안상의 이유로 실제 서비스에서는 이 메뉴의 특정 기능을 비활성화하는 것을 고려할 수 있습니다.
*   **보안 주의**: `commit` 시그널 등으로 비밀번호 텍스트를 전달받은 후에는, 애플리케이션 로직에서 해당 데이터를 안전하게 처리해야 합니다. 평문으로 로그를 남기거나 저장하지 않도록 각별히 주의해야 합니다.

---

### 5. FluMultilineTextBox

여러 줄의 텍스트를 입력하고 편집할 수 있는 컨트롤입니다. `QtQuick.Controls.TextArea`를 기반으로 합니다.

#### 고유/특징적 프로퍼티

| 이름                   | 타입    | 기본값                  | 설명                                                         |
| :--------------------- | :------ | :---------------------- | :----------------------------------------------------------- |
| `normalColor`          | `color` | `FluTheme` 기반 자동 계산 | 활성 상태 텍스트 색상.                                       |
| `disableColor`         | `color` | `FluTheme` 기반 자동 계산 | 비활성 상태 텍스트 색상.                                     |
| `placeholderNormalColor`| `color`| `FluTheme` 기반 자동 계산 | 포커스 없을 때 플레이스홀더 색상.                            |
| `placeholderFocusColor`| `color`| `FluTheme` 기반 자동 계산 | 포커스 있을 때 플레이스홀더 색상.                            |
| `placeholderDisableColor`| `color`| `FluTheme` 기반 자동 계산 | 비활성 상태 플레이스홀더 색상.                               |
| `isCtrlEnterForNewline`| `bool`  | `false`                 | `true`: Ctrl+Enter로 줄바꿈, Enter로 `commit` 시그널 발생.<br>`false`: Enter로 줄바꿈, Ctrl+Enter로 `commit` 시그널 발생. |
| `wrapMode`             | `enum`  | `Text.WrapAnywhere`     | 텍스트 줄 바꿈 모드 (예: `Text.WrapAnywhere`). (상속됨)         |

#### 고유 시그널

| 이름          | 파라미터       | 반환타입 | 설명                                                                                  |
| :------------ | :------------- | :------- | :------------------------------------------------------------------------------------ |
| `commit(text)`| `text`: `string` | -        | 사용자가 입력을 완료했을 때 (Enter 또는 Ctrl+Enter, `isCtrlEnterForNewline` 설정에 따라 다름) 발생합니다. |

*(이 외 `TextArea` 및 공통 프로퍼티, 메소드, 시그널 상속)*

#### 예제

```qml
FluMultilineTextBox {
    placeholderText: qsTr("여기에 여러 줄의 텍스트를 입력하세요...\nEnter 키로 줄바꿈, Ctrl+Enter로 완료됩니다.")
    width: 300
    height: 100
    isCtrlEnterForNewline: false // 기본값
    onCommit: (text) => {
        console.log("최종 텍스트:", text)
    }
}
```

#### 참고 사항

*   `isCtrlEnterForNewline` 프로퍼티를 통해 Enter 키와 Ctrl+Enter 키의 동작(줄바꿈 vs 커밋)을 설정할 수 있습니다.
*   `TextArea`의 모든 기능을 상속받으므로, 스크롤, 텍스트 조작 등이 가능합니다.
*   `FluAutoSuggestBox`와 `FluSpinBox`는 텍스트 입력과 관련된 다른 특수 컨트롤입니다. (별도 문서 참고)
