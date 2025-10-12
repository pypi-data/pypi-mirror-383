# Fluent UI 트리 뷰 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluTreeView` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 계층적인 데이터를 테이블 형식으로 표시하고 조작하는 데 사용됩니다.

## 공통 임포트 방법

Fluent UI 트리 뷰 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Layouts, Controls, Qt.labs.qmlmodels 등 추가
import QtQuick.Layouts 1.15 
import QtQuick.Controls 2.15
import Qt.labs.qmlmodels 1.0 // TableView, TableModel 등 사용 시
```

---

## FluTreeView

`FluTreeView`는 트리 구조의 데이터를 표 형태로 보여주는 컨트롤입니다. 각 행은 하나의 노드를 나타내며, 들여쓰기를 통해 계층 구조를 시각적으로 표현합니다. 사용자는 노드 옆의 아이콘을 클릭하여 하위 노드를 펼치거나 접을 수 있습니다. 열(Column) 정의, 행 높이 조절, 계층 구조 선 표시, 체크박스 표시, 셀 편집, 사용자 정의 셀 렌더링 등 다양한 기능을 제공합니다. 내부적으로 Qt Quick의 `TableView`와 커스텀 모델인 `FluTreeModel`을 사용하여 구현되었습니다.

### 기반 클래스

`Rectangle` (내부적으로 `TableView` 사용)

### 데이터 소스 구조 (`dataSource`)

`FluTreeView`는 `dataSource` 프로퍼티를 통해 데이터를 받습니다. 이 프로퍼티에는 JavaScript 객체 배열을 할당해야 합니다. 각 객체는 트리 노드 하나를 나타내며 다음과 같은 구조를 가질 수 있습니다:

*   **`columnSource`의 `dataIndex`에 해당하는 키**: 각 열에 표시될 데이터를 정의합니다. (예: `title: "노드 제목"`, `name: "홍길동"`)
*   **`_key`**: 각 노드를 고유하게 식별하기 위한 내부 키입니다. 제공하지 않으면 자동으로 생성될 수 있으나, 안정적인 식별을 위해 고유한 값을 제공하는 것이 좋습니다.
*   **`children`**: `array` (선택 사항) - 이 노드의 하위 노드 객체들을 담는 배열입니다. 이 배열이 존재하면 해당 노드는 확장/축소 가능한 부모 노드가 됩니다.
*   **`isExpanded`**: `bool` (선택 사항) - 이 노드가 초기에 확장된 상태로 표시될지 여부를 지정합니다.

```javascript
// dataSource 예시
[
  {
    _key: "node-1",
    title: "문서",
    author: "김철수",
    children: [
      { _key: "node-1-1", title: "보고서.docx", author: "이영희", isExpanded: true },
      { 
        _key: "node-1-2", 
        title: "이미지", 
        author: "박민지",
        children: [
          { _key: "node-1-2-1", title: "풍경.jpg", author: "김철수" }
        ]
      }
    ]
  },
  { _key: "node-2", title: "다운로드", author: "관리자" }
]
```

### 열 정의 (`columnSource`)

테이블의 열 구조는 `columnSource` 프로퍼티를 통해 정의합니다. 이 프로퍼티에는 각 열을 설명하는 객체 배열을 할당합니다. 각 열 객체는 다음과 같은 프로퍼티를 가질 수 있습니다:

*   `title`: `string` - 테이블 헤더에 표시될 열의 제목.
*   `dataIndex`: `string` - `dataSource` 객체에서 이 열에 해당하는 데이터 값의 키(key).
*   `width`: `int` (선택 사항) - 열의 기본 너비 (픽셀 단위).
*   `minimumWidth`: `int` (선택 사항) - 열의 최소 너비. 사용자가 너비를 조절할 때 이 값 미만으로 줄일 수 없습니다.
*   `maximumWidth`: `int` (선택 사항) - 열의 최대 너비.
*   `editDelegate`: `Component` (선택 사항) - 해당 열의 셀을 더블 클릭했을 때 내용을 편집하기 위한 사용자 정의 컴포넌트. 지정하지 않으면 기본 `FluTextBox`가 사용됩니다.
*   `editMultiline`: `bool` (선택 사항) - 기본 편집기 사용 시 여러 줄 입력(`TextArea`)을 허용할지 여부 (기본값 `false`).
*   `readOnly`: `bool` (선택 사항) - 해당 열의 편집 가능 여부 (기본값 `false`).

```javascript
// columnSource 예시
[
  { title: "제목", dataIndex: 'title', width: 300 },
  { title: "작성자", dataIndex: 'author', width: 100 },
  { title: "상태", dataIndex: 'status', minimumWidth: 80, readOnly: true },
  { title: "편집 가능", dataIndex: 'editableContent', editMultiline: true }
]
```

### 고유/특징적 프로퍼티

| 이름                  | 타입            | 기본값                 | 설명                                                                                                                             |
| :-------------------- | :-------------- | :--------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `dataSource`          | `var`           | (없음)                 | 트리의 계층 구조 데이터를 나타내는 JavaScript 객체 배열. 변경 시 트리가 업데이트됩니다.                                                                |
| `columnSource`        | `var` (배열)    | `[]`                   | 테이블의 열 구조를 정의하는 객체 배열.                                                                                              |
| `showLine`            | `bool`          | `true`                 | 트리 계층 구조를 나타내는 선(line) 표시 여부를 결정합니다.                                                                                 |
| `cellHeight`          | `int`           | `30`                   | 각 행(셀)의 높이를 픽셀 단위로 지정합니다.                                                                                             |
| `depthPadding`        | `int`           | `15`                   | 트리 계층의 깊이(depth) 당 적용될 들여쓰기 간격(픽셀 단위)입니다.                                                                                |
| `checkable`           | `bool`          | `false`                | 각 행 앞에 체크박스를 표시할지 여부를 결정합니다.                                                                                            |
| `lineColor`           | `color`         | (테마 기반 `dividerColor`) | 계층 구조 선의 색상입니다.                                                                                                     |
| `borderColor`         | `color`         | (테마 기반 색상)         | 테이블 헤더 및 그리드 선의 색상입니다.                                                                                              |
| `selectedBorderColor` | `color`         | (테마 기반 `primaryColor`) | 현재 선택된 행의 테두리 색상입니다.                                                                                               |
| `selectedColor`       | `color`         | (테마 기반 투명도 적용 색상) | 현재 선택된 행의 배경색입니다.                                                                                                    |
| `current`             | `readonly alias`| (없음)                 | 현재 선택된 행의 모델 데이터 객체 (`FluTreeModel`의 `rowModel`)에 대한 읽기 전용 별칭입니다. `onCurrentChanged` 시그널 핸들러를 통해 변경을 감지할 수 있습니다. |
| `view`                | `readonly alias`| (내부 `TableView`)     | 내부적으로 사용되는 `TableView` 인스턴스에 대한 읽기 전용 별칭입니다. 스크롤 위치 등 `TableView`의 프로퍼티에 접근할 때 사용할 수 있습니다.                              |

### 고유 메소드

| 이름           | 파라미터                               | 반환타입     | 설명                                                                                                                               |
| :------------- | :------------------------------------- | :----------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `collapse`     | `int`: `rowIndex`                    | `void`       | 화면에 보이는 행의 인덱스(`rowIndex`)에 해당하는 노드를 축소합니다 (하위 노드를 숨김).                                                                    |
| `expand`       | `int`: `rowIndex`                    | `void`       | 화면에 보이는 행의 인덱스(`rowIndex`)에 해당하는 노드를 확장합니다 (하위 노드를 표시).                                                                    |
| `allExpand`    | 없음                                   | `void`       | 트리의 모든 노드를 확장합니다.                                                                                                        |
| `allCollapse`  | 없음                                   | `void`       | 트리의 모든 노드를 축소합니다 (최상위 레벨 노드 제외).                                                                                              |
| `customItem`   | `Component`: `comId`, `var`: `options` (기본값 `{}`) | `object`     | 특정 셀을 사용자 정의 컴포넌트(`comId`)로 렌더링하기 위한 헬퍼 객체를 생성합니다. `options` 객체를 통해 컴포넌트에 데이터를 전달할 수 있습니다. 이 객체를 `dataSource`의 해당 셀 값으로 지정합니다. |
| `closeEditor`  | 없음                                   | `void`       | 현재 열려 있는 셀 편집기를 닫습니다.                                                                                                    |
| `selectionModel` | 없음                                   | `list<object>` | `checkable`이 `true`일 때, 현재 체크된 모든 항목의 모델 데이터 객체(`rowModel.data`)를 배열 형태로 반환합니다.                                                |
| `count`        | 없음                                   | `int`        | `dataSource`에 포함된 전체 노드의 개수 (숨겨진 하위 노드 포함)를 반환합니다.                                                                       |
| `visibleCount` | 없음                                   | `int`        | 현재 화면에 보이는 행(row)의 개수를 반환합니다.                                                                                             |

### 사용자 정의 셀 렌더링 및 편집

*   **렌더링**: 특정 셀의 내용을 기본 텍스트가 아닌 사용자 정의 QML 컴포넌트로 표시하려면, `dataSource`의 해당 위치에 `customItem(componentId, { key: value, ... })` 메소드가 반환하는 객체를 값으로 지정합니다. `componentId`는 사용할 `Component`의 ID이며, `options` 객체는 해당 컴포넌트에 전달될 데이터입니다. 컴포넌트 내에서는 `options`라는 이름의 프로퍼티로 이 데이터에 접근할 수 있습니다.
*   **편집**: 사용자가 셀을 더블 클릭하면 편집 모드로 진입합니다. 기본적으로 `FluTextBox` 또는 `FluMultilineTextBox`(열 속성 `editMultiline: true` 설정 시)가 편집기로 사용됩니다. `columnSource`에서 열 객체의 `editDelegate` 프로퍼티에 사용자 정의 `Component`를 지정하여 편집기를 교체할 수 있습니다. 편집기 컴포넌트 내에서는 `display` 프로퍼티를 통해 초기값을 받고, `commit()` 또는 `editTextChaged(newText)` 시그널을 통해 변경된 값을 `FluTreeView`에 알릴 수 있습니다. `readOnly: true`로 설정된 열은 편집할 수 없습니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0
import Qt.labs.qmlmodels 1.0

FluContentPage {
    title: qsTr("TreeView 예제")

    // 사용자 정의 아바타 컴포넌트
    Component {
        id: avatarComponent
        Item {
            FluClip {
                anchors.centerIn: parent
                width: parent.height * 0.8
                height: parent.height * 0.8
                radius: [height / 2, height / 2, height / 2, height / 2]
                Image {
                    anchors.fill: parent
                    source: options.avatarUrl // options 객체 사용
                    fillMode: Image.PreserveAspectCrop
                }
            }
        }
    }

    // 트리 데이터 생성 함수 (예시)
    function generateTreeData() { /* ... */ }

    // 트리 뷰 정의
    FluTreeView {
        id: treeView
        anchors.fill: parent
        anchors.topMargin: 80 // 컨트롤 영역 아래
        
        checkable: checkSwitch.checked // 체크박스 표시 여부 바인딩
        showLine: lineSwitch.checked     // 라인 표시 여부 바인딩
        cellHeight: heightSlider.value // 셀 높이 바인딩
        depthPadding: paddingSlider.value // 들여쓰기 간격 바인딩
        
        // 열 정의
        columnSource: [
            { title: "파일/폴더명", dataIndex: 'title', width: 300 },
            { title: "소유자", dataIndex: 'owner', width: 100 },
            {
                title: "아이콘",
                dataIndex: 'iconData', // dataSource에 customItem() 반환값 저장
                width: 80
            },
            { title: "크기(KB)", dataIndex: 'size', width: 100, readOnly: true } // 읽기 전용 열
        ]

        // 데이터 소스 초기화
        Component.onCompleted: {
            var data = generateTreeData() // 실제 데이터 생성 로직 필요
            // 예시: 첫 번째 노드의 아이콘 셀에 커스텀 아이템 지정
            if (data.length > 0 && data[0].children.length > 0) {
                data[0].children[0].iconData = treeView.customItem(avatarComponent, { avatarUrl: "qrc:/example/res/svg/avatar_1.svg" })
            }
            dataSource = data
        }

        // 현재 선택된 항목 변경 시 로그 출력
        onCurrentChanged: {
            if (current) {
                console.log("선택됨:", current.data.title)
            }
        }
    }

    // 컨트롤 영역 (예시)
    RowLayout {
        anchors { top: parent.top; left: parent.left; right: parent.right; margins: 10 }
        spacing: 15
        FluToggleSwitch { id: checkSwitch; text: "체크박스" }
        FluToggleSwitch { id: lineSwitch; text: "라인 표시"; checked: true }
        FluSlider { id: heightSlider; from: 25; to: 50; value: 30; Layout.minimumWidth: 100 }
        FluLabel { text: "셀 높이: " + heightSlider.value.toFixed(0) }
        FluSlider { id: paddingSlider; from: 10; to: 40; value: 15; Layout.minimumWidth: 100 }
        FluLabel { text: "들여쓰기: " + paddingSlider.value.toFixed(0) }
        FluButton { text: "전체 펼치기"; onClicked: treeView.allExpand() }
        FluButton { text: "전체 접기"; onClicked: treeView.allCollapse() }
        FluButton {
            text: "선택된 항목 확인"
            visible: checkSwitch.checked
            onClicked: {
                var selected = treeView.selectionModel()
                console.log("체크된 항목 개수:", selected.length)
                selected.forEach(item => console.log("- " + item.title))
            }
        }
    }
}
```

### 참고 사항

*   **`_key` 프로퍼티**: `dataSource` 내 각 노드 객체에 고유한 `_key` 값을 지정하는 것이 좋습니다. 이는 노드 식별 및 상태 관리(확장/축소, 체크 상태 등)에 사용됩니다.
*   **성능**: 매우 많은 수의 노드를 표시할 경우 성능에 영향을 줄 수 있습니다. 데이터 로딩 및 모델 업데이트 최적화가 필요할 수 있습니다. 내부적으로 `TableView`를 사용하여 가상 스크롤링을 활용하므로 보이는 영역만 렌더링하여 기본적인 성능은 확보됩니다.
*   **`FluTreeModel`**: 데이터 관리, 계층 구조 처리, 확장/축소, 체크 상태 관리는 내부 `FluTreeModel`에서 담당합니다. 일반적으로 직접 상호작용할 필요는 없지만, `FluTreeView`의 동작 방식을 이해하는 데 도움이 됩니다.
*   **선택 상태**: `current` 프로퍼티는 단일 행 선택 상태를 나타냅니다. `checkable`이 `true`일 때는 여러 행을 체크할 수 있으며, 체크된 항목 목록은 `selectionModel()` 메소드로 얻습니다. 