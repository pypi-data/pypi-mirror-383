# Fluent UI 평점 제어 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluRatingControl` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 별점과 같은 평점을 시각적으로 선택할 수 있는 인터페이스를 제공합니다.

## 공통 임포트 방법

Fluent UI 평점 제어 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluRatingControl

사용자가 일련의 아이콘(기본적으로 별 모양) 중에서 선택하여 항목에 대한 평점을 매길 수 있게 해주는 컨트롤입니다. 마우스를 아이콘 위로 가져가면 선택될 평점을 미리 보여주는 시각적 피드백을 제공하며, 클릭 시 해당 평점으로 값이 설정됩니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름      | 타입   | 기본값 | 설명                                                                                 |
| :-------- | :----- | :----- | :----------------------------------------------------------------------------------- |
| `value`   | `int`  | `0`    | 현재 선택된 평점 값 (채워진 별의 개수). 사용자가 별을 클릭하면 이 값이 업데이트됩니다.             |
| `number`  | `int`  | `5`    | 표시할 총 별(아이콘)의 개수. 즉, 최대 평점 값입니다.                                       |
| `size`    | `int`  | `18`   | 각 별(아이콘)의 크기 (픽셀 단위).                                                        |
| `spacing` | `int`  | `4`    | 각 별 아이템 내부의 여백. 아이콘 주변의 클릭 가능한 영역에 영향을 줄 수 있습니다 (아이콘 간 간격 아님). |

### 고유 시그널

*   `value` 프로퍼티 값이 변경될 때 암시적으로 `onValueChanged` 시그널 핸들러를 사용할 수 있습니다.

### 고유 메소드

`FluRatingControl` 자체에 고유한 메소드는 정의되어 있지 않습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 15

    FluText { text: "기본 평점 컨트롤 (5개 별):" }
    FluRatingControl {
        id: ratingControl1
        onValueChanged: {
            console.log("평점 1 선택됨:", value)
        }
    }

    FluText { text: qsTr("10개 별 평점 컨트롤 (크기 조정):") }
    FluRatingControl {
        id: ratingControl2
        number: 10
        size: 24 // 아이콘 크기 변경
        value: 3 // 초기 값 설정
        onValueChanged: {
            console.log("평점 2 선택됨:", value)
        }
    }
    
    FluText { text: qsTr("현재 평점: %1 / %2").arg(ratingControl2.value).arg(ratingControl2.number) }
}
```

### 참고 사항

*   **상호작용**: 사용자가 마우스를 컨트롤 위로 가져가면 마우스 포인터 위치까지의 별들이 채워진 상태로 미리 표시됩니다. 마우스를 클릭하면 해당 위치까지의 별 개수가 `value` 프로퍼티 값으로 설정됩니다. 마우스가 컨트롤 영역을 벗어나면 실제 `value` 값에 해당하는 별들만 채워진 상태로 돌아갑니다.
*   **아이콘 및 색상**: 기본적으로 선택되지 않은 별은 `FluentIcons.FavoriteStar` 아이콘을, 선택된(채워진) 별은 `FluentIcons.FavoriteStarFill` 아이콘을 사용합니다. 선택된 별의 색상은 `FluTheme.primaryColor`를 따르며, 선택되지 않은 별의 색상은 현재 테마(밝은/어두운)에 따라 결정됩니다.
*   **레이아웃**: 내부는 `Row` 레이아웃과 `Repeater`를 사용하여 별 아이콘들을 수평으로 배치합니다. 컴포넌트의 전체 크기는 `number`, `size`, `spacing` 프로퍼티에 따라 자동으로 결정됩니다. 