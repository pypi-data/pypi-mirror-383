# Fluent UI 라디오 버튼 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 라디오 버튼 관련 컴포넌트인 `FluRadioButton`과 이를 그룹으로 관리하는 `FluRadioButtons`에 대해 설명합니다. `FluRadioButton`은 기본적인 `QtQuick.Controls.Button`을 기반으로 하며, `FluRadioButtons`는 `Item`을 기반으로 자식 라디오 버튼들의 선택 상태를 관리합니다.

## 공통 임포트 방법

Fluent UI 라디오 버튼 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## 1. FluRadioButton

상호 배타적인 옵션 그룹 중 하나를 나타내는 개별 라디오 버튼입니다. 일반적으로 단독으로 사용되기보다는 `FluRadioButtons` 컨테이너 내에서 그룹으로 사용됩니다.

### 주요 상속 프로퍼티 (Button)

`FluRadioButton`은 `QtQuick.Controls.Button`의 프로퍼티를 상속받습니다. 자주 사용되는 주요 프로퍼티는 다음과 같습니다.

| 이름         | 타입     | 기본값              | 설명                                                         |
| :----------- | :------- | :------------------ | :----------------------------------------------------------- |
| `text`       | `string` | `""`                | 라디오 버튼 옆에 표시될 텍스트.                                |
| `font`       | `font`   | `FluTextStyle.Body` | 텍스트의 글꼴.                                               |
| `checked`    | `bool`   | `false`             | 라디오 버튼의 선택 여부. `FluRadioButtons`에 의해 관리됩니다. |
| `disabled`   | `bool`   | `false`             | 컴포넌트 비활성화 여부. `true`이면 `enabled`는 `false`가 됩니다. |
| `enabled`    | `bool`   | `!disabled`         | 컴포넌트 활성화 여부 (읽기 전용). `disabled`에 의해 제어됨.      |
| `focusPolicy`| `enum`   | `Qt.TabFocus`       | 키보드 포커스를 받는 정책.                                     |
| `hovered`    | `bool`   | (읽기 전용)         | 마우스 커서가 컴포넌트 위에 있는지 여부.                         |
| `pressed`    | `bool`   | (읽기 전용)         | 컴포넌트가 현재 눌려있는지 여부.                               |
| `activeFocus`| `bool`   | (읽기 전용)         | 현재 활성 키보드 포커스를 가지고 있는지 여부.                    |

### 고유/특징적 프로퍼티

| 이름            | 타입       | 기본값                             | 설명                                                                                |
| :-------------- | :--------- | :--------------------------------- | :---------------------------------------------------------------------------------- |
| `size`          | `real`     | `18`                               | 라디오 버튼 그래픽 영역의 크기 (원의 직경).                                         |
| `textRight`     | `bool`     | `true`                             | 텍스트를 라디오 버튼 오른쪽에 표시할지 여부. `false`이면 왼쪽에 표시됩니다.             |
| `textSpacing`   | `real`     | `6`                                | 라디오 버튼과 텍스트 사이의 간격.                                                     |
| `textColor`     | `color`    | (alias to `btn_text.textColor`)    | 텍스트 색상. `FluText`의 `textColor`를 따릅니다.                                      |
| `clickListener` | `function` | `function(){ checked = !checked }` | 클릭 시 실행될 사용자 정의 함수. `FluRadioButtons` 내에서는 그룹 관리를 위해 자동으로 재정의됩니다. |
| (색상 프로퍼티) | `color`    | (다양함)                           | `borderNormalColor`, `normalColor`, `hoverColor` 등 상태별 색상을 제어하는 다수의 프로퍼티. |

### 주요 상속 시그널 (Button)

| 이름         | 파라미터 | 반환타입 | 설명                                                         |
| :----------- | :------- | :------- | :----------------------------------------------------------- |
| `clicked()`    | 없음     | -        | 컴포넌트가 클릭되었을 때 발생 (`FluRadioButtons`가 선택 변경에 사용). |
| `toggled()`    | 없음     | -        | `checked` 프로퍼티의 값이 변경될 때 발생합니다.               |
| `pressed()`    | 없음     | -        | 컴포넌트가 눌렸을 때 발생합니다.                               |
| `released()`   | 없음     | -        | 컴포넌트에서 손을 떼었을 때 발생합니다.                         |

### 예제 (FluRadioButtons 내 사용)

```qml
FluRadioButtons {
    currentIndex: 0 // 첫 번째 버튼을 기본 선택
    FluRadioButton { text: qsTr("옵션 A") }
    FluRadioButton { text: qsTr("옵션 B") }
    FluRadioButton { text: qsTr("옵션 C") }
}
```

### 참고 사항

*   `FluRadioButton`은 시각적으로 원형이며, 선택 시 내부 원의 크기가 변경되는 애니메이션 효과가 있습니다.
*   개별 `FluRadioButton`의 `checked` 상태는 직접 제어하기보다는 `FluRadioButtons`의 `currentIndex`를 통해 관리하는 것이 일반적입니다.

---

## 2. FluRadioButtons

여러 개의 `FluRadioButton` (또는 `checked` 프로퍼티를 가진 유사 버튼)을 그룹으로 묶어 관리하는 컨테이너입니다. 그룹 내에서는 오직 하나의 버튼만 선택될 수 있도록 보장합니다.

### 고유/특징적 프로퍼티

| 이름           | 타입           | 기본값        | 설명                                                                                              |
| :------------- | :------------- | :------------ | :------------------------------------------------------------------------------------------------ |
| `buttons`      | `list<QtObject>`| `[]`          | **기본 프로퍼티**. 그룹으로 관리할 버튼 객체들의 리스트. `FluRadioButton` 등을 자식으로 추가하면 자동으로 채워집니다. |
| `currentIndex` | `int`          | `-1`          | 현재 선택된 버튼의 인덱스. `-1`은 아무것도 선택되지 않았음을 의미합니다. 이 값을 변경하면 해당 인덱스의 버튼이 선택됩니다. |
| `spacing`      | `int`          | `8`           | 버튼들 사이의 간격. 내부 레이아웃(`ColumnLayout` 또는 `RowLayout`)의 `spacing`으로 사용됩니다.                    |
| `orientation`  | `enum`         | `Qt.Vertical` | 버튼들을 배치할 방향 (`Qt.Vertical` 또는 `Qt.Horizontal`).                                         |
| `disabled`     | `bool`         | `false`       | 그룹 내 모든 버튼을 비활성화할지 여부.                                                            |

### 고유 시그널

| 이름                  | 파라미터 | 반환타입 | 설명                                    |
| :-------------------- | :------- | :------- | :-------------------------------------- |
| `currentIndexChanged()` | 없음     | -        | `currentIndex` 프로퍼티 값이 변경될 때 발생. |

### 예제

**1. 수직 라디오 버튼 그룹:**

```qml
FluRadioButtons {
    id: verticalGroup
    spacing: 10
    currentIndex: 1 // 두 번째 버튼 선택

    FluRadioButton { text: qsTr("옵션 1") }
    FluRadioButton { text: qsTr("옵션 2") }
    FluRadioButton { text: qsTr("옵션 3") }

    onCurrentIndexChanged: {
        console.log("선택 변경(수직):", currentIndex, buttons[currentIndex].text)
    }
}
```

**2. 수평 라디오 버튼 그룹:**

```qml
FluRadioButtons {
    orientation: Qt.Horizontal
    spacing: 20
    currentIndex: -1 // 선택 없음

    FluRadioButton { text: "A" }
    FluRadioButton { text: "B" }
    FluRadioButton { text: "C" }
    FluRadioButton { text: "D" }

    // 버튼 클릭 등으로 currentIndex가 변경되면 호출됨
    onCurrentIndexChanged: {
        if (currentIndex !== -1) {
            console.log("선택 변경(수평):", currentIndex, buttons[currentIndex].text)
        }
    }
}
```

### 참고 사항

*   `FluRadioButtons`는 자식으로 추가된 `FluRadioButton`들의 `clickListener`를 내부적으로 재정의하여, 클릭 시 해당 버튼의 인덱스로 `currentIndex`를 업데이트하고 다른 버튼들의 `checked` 상태를 `false`로 변경합니다.
*   `currentIndex` 프로퍼티를 `-1`로 설정하면 모든 버튼의 선택이 해제됩니다.
*   `orientation` 프로퍼티 값에 따라 내부적으로 `ColumnLayout` 또는 `RowLayout`을 사용하여 버튼들을 배치합니다.
*   `disabled` 프로퍼티를 `true`로 설정하면 그룹 내의 모든 라디오 버튼이 비활성화됩니다. 개별 버튼의 `disabled` 상태는 무시될 수 있습니다.
*   `FluRadioButton` 외에 `checked` 프로퍼티와 `clickListener`를 가진 다른 타입의 버튼(예: `FluCheckBox`)도 기술적으로는 `buttons` 리스트에 포함될 수 있으나, UI/UX 관점에서는 동일한 타입의 버튼을 사용하는 것이 일반적입니다. 