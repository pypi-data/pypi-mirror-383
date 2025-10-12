# Fluent UI 스크롤 컨트롤 (FluScrollBar & FluScrollIndicator)

이 문서에서는 `FluentUI` 모듈에서 스크롤 가능한 뷰(`Flickable`, `ListView` 등)와 함께 사용되어 스크롤 상태를 시각적으로 표시하고 상호작용하는 컨트롤인 `FluScrollBar`와 `FluScrollIndicator`에 대해 설명합니다.

## 공통 임포트 방법

스크롤 컨트롤을 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import QtQuick.Templates as T // 기반 템플릿 사용 시
import FluentUI 1.0
```

---

## FluScrollBar

`FluScrollBar`는 사용자가 스크롤 위치를 확인하고 직접 조작할 수 있는 Fluent UI 스타일의 스크롤바입니다. `QtQuick.Templates.ScrollBar`를 기반으로 하며, 마우스 호버(hover) 시 확장되는 시각적 효과와 선택적인 증가/감소 버튼을 포함합니다.

### 기반 클래스

`QtQuick.Templates.ScrollBar` (QML에서는 `T.ScrollBar`으로 사용)

### 주요 프로퍼티

| 이름              | 타입    | 기본값                  | 설명                                                                                                                                                                       |
| :---------------- | :------ | :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `orientation`     | `enum`  | (뷰에 따라 자동 설정)   | 스크롤바의 방향 (`Qt.Horizontal` 또는 `Qt.Vertical`). 일반적으로 스크롤바를 연결하는 뷰(`ScrollView`, `ListView` 등)에 의해 자동으로 설정됩니다. (상속됨)                               |
| `policy`          | `enum`  | `T.ScrollBar.AsNeeded`  | 스크롤바가 표시되는 정책 (`AlwaysOn`, `AlwaysOff`, `AsNeeded`). 기본값은 콘텐츠 크기가 뷰 크기를 초과할 때만 표시됩니다. (상속됨)                                                     |
| `active`          | `bool`  | (읽기 전용)             | 사용자가 스크롤바와 상호작용 중(예: 마우스 호버, 드래그)인지 여부를 나타냅니다. (상속됨)                                                                                         |
| `pressed`         | `bool`  | (읽기 전용)             | 사용자가 스크롤바의 핸들(막대)을 누르고 있는지 여부를 나타냅니다. (상속됨)                                                                                                  |
| `size`            | `real`  | (뷰에 따라 자동 계산)   | 현재 뷰에 보이는 콘텐츠의 비율 (0.0 ~ 1.0). 이 값에 따라 스크롤바 핸들의 길이가 결정됩니다. (상속됨)                                                                                 |
| `position`        | `real`  | (뷰에 따라 자동 계산)   | 현재 스크롤 위치 (0.0 ~ 1.0). (상속됨)                                                                                                                                     |
| `visible`         | `bool`  | `policy !== AlwaysOff`  | 스크롤바의 현재 가시성 상태입니다. `policy` 및 콘텐츠 크기에 따라 결정됩니다. (상속됨)                                                                                            |
| `color`           | `color` | 테마 기반 자동 설정       | 스크롤바 핸들(막대)의 기본 색상입니다. (기본: `FluTheme.dark` ? `#9F9F9F` : `#8A8A8A`)                                                                                        |
| `pressedColor`    | `color` | 테마 기반 자동 설정       | 스크롤바 핸들을 누르고 있을 때의 색상입니다. (기본 `color`보다 약간 밝거나 어둡게)                                                                                               |
| `minimumSize`     | `real`  | (자동 계산, 최소 0.3)  | 스크롤바 핸들의 최소 상대 크기입니다. 콘텐츠가 매우 길어도 핸들이 너무 작아지지 않도록 보장합니다.                                                                                   |
| `verticalPadding` | `real`  | 수직: 15, 수평: 3       | 스크롤바 트랙(배경)의 수직 여백입니다.                                                                                                                                      |
| `horizontalPadding`| `real` | 수직: 3, 수평: 15       | 스크롤바 트랙(배경)의 수평 여백입니다.                                                                                                                                      |

*(이 외 `T.ScrollBar`로부터 `increase()`, `decrease()`, `step`, `interactive` 등 다수의 프로퍼티, 메소드, 시그널 상속)*

### 주요 특징 및 동작

*   **Fluent UI 스타일**: 둥근 모서리의 핸들(막대)과 배경, 테마에 맞는 색상을 사용합니다.
*   **호버 효과 (확장)**: 사용자가 스크롤바 영역에 마우스를 올리거나 상호작용(`active` 상태)하면 스크롤바 핸들(막대)과 배경의 두께/너비가 증가하고, 증가/감소 버튼(`FluIconButton`)이 나타납니다. 마우스가 벗어나면 일정 시간 후 다시 원래 크기로 축소됩니다.
*   **증가/감소 버튼**: 스크롤바 양 끝에 작은 화살표 버튼(`FluIconButton`)이 있으며, 클릭 시 `increase()` 또는 `decrease()` 메소드를 호출하여 스크롤 위치를 조금씩 이동시킵니다. 이 버튼들은 호버 시에만 완전히 표시됩니다.
*   **자동 숨김**: `policy`가 `AsNeeded`(기본값)일 경우, 스크롤이 필요 없을 때는 스크롤바가 보이지 않습니다.

### 예제

`FluScrollBar`는 일반적으로 `ScrollView`, `ListView`, `Flickable` 등 스크롤 가능한 뷰의 `ScrollBar.vertical` 또는 `ScrollBar.horizontal` 프로퍼티에 할당하여 사용합니다.

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

Flickable {
    id: flickable
    width: 200
    height: 150
    contentHeight: 500 // 콘텐츠 높이가 뷰 높이보다 큼
    clip: true

    // Flickable 내부 콘텐츠 (예: 긴 텍스트)
    FluText {
        width: flickable.width
        text: "매우 긴 텍스트...".repeat(20)
        wrapMode: Text.Wrap
    }

    // 수직 스크롤바로 FluScrollBar 사용
    ScrollBar.vertical: FluScrollBar {}

    // (필요시) 수평 스크롤바도 추가 가능
    // contentWidth: 400
    // ScrollBar.horizontal: FluScrollBar {}
}
```

### 참고 사항

*   `FluScrollablePage` 컴포넌트는 내부적으로 수직 스크롤을 위해 `FluScrollBar`를 사용합니다.
*   스크롤바의 시각적 크기(두께/너비)는 내부 `d.minLine`(최소 2)과 `d.maxLine`(최대 6) 값 및 `active` 상태에 따라 동적으로 변합니다.
*   색상(`color`, `pressedColor`) 등은 필요에 따라 직접 재정의할 수 있습니다.

---

## FluScrollIndicator

`FluScrollIndicator`는 스크롤 가능한 뷰의 현재 스크롤 위치를 시각적으로 나타내는 더 간단하고 비간섭적인 표시기입니다. `QtQuick.Templates.ScrollIndicator`를 기반으로 하며, 보통 사용자가 스크롤할 때 잠시 나타났다가 사라지는 얇은 막대 형태로 표시됩니다.

### 기반 클래스

`QtQuick.Templates.ScrollIndicator` (QML에서는 `T.ScrollIndicator`으로 사용)

### 주요 프로퍼티

| 이름          | 타입    | 기본값                | 설명                                                                                                          |
| :------------ | :------ | :-------------------- | :---------------------------------------------------------------------------------------------------------- |
| `orientation` | `enum`  | (뷰에 따라 자동 설정) | 표시기의 방향 (`Qt.Horizontal` 또는 `Qt.Vertical`). (상속됨)                                                      |
| `active`      | `bool`  | (뷰에 따라 자동 설정) | 표시기가 활성 상태인지 여부. 일반적으로 사용자가 스크롤(flick)하는 동안 `true`가 됩니다. (상속됨)                            |
| `size`        | `real`  | (뷰에 따라 자동 계산) | 현재 뷰에 보이는 콘텐츠의 비율 (0.0 ~ 1.0). 표시기 막대의 길이를 결정합니다. (상속됨)                                |
| `position`    | `real`  | (뷰에 따라 자동 계산) | 현재 스크롤 위치 (0.0 ~ 1.0). 표시기 막대의 위치를 결정합니다. (상속됨)                                        |
| `padding`     | `real`  | `2`                   | 표시기와 뷰 가장자리 사이의 여백입니다. (상속됨)                                                                  |

*(이 외 `T.ScrollIndicator`로부터 `minimumSize` 등 일부 프로퍼티 상속)*

### 주요 특징 및 동작

*   **간결한 디자인**: 기본적으로 얇은 회색(`control.palette.mid`) 직사각형 막대로 표시됩니다.
*   **자동 페이드 효과**: `active` 상태가 되면(`when: control.active`) 즉시 표시기(`contentItem`)의 `opacity`가 0.75로 설정되어 나타납니다. `active` 상태가 해제되면, 일정 시간(450ms) 대기 후 200ms 동안 서서히 투명해지며 사라집니다.
*   **비상호작용**: 사용자가 직접 드래그하거나 클릭할 수 없습니다. 단순히 스크롤 위치 정보만 제공합니다.

### 예제

`FluScrollBar`와 마찬가지로 스크롤 가능한 뷰의 `ScrollIndicator.vertical` 또는 `ScrollIndicator.horizontal` 프로퍼티에 할당하여 사용합니다.

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0

Flickable {
    width: 200
    height: 150
    contentHeight: 500
    clip: true
    flickableDirection: Flickable.VerticalFlick // 스크롤 방향 설정

    // ... Flickable 내부 콘텐츠 ...

    // 기본 스크롤바 대신 FluScrollIndicator 사용
    ScrollIndicator.vertical: FluScrollIndicator {}
}
```

### 참고 사항

*   `FluScrollIndicator`는 터치스크린 환경이나 미니멀한 UI 디자인에서 스크롤바 대신 사용하기에 적합합니다.
*   `FluScrollBar`와 달리 증가/감소 버튼이나 직접적인 핸들 조작 기능이 없습니다.
*   표시기 막대의 색상(`control.palette.mid`), 크기(`implicitWidth/Height`), 페이드 아웃 시간 등은 필요시 재정의할 수 있습니다. 