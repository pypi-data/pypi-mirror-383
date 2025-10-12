# Fluent UI 토글 스위치 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluToggleSwitch` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 켜고 끌 수 있는 옵션을 나타내는 스위치 형태의 컨트롤이며, 기본적인 `QtQuick.Controls.Button`을 기반으로 합니다.

## 공통 임포트 방법

Fluent UI 토글 스위치 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluToggleSwitch

켜짐(checked) 또는 꺼짐(unchecked) 상태를 시각적인 스위치 형태로 나타내는 컨트롤입니다. 사용자가 클릭하거나 탭하여 상태를 변경할 수 있습니다.

### 주요 상속 프로퍼티 (Button)

`FluToggleSwitch`는 `QtQuick.Controls.Button`의 프로퍼티를 상속받습니다. 자주 사용되는 주요 프로퍼티는 다음과 같습니다.

| 이름         | 타입     | 기본값              | 설명                                                         |
| :----------- | :------- | :------------------ | :----------------------------------------------------------- |
| `text`       | `string` | `""`                | 스위치 옆에 표시될 텍스트.                                   |
| `font`       | `font`   | `FluTextStyle.Body` | 텍스트의 글꼴.                                               |
| `checked`    | `bool`   | `false`             | 스위치의 켜짐(on)/꺼짐(off) 상태.                            |
| `disabled`   | `bool`   | `false`             | 컴포넌트 비활성화 여부. `true`이면 `enabled`는 `false`가 됩니다. |
| `enabled`    | `bool`   | `!disabled`         | 컴포넌트 활성화 여부 (읽기 전용). `disabled`에 의해 제어됨.      |
| `focusPolicy`| `enum`   | `Qt.TabFocus`       | 키보드 포커스를 받는 정책.                                     |
| `hovered`    | `bool`   | (읽기 전용)         | 마우스 커서가 컴포넌트 위에 있는지 여부.                         |
| `pressed`    | `bool`   | (읽기 전용)         | 컴포넌트가 현재 눌려있는지 여부.                               |
| `activeFocus`| `bool`   | (읽기 전용)         | 현재 활성 키보드 포커스를 가지고 있는지 여부.                    |

### 고유/특징적 프로퍼티

| 이름            | 타입       | 기본값                             | 설명                                                                               |
| :-------------- | :--------- | :--------------------------------- | :--------------------------------------------------------------------------------- |
| `textRight`     | `bool`     | `true`                             | 텍스트를 스위치 오른쪽에 표시할지 여부. `false`이면 왼쪽에 표시됩니다.                  |
| `textSpacing`   | `real`     | `6`                                | 스위치와 텍스트 사이의 간격.                                                         |
| `textColor`     | `color`    | (alias to `btn_text.textColor`)    | 텍스트 색상. `FluText`의 `textColor`를 따릅니다.                                     |
| `clickListener` | `function` | `function(){ checked = !checked }` | 클릭 시 실행될 사용자 정의 함수. 기본 동작은 `checked` 상태를 토글합니다.               |
| (색상 프로퍼티) | `color`    | (다양함)                           | `checkColor`, `normalColor`, `hoverColor`, `borderNormalColor` 등 상태별 색상을 제어하는 다수의 프로퍼티. |

### 주요 상속 시그널 (Button)

| 이름         | 파라미터 | 반환타입 | 설명                                            |
| :----------- | :------- | :------- | :---------------------------------------------- |
| `clicked()`    | 없음     | -        | 컴포넌트가 클릭되었을 때 발생합니다.             |
| `toggled()`    | 없음     | -        | `checked` 프로퍼티의 값이 변경될 때 발생합니다.  |
| `pressed()`    | 없음     | -        | 컴포넌트가 눌렸을 때 발생합니다.                  |
| `released()`   | 없음     | -        | 컴포넌트에서 손을 떼었을 때 발생합니다.            |

### 예제

```qml
Column {
    spacing: 15
    FluToggleSwitch {
        id: switch1
        text: qsTr("알림 받기")
        checked: true
        onToggled: {
            console.log("알림 상태:", checked)
        }
    }

    FluToggleSwitch {
        text: qsTr("왼쪽 텍스트 스위치")
        textRight: false
    }

    FluToggleSwitch {
        // 텍스트 없음
    }

    FluToggleSwitch {
        text: qsTr("비활성화됨")
        disabled: true
        checked: true
    }
}
```

### 참고 사항

*   시각적으로 캡슐 모양의 배경과 그 안에서 좌우로 움직이는 원형 '닷(dot)'으로 구성됩니다.
*   `checked` 상태에 따라 배경색과 테두리색, 닷의 위치와 색상이 변경됩니다. 상태 변경 시 부드러운 애니메이션 효과가 적용됩니다 (`FluTheme.animationEnabled`가 true일 경우).
*   `textRight` 프로퍼티를 `false`로 설정하면 텍스트가 스위치 왼쪽에 표시됩니다.
*   `clickListener`를 재정의하여 클릭 시 기본 토글 동작 외의 다른 작업을 수행하거나 토글 조건을 변경할 수 있습니다. 