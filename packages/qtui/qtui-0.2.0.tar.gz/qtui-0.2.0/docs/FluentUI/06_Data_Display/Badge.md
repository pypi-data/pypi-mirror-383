# Fluent UI 배지 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluBadge` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 주로 다른 UI 요소의 모서리에 부착되어 알림 수나 상태를 나타내는 작은 시각적 표시기입니다.

## 공통 임포트 방법

Fluent UI 배지 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluBadge

`FluBadge`는 일반적으로 알림 아이콘, 아바타, 메뉴 항목 등의 오른쪽 상단 모서리에 위치하여 처리해야 할 항목의 수(예: 읽지 않은 메시지)나 특정 상태(예: '새로운' 상태 표시 점)를 사용자에게 알려주는 데 사용됩니다. 숫자 또는 작은 점 형태로 표시될 수 있으며, 부모 요소에 쉽게 부착할 수 있는 기능을 제공합니다.

### 기반 클래스

`Rectangle`

### 고유/특징적 프로퍼티

| 이름       | 타입    | 기본값                                | 설명                                                                                                         |
| :--------- | :------ | :------------------------------------ | :----------------------------------------------------------------------------------------------------------- |
| `count`    | `int`   | `0`                                   | 배지에 표시할 숫자. 이 값에 따라 배지의 크기가 자동으로 조절됩니다 (1-9, 10-99, 100+). 100 이상은 "99+"로 표시될 수 있습니다. |
| `isDot`    | `bool`  | `false`                               | `true`이면 `count` 값 대신 작은 원형 점을 표시합니다. 점 모드에서는 크기가 고정됩니다.                                |
| `showZero` | `bool`  | `false`                               | `true`이면 `count`가 0일 때도 배지를 표시합니다. `false`이면 `count`가 0일 때 배지가 자동으로 숨겨집니다(`visible` = `false`).     |
| `topRight` | `bool`  | `false`                               | `true`이면 배지를 부모(`parent`) 아이템의 오른쪽 상단 모서리에 자동으로 배치합니다. 위치 조정을 위한 음수 여백이 적용됩니다.               |
| `color`    | `color` | `Qt.rgba(255/255,77/255,79/255,1)` (빨간색) | 배지의 배경색.                                                                                                |

*   `border.color`, `border.width`, `radius`: `Rectangle`에서 상속받는 테두리 및 모서리 둥글기 속성도 사용 가능하며, 기본값이 설정되어 있습니다 (`border.width`: 1, `border.color`: 흰색, `radius`: 너비/높이에 따라 자동 조절).
*   `width`, `height`: `isDot` 및 `count` 값에 따라 자동으로 계산됩니다.
*   `visible`: `count` 값과 `showZero` 설정에 따라 자동으로 결정됩니다 (`count`가 0이고 `showZero`가 `false`이면 `false`).

### 고유 시그널 / 메소드

`FluBadge` 자체에 고유한 시그널이나 메소드는 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

RowLayout {
    spacing: 30

    // 기본 숫자 배지 (count = 5)
    Rectangle {
        width: 40; height: 40; radius: 8; color: "lightgrey"
        FluBadge {
            topRight: true // 부모의 우측 상단에 자동 배치
            count: 5
        }
    }

    // 숫자 배지 (count = 50)
    Rectangle {
        width: 40; height: 40; radius: 8; color: "lightgrey"
        FluBadge {
            topRight: true
            count: 50
        }
    }

    // 숫자 배지 (count = 100 -> 99+)
    Rectangle {
        width: 40; height: 40; radius: 8; color: "lightgrey"
        FluBadge {
            topRight: true
            count: 120 // 100 이상은 99+ 로 표시될 수 있음 (구현 확인 필요, 예시에서는 100으로 가정)
        }
    }

    // 점 형태 배지
    Rectangle {
        width: 40; height: 40; radius: 8; color: "lightgrey"
        FluBadge {
            topRight: true
            isDot: true
            // isDot=true 이면 count 값은 무시됨
        }
    }

    // showZero=true 일 때 count = 0
    Rectangle {
        width: 40; height: 40; radius: 8; color: "lightgrey"
        FluBadge {
            topRight: true
            showZero: true
            count: 0 // showZero가 true 이므로 표시됨
        }
    }

    // 사용자 정의 색상
    Rectangle {
        width: 40; height: 40; radius: 8; color: "lightgrey"
        FluBadge {
            topRight: true
            count: 15
            color: "#52c41a" // 녹색 계열
        }
    }
}
```

### 참고 사항

*   **위치 지정**: `FluBadge`를 다른 요소 위에 표시하려면 해당 요소의 자식으로 `FluBadge`를 배치하고 `topRight: true`를 설정하는 것이 가장 간편합니다. 필요하다면 `anchors`를 직접 설정하여 위치를 미세 조정할 수도 있습니다.
*   **크기 조절**: 숫자 모드에서 배지의 너비는 `count` 값(자릿수)에 따라 자동으로 변경됩니다 (1-9, 10-99, 100+). `isDot` 모드에서는 고정된 작은 크기를 가집니다. 높이와 모서리 반경(`radius`)도 이에 맞춰 조정됩니다.
*   **가시성**: 기본적으로 `count`가 0이면 배지는 보이지 않습니다. 0일 때도 배지를 표시하려면 `showZero: true`를 설정해야 합니다. 