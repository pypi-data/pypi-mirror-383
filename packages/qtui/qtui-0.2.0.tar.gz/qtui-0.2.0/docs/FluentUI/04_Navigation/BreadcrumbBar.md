# Fluent UI 브레드크럼 바 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluBreadcrumbBar` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 계층 구조 내에서 현재 위치를 파악하고 이전 단계로 이동할 수 있도록 도와주는 탐색 경로를 표시합니다.

## 공통 임포트 방법

Fluent UI 브레드크럼 바 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Layouts, Controls 등 추가
import QtQuick.Layouts 1.15 
import QtQuick.Controls 2.15
```

---

## FluBreadcrumbBar

`FluBreadcrumbBar`는 현재 사용자의 위치까지의 탐색 경로를 일련의 클릭 가능한 링크(항목)로 표시하는 컨트롤입니다. 각 항목은 계층 구조의 한 단계를 나타내며, 지정된 구분 기호로 분리됩니다. 사용자는 이전 항목을 클릭하여 상위 단계로 쉽게 이동할 수 있습니다. 이 컴포넌트는 `Item`을 기반으로 하며, 내부에 항목들을 가로로 배열하는 `ListView`를 포함합니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름        | 타입        | 기본값   | 설명                                                                                                                                |
| :---------- | :---------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `items`     | `var`       | `[]`     | 브레드크럼 항목들의 데이터 모델 역할을 하는 JavaScript 객체 배열입니다. 각 객체는 반드시 `title` (표시될 텍스트) 프로퍼티를 가져야 합니다. 이 프로퍼티가 변경되면 내부 `ListModel`이 해당 내용으로 업데이트됩니다. |
| `separator` | `string`    | `/`      | 브레드크럼 항목들 사이에 표시될 구분 기호 문자열입니다.                                                                                |
| `spacing`   | `int`       | `5`      | 각 항목 내에서 텍스트와 구분 기호 사이의 간격, 그리고 `ListView`에서 항목 간의 간격입니다.                                                         |
| `textSize`  | `int`       | `15`     | 구분 기호(`separator`) 텍스트의 픽셀 크기입니다. 항목 자체의 텍스트 크기는 내부 `FluText`의 기본값을 따릅니다.                                        |

### 고유 시그널

| 이름        | 파라미터         | 반환타입 | 설명                                                                                                                                                                 |
| :---------- | :--------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `clickItem` | `var`: `model` | -        | 브레드크럼 항목 중 하나가 클릭되었을 때 발생하는 시그널입니다. 클릭된 항목에 해당하는 모델 데이터 객체(즉, `items` 배열의 요소)가 `model` 파라미터로 전달됩니다. 이 `model` 객체에는 해당 항목의 인덱스 정보(`model.index`)도 포함되어 있습니다. | 

### 고유 메소드

| 이름     | 파라미터                 | 반환타입 | 설명                                                                            |
| :------- | :----------------------- | :------- | :------------------------------------------------------------------------------ |
| `remove` | `int`: `index`, `int`: `count` | `void`   | 지정된 `index`부터 `count` 개수만큼의 항목을 브레드크럼 바(내부 `ListModel`)에서 제거합니다. |
| `count`  | 없음                     | `int`    | 현재 브레드크럼 바에 있는 항목의 총 개수를 반환합니다.                                       |

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 15
    width: 400

    Component.onCompleted: {
        // 초기 브레드크럼 항목 설정
        var initialItems = [
            { title: "문서", path: "/Documents" },
            { title: "프로젝트", path: "/Documents/Projects" },
            { title: "FluentUI", path: "/Documents/Projects/FluentUI" }
        ]
        breadcrumbBar.items = initialItems
    }

    FluBreadcrumbBar {
        id: breadcrumbBar
        Layout.fillWidth: true
        separator: ">" // 구분 기호 변경
        spacing: 8     // 간격 조정

        // 항목 클릭 시 처리: 클릭된 항목 이후의 모든 항목 제거 (상위 경로로 이동)
        onClickItem: (model) => {
            console.log("Clicked:", model.title, "at index:", model.index, "path:", model.path)
            var currentIndex = model.index
            var totalCount = breadcrumbBar.count()
            if (currentIndex + 1 < totalCount) {
                breadcrumbBar.remove(currentIndex + 1, totalCount - (currentIndex + 1))
            }
            // 여기에 실제 경로 이동 로직 추가 (예: model.path 사용)
        }
    }

    // 예시: 하위 경로 추가 버튼
    FluButton {
        text: qsTr("하위 폴더 추가")
        onClicked: {
            var currentItems = breadcrumbBar.items
            var newItem = { title: "새 폴더 " + (currentItems.length + 1), path: breadcrumbBar.items[currentItems.length-1].path + "/NewFolder"}
            currentItems.push(newItem)
            breadcrumbBar.items = currentItems // items 업데이트하여 추가
        }
    }
}
```

### 참고 사항

*   **데이터 모델**: `items` 프로퍼티에 JavaScript 객체 배열을 할당하여 브레드크럼 내용을 설정합니다. 각 객체는 `title` 외에도 경로 정보(`path`) 등 필요한 데이터를 포함할 수 있으며, 이 데이터는 `clickItem` 시그널 핸들러에서 `model` 파라미터를 통해 접근 가능합니다.
*   **탐색 구현**: `clickItem` 시그널 핸들러 내에서 `model.index`와 `count()` 메소드를 사용하여 현재 클릭된 항목의 위치를 파악하고, `remove()` 메소드를 호출하여 클릭된 항목 이후의 항목들을 제거하는 방식으로 상위 단계로의 탐색을 구현하는 것이 일반적입니다.
*   **동적 업데이트**: `items` 프로퍼티에 새 배열을 할당하면 브레드크럼 바의 내용이 업데이트됩니다. 하위 경로로 이동할 때는 기존 배열에 새 항목 객체를 추가(`push`)한 후 업데이트된 배열을 다시 `items`에 할당합니다.
*   **스타일링**: 항목 텍스트의 마우스 호버 및 눌림 상태에 따른 색상 변화는 내부 `delegate`에 구현되어 있으며, `FluTheme`을 따릅니다. `separator`, `spacing`, `textSize` 프로퍼티를 통해 기본적인 모양을 커스터마이징할 수 있습니다.
*   **스크롤**: 항목들의 총 너비가 `FluBreadcrumbBar`의 너비를 초과할 경우, 내장된 `ListView`가 자동으로 스크롤 기능을 제공하지는 않습니다 (기본 `boundsBehavior`는 `ListView.StopAtBounds`). 매우 긴 경로가 예상될 경우 스크롤 가능한 컨테이너(예: `ScrollView`) 안에 배치하는 것을 고려할 수 있습니다. 