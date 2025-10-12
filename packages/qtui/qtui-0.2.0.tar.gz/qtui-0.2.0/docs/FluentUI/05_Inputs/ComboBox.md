# Fluent UI 콤보 상자 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluComboBox` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 드롭다운 목록에서 항목을 선택하거나 직접 값을 입력할 수 있는 컨트롤입니다.

## 공통 임포트 방법

Fluent UI 콤보 상자 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluComboBox

`FluComboBox`는 현재 선택된 값을 표시하는 텍스트 필드와 드롭다운 목록을 여는 화살표 아이콘으로 구성된 컨트롤입니다. 사용자는 드롭다운 목록에서 미리 정의된 옵션 중 하나를 선택할 수 있습니다. `editable` 프로퍼티를 `true`로 설정하면 사용자가 텍스트 필드에 직접 값을 입력할 수도 있으며, 입력된 값을 모델에 추가하는 등의 상호작용이 가능합니다. `QtQuick.Templates.ComboBox`를 기반으로 하며 Fluent UI 스타일이 적용되었습니다.

### 기반 클래스

`QtQuick.Templates.ComboBox` (T.ComboBox)

### 주요 상속 프로퍼티 (T.ComboBox)

`FluComboBox`는 `T.ComboBox`의 모든 표준 프로퍼티와 메소드를 상속받습니다. 자주 사용되는 멤버는 다음과 같습니다:

*   `model`: 드롭다운 목록에 표시할 데이터 모델 (`ListModel`, JavaScript 배열 등).
*   `currentIndex`: 현재 선택된 항목의 모델 인덱스.
*   `currentText`: 현재 선택된 항목의 텍스트.
*   `displayText`: 비 편집 모드에서 텍스트 필드에 표시되는 텍스트 (`currentText`와 동일).
*   `editText`: 편집 모드에서 사용자가 입력/수정한 텍스트.
*   `editable`: `true`이면 사용자가 텍스트 필드에 직접 입력할 수 있습니다 (기본값 `false`).
*   `textRole`: 모델 데이터에서 텍스트로 사용할 역할(role) 이름.
*   `popup`: 드롭다운 목록을 표시하는 팝업 아이템.
*   `delegate`: 드롭다운 목록의 각 항목을 렌더링하는 컴포넌트 (기본값: `FluItemDelegate`).
*   `find(string text)`: 주어진 텍스트와 일치하는 첫 번째 항목의 인덱스를 반환하는 메소드.
*   `accepted()`: 사용자가 드롭다운 목록에서 항목을 선택하거나, 편집 모드에서 Enter/Return 키를 눌렀을 때 발생하는 시그널.

### 고유/스타일링 프로퍼티

`FluComboBox`는 Fluent UI 스타일을 적용하고 일부 기능을 추가하기 위해 다음과 같은 프로퍼티를 제공하거나 기본값을 재정의합니다:

| 이름           | 타입        | 기본값              | 설명                                                                                        |
| :------------- | :---------- | :------------------ | :------------------------------------------------------------------------------------------ |
| `disabled`     | `bool`      | `false`             | `true`이면 콤보 상자가 비활성화되어 상호작용할 수 없습니다. `enabled` 프로퍼티는 `!disabled`와 같습니다. |
| `normalColor`  | `color`     | (테마 기반)         | 기본 상태일 때의 배경색.                                                                       |
| `hoverColor`   | `color`     | (테마 기반)         | 마우스 호버 시 배경색.                                                                        |
| `disableColor` | `color`     | (테마 기반)         | 비활성화 상태일 때의 배경색.                                                                   |
| `textBox`      | `alias`     | 내부 `T.TextField`  | 내부 텍스트 필드 객체에 대한 별칭. 직접 접근하여 추가적인 속성을 제어할 수 있습니다.                         |
| `indicator`    | `Item`      | `FluIcon` 인스턴스  | 드롭다운 화살표 아이콘. `FluentIcons.ChevronDown`을 사용합니다.                                  |
| `contentItem`  | `T.TextField` | (커스텀 `TextField`) | 텍스트 표시 및 입력을 담당하는 내부 아이템. `FluTextBoxBackground`를 사용하여 Fluent 스타일 배경 및 포커스 효과를 구현합니다. |
| `background`   | `Rectangle` | (커스텀 `Rectangle`) | 주 배경 요소. 테두리, 둥근 모서리, 상태별 색상 및 `FluFocusRectangle`을 이용한 포커스 효과를 포함합니다.         |

### 고유 시그널

| 이름             | 파라미터         | 반환타입 | 설명                                                                                                    |
| :--------------- | :--------------- | :------- | :------------------------------------------------------------------------------------------------------ |
| `commit(string text)` | `string`: `text` | -        | `editable`이 `true`일 때, 사용자가 텍스트 필드에서 Enter 또는 Return 키를 눌러 입력 내용을 확정했을 때 발생합니다. 입력된 텍스트를 파라미터로 전달합니다. |

### 고유 메소드

`FluComboBox` 자체에 고유한 메소드는 정의되어 있지 않으며, `T.ComboBox`에서 상속된 메소드(예: `find()`)를 사용합니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 20
    width: 250

    // 기본 콤보 상자 (편집 불가)
    FluComboBox {
        id: comboBox1
        Layout.fillWidth: true
        model: ["항목 1", "항목 2", "항목 3"]
        currentIndex: 0 // 초기 선택 항목
        onCurrentTextChanged: console.log("선택됨:", currentText)
    }

    // 비활성화된 콤보 상자
    FluComboBox {
        Layout.fillWidth: true
        model: ["옵션 A", "옵션 B"]
        disabled: true
    }

    // 편집 가능한 콤보 상자 (새 항목 추가 기능 포함)
    FluComboBox {
        id: comboBoxEditable
        Layout.fillWidth: true
        editable: true
        model: ListModel {
            id: editableModel
            ListElement { text: "사과" }
            ListElement { text: "바나나" }
            ListElement { text: "오렌지" }
        }
        
        // Enter/Return 키 입력 완료 시 처리
        onCommit: (text) => {
            console.log("입력 완료 (commit):", text)
            if (comboBoxEditable.find(text) === -1) { // 목록에 없는 경우
                editableModel.append({ text: text })
                comboBoxEditable.currentIndex = comboBoxEditable.count - 1 // 새로 추가된 항목 선택
                console.log("새 항목 추가됨:", text)
            }
        }
        
        // 드롭다운에서 항목 선택 시 처리 (선택 사항)
        // onAccepted: console.log("항목 선택됨 (accepted):", currentText)
    }
}
```

### 참고 사항

*   **편집 가능 상태**: `editable`을 `true`로 설정하면 사용자는 텍스트 필드에 직접 텍스트를 입력할 수 있습니다. 입력 완료는 Enter 또는 Return 키를 눌렀을 때 `commit` 시그널을 통해 감지할 수 있습니다. 또한, 드롭다운 목록에서 항목을 선택하거나 Enter/Return 키를 누르면 `accepted` 시그널도 발생합니다.
*   **텍스트 프로퍼티**: `editable`이 `false`일 때는 `displayText` (주로 `currentText`와 동일)가 표시되고, `true`일 때는 사용자가 수정할 수 있는 `editText`가 표시됩니다.
*   **스타일링**: 배경색(`normalColor`, `hoverColor`, `disableColor`), 텍스트 색상, 포커스 테두리(`FluFocusRectangle`) 등이 Fluent UI 테마에 맞게 기본 설정되어 있습니다. 드롭다운 팝업(`popup`)과 목록 아이템(`delegate`) 역시 Fluent UI 스타일을 따릅니다.
*   **모델**: `model` 프로퍼티에는 문자열 리스트, `ListModel`, 또는 JavaScript 객체 배열 등을 지정할 수 있습니다. 객체 배열을 사용할 경우 `textRole` 프로퍼티를 설정하여 표시할 텍스트가 포함된 속성 이름을 지정해야 합니다. 