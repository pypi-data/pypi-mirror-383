# Fluent UI 진행률 표시 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 진행률 표시 컴포넌트인 `FluProgressBar`와 `FluProgressRing`에 대해 설명합니다. 이 컴포넌트들은 작업이나 프로세스의 진행 상태를 시각적으로 나타내는 데 사용됩니다.

## 공통 임포트 방법

Fluent UI 진행률 표시 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## 공통 기능 및 속성 (QtQuick.Controls.ProgressBar 기반)

`FluProgressBar`와 `FluProgressRing`은 모두 `QtQuick.Controls.ProgressBar`를 기반으로 하므로 다음과 같은 주요 프로퍼티를 공통으로 상속받아 사용합니다:

*   `value`: 현재 진행률 값. `from`과 `to` 사이의 값입니다.
*   `from`: 진행률의 최소값 (기본값: `0.0`).
*   `to`: 진행률의 최대값 (기본값: `1.0`).
*   `indeterminate`: 진행 상태를 알 수 없거나 정확한 값을 표시할 수 없을 때 사용되는 불확정 모드 여부 (`bool`). `true`이면 애니메이션 효과가 나타나며 `value`는 무시됩니다. (기본값: `true`)
*   `visualPosition`: `from`과 `to` 사이의 `value`를 `0.0`과 `1.0` 사이의 정규화된 값으로 나타냅니다.

--- 

## FluProgressBar

선형(막대) 형태의 진행률 표시기입니다. 작업의 진행도를 가로 막대로 표시합니다.

### 설명

`FluProgressBar`는 작업의 완료율을 직관적인 선형 막대로 보여줍니다. 확정적 모드에서는 `value`에 따라 채워진 막대의 길이가 변경되고, 불확정 모드에서는 막대의 일부가 계속해서 좌우로 움직이는 애니메이션을 표시하여 작업이 진행 중임을 나타냅니다.

### 고유/스타일링 프로퍼티

| 이름              | 타입    | 기본값                                      | 설명                                                                       |
| :---------------- | :------ | :------------------------------------------ | :------------------------------------------------------------------------- |
| `duration`        | `int`   | `888`                                       | 불확정(`indeterminate`=`true`) 상태일 때 애니메이션 한 주기의 시간 (밀리초).      |
| `strokeWidth`     | `real`  | `6`                                         | 진행률 막대의 두께(높이).                                                     |
| `progressVisible` | `bool`  | `false`                                     | 확정(`indeterminate`=`false`) 상태일 때 진행률 텍스트("NN%")를 표시할지 여부.   |
| `color`           | `color` | `FluTheme.primaryColor`                   | 진행률 막대의 색상.                                                          |
| `backgroundColor` | `color` | (테마 기반)                                 | 진행률 막대의 배경(채워지지 않은 부분) 색상.                                    |

### 고유 시그널 / 메소드

`FluProgressBar` 자체에 고유한 시그널이나 메소드는 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 20
    width: 300

    // 불확정 모드 (기본값)
    FluText { text: "Indeterminate ProgressBar" }
    FluProgressBar {
        Layout.fillWidth: true
    }

    // 확정 모드
    FluText { text: "Determinate ProgressBar" }
    FluProgressBar {
        Layout.fillWidth: true
        indeterminate: false
        value: 0.6 // 60%
    }

    // 확정 모드 + 진행률 텍스트 표시
    FluText { text: "Determinate ProgressBar with Text" }
    FluProgressBar {
        Layout.fillWidth: true
        indeterminate: false
        value: 0.75 // 75%
        progressVisible: true
    }
}
```

### 참고 사항

*   `indeterminate`가 `true`이면 `value` 프로퍼티는 무시되고 애니메이션이 표시됩니다.
*   `progressVisible`이 `true`이면 진행률 막대 오른쪽에 "NN%" 형식의 텍스트가 표시됩니다. 이 텍스트는 `indeterminate`가 `false`일 때만 보입니다.
*   `strokeWidth`로 막대의 높이를 조절할 수 있습니다.

--- 

## FluProgressRing

원형(링) 형태의 진행률 표시기입니다. 작업의 진행도를 원형 호(arc)로 표시합니다.

### 설명

`FluProgressRing`은 작업 완료율을 원형 링의 채워진 정도로 보여줍니다. 확정적 모드에서는 `value`에 따라 링의 호가 채워지고, 불확정 모드에서는 링의 일부 호가 계속 회전하는 애니메이션을 표시하여 작업이 진행 중임을 나타냅니다.

### 고유/스타일링 프로퍼티

| 이름              | 타입    | 기본값                                      | 설명                                                                       |
| :---------------- | :------ | :------------------------------------------ | :------------------------------------------------------------------------- |
| `duration`        | `int`   | `2000`                                      | 불확정(`indeterminate`=`true`) 상태일 때 애니메이션 한 주기의 시간 (밀리초).      |
| `strokeWidth`     | `real`  | `6`                                         | 진행률 링의 두께.                                                           |
| `progressVisible` | `bool`  | `false`                                     | 확정(`indeterminate`=`false`) 상태일 때 진행률 텍스트("NN%")를 링 중앙에 표시할지 여부. |
| `color`           | `color` | `FluTheme.primaryColor`                   | 진행률 링(호)의 색상.                                                        |
| `backgroundColor` | `color` | (테마 기반)                                 | 진행률 링의 배경(채워지지 않은 부분) 색상.                                    |

### 고유 시그널 / 메소드

`FluProgressRing` 자체에 고유한 시그널이나 메소드는 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

RowLayout {
    spacing: 30

    // 불확정 모드 (기본값)
    ColumnLayout { 
        FluText { text: "Indeterminate" }
        FluProgressRing { }
    }

    // 확정 모드
    ColumnLayout { 
        FluText { text: "Determinate" }
        FluProgressRing {
            indeterminate: false
            value: 0.6 // 60%
        }
    }

    // 확정 모드 + 진행률 텍스트 표시
    ColumnLayout { 
        FluText { text: "Determinate with Text" }
        FluProgressRing {
            indeterminate: false
            value: 0.75 // 75%
            progressVisible: true
        }
    }
}
```

### 참고 사항

*   `indeterminate`가 `true`이면 `value` 프로퍼티는 무시되고 회전하는 호 애니메이션이 표시됩니다.
*   `progressVisible`이 `true`이면 링의 중앙에 "NN%" 형식의 텍스트가 표시됩니다. 이 텍스트는 `indeterminate`가 `false`일 때만 보입니다.
*   `strokeWidth`로 링의 두께를 조절할 수 있습니다. 컴포넌트의 전체 크기는 `width`와 `height` 프로퍼티로 설정합니다 (기본값은 `56x56`). 