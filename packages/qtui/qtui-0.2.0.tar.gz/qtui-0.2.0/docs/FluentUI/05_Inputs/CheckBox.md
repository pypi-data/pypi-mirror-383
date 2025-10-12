# Fluent UI 체크박스 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluCheckBox` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 옵션을 선택하거나 해제할 수 있도록 하며, 기본적인 `QtQuick.Controls.Button`을 기반으로 합니다.

## 공통 임포트 방법

Fluent UI 체크박스 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluCheckBox

사용자가 옵션을 선택하거나 해제할 수 있는 컨트롤입니다. 선택됨(checked), 선택 안 됨(unchecked)의 2가지 상태뿐만 아니라, 불확정(indeterminate) 상태를 포함한 3가지 상태를 지원할 수 있습니다.

### 주요 상속 프로퍼티 (Button)

`FluCheckBox`는 `QtQuick.Controls.Button`의 프로퍼티를 상속받습니다. 자주 사용되는 주요 프로퍼티는 다음과 같습니다.

| 이름         | 타입     | 기본값              | 설명                                                         |
| :----------- | :------- | :------------------ | :----------------------------------------------------------- |
| `text`       | `string` | `""`                | 체크박스 옆에 표시될 텍스트.                                   |
| `font`       | `font`   | `FluTextStyle.Body` | 텍스트의 글꼴.                                               |
| `checked`    | `bool`   | `false`             | 체크박스의 선택 여부.                                        |
| `disabled`   | `bool`   | `false`             | 컴포넌트 비활성화 여부. `true`이면 `enabled`는 `false`가 됩니다. |
| `enabled`    | `bool`   | `!disabled`         | 컴포넌트 활성화 여부 (읽기 전용). `disabled`에 의해 제어됨.      |
| `focusPolicy`| `enum`   | `Qt.TabFocus`       | 키보드 포커스를 받는 정책.                                     |
| `hovered`    | `bool`   | (읽기 전용)         | 마우스 커서가 컴포넌트 위에 있는지 여부.                         |
| `pressed`    | `bool`   | (읽기 전용)         | 컴포넌트가 현재 눌려있는지 여부.                               |
| `activeFocus`| `bool`   | (읽기 전용)         | 현재 활성 키보드 포커스를 가지고 있는지 여부.                    |

### 고유/특징적 프로퍼티

| 이름            | 타입       | 기본값                             | 설명                                                                                      |
| :-------------- | :--------- | :--------------------------------- | :---------------------------------------------------------------------------------------- |
| `indeterminate` | `bool`     | `false`                            | 불확정 상태 여부. `true`이면 체크박스에 중간 상태(-) 아이콘이 표시됩니다.                      |
| `size`          | `real`     | `18`                               | 체크박스 그래픽 영역의 크기 (너비와 높이).                                                  |
| `textRight`     | `bool`     | `true`                             | 텍스트를 체크박스 오른쪽에 표시할지 여부. `false`이면 왼쪽에 표시됩니다.                          |
| `textSpacing`   | `real`     | `6`                                | 체크박스와 텍스트 사이의 간격.                                                              |
| `textColor`     | `color`    | (alias to `btn_text.textColor`)    | 텍스트 색상. `FluText`의 `textColor`를 따릅니다.                                            |
| `clickListener` | `function` | `function(){ checked = !checked }` | 클릭 시 실행될 사용자 정의 함수. 기본 동작은 `checked` 상태를 토글합니다. 3상태 구현 등에 사용됩니다. |
| `animationEnabled`| `bool`   | `FluTheme.animationEnabled`        | 상태 변경 시 애니메이션 효과 사용 여부.                                                     |
| (색상 프로퍼티) | `color`    | (다양함)                           | `borderNormalColor`, `checkedColor`, `hoverColor` 등 상태별 색상을 제어하는 다수의 프로퍼티. |

### 주요 상속 시그널 (Button)

| 이름         | 파라미터 | 반환타입 | 설명                                                  |
| :----------- | :------- | :------- | :---------------------------------------------------- |
| `clicked()`    | 없음     | -        | 컴포넌트가 클릭되었을 때 발생합니다.                   |
| `toggled()`    | 없음     | -        | `checked` 프로퍼티의 값이 변경될 때 발생합니다.        |
| `pressed()`    | 없음     | -        | 컴포넌트가 눌렸을 때 발생합니다.                        |
| `released()`   | 없음     | -        | 컴포넌트에서 손을 떼었을 때 발생합니다.                  |

### 예제

**1. 기본적인 2상태 체크박스:**

```qml
Row {
    spacing: 20
    FluCheckBox {
        text: qsTr("옵션 1")
        onCheckedChanged: console.log("옵션 1 선택됨:", checked)
    }
    FluCheckBox {
        text: qsTr("옵션 2 (왼쪽 텍스트)")
        textRight: false
        checked: true
    }
    FluCheckBox {
        text: qsTr("비활성화됨")
        disabled: true
    }
}
```

**2. 3상태 체크박스 구현:**

```qml
FluCheckBox {
    id: threeStateCheckbox
    property int currentState: 0 // 0: unchecked, 1: checked, 2: indeterminate
    text: qsTr("3상태 체크박스")

    // 초기 상태 설정 (예: 불확정 상태로 시작)
    Component.onCompleted: {
        setState(2); // indeterminate
    }

    // 클릭 시 상태 순환
    clickListener: function() {
        currentState = (currentState + 1) % 3;
        setState(currentState);
    }

    function setState(state) {
        if (state === 0) { // unchecked
            checked = false;
            indeterminate = false;
        } else if (state === 1) { // checked
            checked = true;
            indeterminate = false;
        } else { // indeterminate
            checked = true; // Indeterminate is visually a checked state
            indeterminate = true;
        }
        console.log("현재 상태:", state, " checked:", checked, " indeterminate:", indeterminate)
    }
}
```

### 참고 사항

*   **3상태 체크박스**: `indeterminate` 프로퍼티를 사용하여 3상태 체크박스를 구현할 수 있습니다. 일반적으로 `indeterminate`가 `true`일 때는 `checked`도 `true`로 설정해야 시각적으로 올바르게 표시됩니다 (배경색 적용). 상태 전환 로직은 예제와 같이 `clickListener`를 통해 직접 구현해야 합니다.
*   **클릭 동작 커스터마이징**: `clickListener` 프로퍼티에 사용자 정의 함수를 할당하여 체크박스를 클릭했을 때의 기본 동작(단순 토글)을 변경할 수 있습니다.
*   **텍스트 위치**: `textRight` 프로퍼티를 `false`로 설정하면 텍스트가 체크박스 왼쪽에 표시됩니다.
*   **색상 커스터마이징**: `borderNormalColor`, `checkedColor`, `hoverColor` 등 다양한 상태에 대한 색상 프로퍼티를 제공하여 세밀한 디자인 조정이 가능합니다.
*   `checkable` 프로퍼티는 내부적으로 관리되므로 직접 변경하지 않는 것이 좋습니다. 