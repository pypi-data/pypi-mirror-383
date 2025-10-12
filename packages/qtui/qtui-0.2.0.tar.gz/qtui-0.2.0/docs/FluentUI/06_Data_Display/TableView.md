# Fluent UI 테이블 뷰 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTableView` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 행과 열로 구성된 데이터를 표시하고 사용자와 상호작용하는 데 사용되는 강력하고 유연한 컨트롤입니다.

## 공통 임포트 방법

Fluent UI 테이블 뷰 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
import Qt.labs.qmlmodels 1.0 // TableView, TableModel 등 사용
// 필요에 따라 Layouts, Controls 등 추가
import QtQuick.Layouts 1.15 
import QtQuick.Controls 2.15
```

---

## FluTableView

`FluTableView`는 대량의 데이터를 효율적으로 표시하기 위한 표 형태의 컨트롤입니다. Qt Quick의 `TableView`를 기반으로 하며, 다음과 같은 다양한 기능을 제공합니다:

*   **열 정의**: 각 열의 제목, 데이터 매핑, 너비, 고정 여부 등을 유연하게 정의할 수 있습니다.
*   **데이터 바인딩**: JavaScript 객체 배열 형태의 `dataSource` 또는 표준 `TableModel` 기반의 `sourceModel`을 사용하여 데이터를 표시합니다.
*   **정렬 및 필터링**: 사용자 정의 로직을 통해 데이터를 정렬하거나 필터링할 수 있습니다.
*   **사용자 정의 렌더링**: `customItem` 메소드를 사용하여 특정 셀이나 헤더를 사용자 정의 QML 컴포넌트로 렌더링할 수 있습니다.
*   **인라인 편집**: 셀을 더블 클릭하여 내용을 편집할 수 있으며, 기본 편집기 외에 사용자 정의 편집 컴포넌트(`editDelegate`)를 지정할 수 있습니다.
*   **고정 열(Frozen Columns)**: 특정 열을 왼쪽에 고정시켜 가로 스크롤 시에도 항상 보이도록 할 수 있습니다.
*   **헤더 및 스타일**: 가로/세로 헤더 표시 여부를 제어하고, 선택된 행의 스타일을 지정할 수 있습니다.
*   **스크롤 및 성능**: 내부적으로 `TableView`의 가상화 기술을 활용하여 많은 행의 데이터를 효율적으로 처리합니다.

### 기반 클래스

`Rectangle` (내부적으로 `TableView`와 `FluTableModel`, `FluTableSortProxyModel` 등 활용)

### 데이터 소스 구조 (`dataSource`)

`dataSource` 프로퍼티에는 행 데이터를 담은 JavaScript 객체 배열을 할당합니다. 각 객체는 하나의 행을 나타내며, 객체의 키(key)는 `columnSource`에서 정의한 `dataIndex`와 일치해야 합니다.

*   **`columnSource`의 `dataIndex` 키**: 해당 열에 표시될 데이터 값입니다.
*   **`_key`**: (선택 사항, 권장) 각 행을 고유하게 식별하는 키입니다. 정렬, 필터링, 선택 상태 유지 등에 사용됩니다.
*   **`height`, `_minimumHeight`, `_maximumHeight`**: (선택 사항) 특정 행의 높이를 개별적으로 제어할 때 사용합니다.

```javascript
// dataSource 예시
[
  { _key: "row1", id: 1, name: "Alice", age: 30, city: "Seoul" },
  { _key: "row2", id: 2, name: "Bob", age: 25, city: "Busan", height: 50 }, // 특정 행 높이 지정
  { _key: "row3", id: 3, name: "Charlie", age: 35, city: "Incheon" }
]
```

### 열 정의 (`columnSource`)

`columnSource` 프로퍼티는 테이블의 열 구조를 정의하는 객체 배열입니다. 각 열 객체는 다음 프로퍼티를 가질 수 있습니다:

*   `title`: `string` 또는 `Component` - 헤더에 표시될 제목. `customItem()`을 사용하여 컴포넌트로 지정하면 사용자 정의 헤더 구현 가능.
*   `dataIndex`: `string` - `dataSource` 객체에서 이 열의 데이터에 해당하는 키.
*   `width`: `int` (선택 사항) - 열의 기본 너비.
*   `minimumWidth`, `maximumWidth`: `int` (선택 사항) - 열 너비 조절 시 최소/최대 한계.
*   `frozen`: `bool` (선택 사항) - `true`로 설정하면 해당 열이 왼쪽에 고정됩니다.
*   `editDelegate`: `Component` (선택 사항) - 셀 편집 시 사용할 사용자 정의 컴포넌트.
*   `editMultiline`: `bool` (선택 사항) - 기본 편집기 사용 시 여러 줄 입력 허용 여부.
*   `readOnly`: `bool` (선택 사항) - 셀 편집 불가 여부.

```javascript
// columnSource 예시
[
  { title: "ID", dataIndex: 'id', width: 50, frozen: true }, // 고정 열
  { title: table_view.customItem(com_column_filter_name, { title:"이름" }), dataIndex: 'name', width: 150 }, // 사용자 정의 헤더
  { title: "나이", dataIndex: 'age', width: 80, editDelegate: com_number_editor }, // 사용자 정의 편집기
  { title: "도시", dataIndex: 'city', width: 120, readOnly: true } // 읽기 전용
]
```

### 고유/특징적 프로퍼티

| 이름                      | 타입            | 기본값                   | 설명                                                                                                                             |
| :------------------------ | :-------------- | :----------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `sourceModel`             | `TableModel`    | (내부 `FluTableModel`)   | 테이블의 원본 데이터 모델. 기본 모델 대신 사용자 정의 `TableModel`을 지정할 수 있습니다.                                                            |
| `dataSource`              | `var`           | (없음)                 | JavaScript 객체 배열 형태의 데이터 소스. `sourceModel`이 기본 `FluTableModel`일 때 사용됩니다. 변경 시 테이블 내용이 업데이트됩니다.                          |
| `columnSource`            | `var` (배열)    | `[]`                   | 테이블 열 구조를 정의하는 객체 배열.                                                                                              |
| `horizonalHeaderVisible`  | `bool`          | `true`                 | 가로(열) 헤더 표시 여부.                                                                                                   |
| `verticalHeaderVisible`   | `bool`          | `true`                 | 세로(행 번호) 헤더 표시 여부.                                                                                               |
| `selectedBorderColor`     | `color`         | (테마 기반 `primaryColor`) | 현재 선택된 행의 테두리 색상.                                                                                               |
| `selectedColor`           | `color`         | (테마 기반 투명도 적용 색상) | 현재 선택된 행의 배경색.                                                                                                    |
| `view`                    | `readonly alias`| (내부 `TableView`)     | 내부 `TableView` 인스턴스에 대한 참조.                                                                                         |
| `columnWidthProvider`     | `function`      | (내부 함수)              | `columnSource` 정의에 따라 열 너비를 반환하는 함수.                                                                                |
| `rowHeightProvider`       | `function`      | (내부 함수)              | `dataSource` 객체의 `height` 관련 프로퍼티 또는 기본값에 따라 행 높이를 반환하는 함수.                                                        |
| `current`                 | `readonly alias`| (없음)                 | 현재 선택된 행의 데이터 객체 (`rowModel`). `onCurrentChanged`로 변경 감지 가능.                                                                 |

### 고유 메소드

| 이름           | 파라미터                                           | 반환타입     | 설명                                                                                                                               |
| :------------- | :------------------------------------------------- | :----------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `customItem`   | `Component`: `comId`, `var`: `options` (기본값 `{}`) | `object`     | 사용자 정의 셀 또는 헤더 렌더링을 위한 객체를 생성합니다. `dataSource`나 `columnSource`의 `title`에 사용됩니다.                                        |
| `sort`         | `function`: `callback` (선택 사항)                 | `void`       | 사용자 정의 비교 함수(`callback(leftRowData, rightRowData)`)를 사용하여 테이블을 정렬합니다. 콜백이 없으면 정렬을 해제합니다.                                |
| `filter`       | `function`: `callback` (선택 사항)                 | `void`       | 사용자 정의 필터 함수(`callback(rowData)`)를 사용하여 테이블을 필터링합니다. 콜백이 없으면 필터를 해제합니다.                                       |
| `setRow`       | `int`: `rowIndex`, `object`: `obj`                 | `void`       | 지정된 행 인덱스(`rowIndex`)의 데이터를 `obj`로 업데이트합니다. (화면에 보이는 행 기준)                                                                  |
| `getRow`       | `int`: `rowIndex`                                | `object`     | 지정된 행 인덱스(`rowIndex`)의 데이터 객체를 반환합니다. (화면에 보이는 행 기준)                                                                   |
| `removeRow`    | `int`: `rowIndex`, `int`: `rows` (기본값 `1`)      | `void`       | 지정된 행 인덱스(`rowIndex`)부터 `rows` 개수만큼 행을 제거합니다. (화면에 보이는 행 기준)                                                              |
| `insertRow`    | `int`: `rowIndex`, `object`: `obj`                 | `void`       | 지정된 행 인덱스(`rowIndex`) 앞에 `obj` 데이터를 삽입합니다. (기본 `FluTableModel` 사용 시, 원본 데이터 기준 인덱스)                                       |
| `appendRow`    | `object`: `obj`                                    | `void`       | 테이블 끝에 `obj` 데이터를 추가합니다. (기본 `FluTableModel` 사용 시)                                                                           |
| `currentIndex`   | 없음                                               | `int`        | 현재 선택된 행의 원본 `sourceModel`에서의 인덱스를 반환합니다. 선택된 항목이 없으면 -1을 반환합니다.                                                           |
| `closeEditor`  | 없음                                               | `void`       | 현재 열려 있는 셀 편집기를 닫습니다.                                                                                                    |
| `resetPosition`| 없음                                               | `void`       | 테이블 뷰의 스크롤 위치를 맨 위, 맨 왼쪽으로 초기화합니다.                                                                                     |

### 사용자 정의 셀/헤더 및 편집

*   **사용자 정의 렌더링**: `dataSource`의 특정 셀 값이나 `columnSource`의 `title` 값으로 `customItem(componentId, options)`가 반환하는 객체를 지정하면, 해당 셀/헤더는 `componentId`로 지정된 `Component`를 사용하여 렌더링됩니다. `options` 객체는 컴포넌트 내에서 `options` 프로퍼티로 접근하여 데이터를 전달받는 데 사용됩니다.
*   **사용자 정의 편집**: `columnSource`의 열 객체에 `editDelegate` 프로퍼티로 사용자 정의 `Component`를 지정하면, 해당 열의 셀을 더블 클릭했을 때 지정된 컴포넌트가 편집기로 나타납니다. 편집기 컴포넌트는 `display` 프로퍼티로 초기값을 받고, `editTextChaged(newText)` 시그널을 발생시켜 변경된 값을 `FluTableView`에 전달해야 합니다.

### 정렬 및 필터링

내부적으로 `FluTableSortProxyModel`을 사용하여 정렬 및 필터링 기능을 제공합니다.
*   `sort(callback)`: 비교 함수 `callback(leftRow, rightRow)`을 제공하여 정렬 로직을 정의합니다. 콜백은 `leftRow`가 `rightRow`보다 앞에 와야 하면 음수, 같으면 0, 뒤에 와야 하면 양수를 반환해야 합니다.
*   `filter(callback)`: 필터 함수 `callback(row)`을 제공하여 필터링 로직을 정의합니다. 콜백은 해당 행(`row`)을 표시해야 하면 `true`, 숨겨야 하면 `false`를 반환해야 합니다.

### 고정 열 (Frozen Columns)

`columnSource` 정의에서 열 객체에 `frozen: true`를 설정하면 해당 열은 테이블 왼쪽에 고정됩니다. 이후 열들은 가로 스크롤 시 고정 열 아래로 이동합니다. 고정 열 기능은 내부적으로 별도의 `TableView` 인스턴스를 사용하여 구현됩니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0
import Qt.labs.qmlmodels 1.0

FluContentPage {
    title: qsTr("TableView 예제")

    // 사용자 정의 컴포넌트 (예: 체크박스, 액션 버튼)
    Component { id: com_checkbox /* ... */ }
    Component { id: com_action /* ... */ }
    Component { id: com_column_filter_name /* ... */ } // 필터 버튼 포함 헤더
    Component { id: com_column_sort_age /* ... */ }    // 정렬 버튼 포함 헤더
    Component { id: com_age_editor /* ... */ }         // 사용자 정의 나이 편집기

    // 정렬 상태 관리 변수
    property int ageSortOrder: 0 // 0: none, 1: asc, 2: desc

    // 필터링 키워드
    property string nameKeyword: ""

    FluTableView {
        id: tableView
        anchors.fill: parent
        anchors.topMargin: 60 // 컨트롤 영역 아래

        // 열 정의 (고정열, 사용자 정의 헤더/셀, 편집기 포함)
        columnSource: [
            {
                title: tableView.customItem(com_column_checkbox_header, { checked: selectAllCheckbox.checked }),
                dataIndex: 'checkboxData',
                width: 50,
                frozen: true // 체크박스 열 고정
            },
            {
                title: tableView.customItem(com_column_filter_name, { title: qsTr("이름") }),
                dataIndex: 'name',
                width: 150,
                readOnly: true
            },
            {
                title: tableView.customItem(com_column_sort_age, { title: qsTr("나이"), sortOrder: ageSortOrder }),
                dataIndex: 'age',
                width: 100,
                editDelegate: com_age_editor
            },
            { title: qsTr("주소"), dataIndex: 'address', width: 250, editMultiline: true },
            {
                title: qsTr("액션"),
                dataIndex: 'actionData', // dataSource에 customItem(com_action) 지정
                width: 120
            }
        ]

        // 데이터 초기화 (예시)
        Component.onCompleted: {
            var initialData = []
            for (var i = 1; i <= 50; ++i) {
                initialData.push({
                    _key: "item" + i,
                    checkboxData: tableView.customItem(com_checkbox, { checked: false }),
                    name: "사용자 " + i,
                    age: 20 + Math.floor(Math.random() * 40),
                    address: "도시 " + (i % 5 + 1),
                    actionData: tableView.customItem(com_action)
                })
            }
            dataSource = initialData
        }

        // 현재 항목 변경 시 로그
        onCurrentChanged: {
            if (current) console.log("Current item key:", current._key)
        }
    }

    // 컨트롤 영역 (정렬, 필터, 추가 등)
    RowLayout {
        anchors { top: parent.top; left: parent.left; right: parent.right; margins: 10 }
        spacing: 10
        FluCheckBox { id: selectAllCheckbox; text: "전체 선택/해제"; /* ... 로직 구현 ... */ }
        FluButton {
            text: ageSortOrder === 1 ? "나이 ▲" : (ageSortOrder === 2 ? "나이 ▼" : "나이 정렬")
            onClicked: {
                ageSortOrder = (ageSortOrder + 1) % 3
                if (ageSortOrder === 0) tableView.sort() // 정렬 해제
                else if (ageSortOrder === 1) tableView.sort((l, r) => l.age - r.age) // 오름차순
                else tableView.sort((l, r) => r.age - l.age) // 내림차순
            }
        }
        FluTextBox {
            id: nameFilterInput
            placeholderText: "이름 필터..."
            onAccepted: {
                nameKeyword = text
                if (text === "") tableView.filter() // 필터 해제
                else tableView.filter(item => item.name.includes(text))
            }
        }
        FluButton { text: "행 추가"; onClicked: { /* tableView.appendRow(...) */ } }
        FluButton { text: "선택 행 삭제"; onClicked: { /* tableView.removeRow(...) */ } }
    }
}
```

### 참고 사항

*   **`_key` 사용**: `dataSource`의 각 행 객체에 고유한 `_key`를 제공하면 선택, 정렬, 필터링 시 행 식별이 더 안정적입니다.
*   **모델 인덱스 vs 뷰 인덱스**: `getRow`, `setRow`, `removeRow` 등의 메소드는 현재 화면에 보이는 행의 인덱스를 사용합니다. 정렬이나 필터링이 적용된 경우 이는 원본 `sourceModel`의 인덱스와 다를 수 있습니다. `currentIndex()` 메소드는 원본 모델 인덱스를 반환합니다.
*   **대규모 데이터**: `FluTableView`는 내부적으로 `TableView`의 행/열 가상화를 사용하여 대량의 데이터를 효율적으로 처리하도록 설계되었습니다.
*   **내부 모델**: 기본적으로 `FluTableView`는 `FluTableModel`과 정렬/필터링을 위한 `FluTableSortProxyModel`을 내부적으로 사용합니다. `sourceModel` 프로퍼티를 통해 사용자 정의 모델을 주입할 수도 있습니다. 