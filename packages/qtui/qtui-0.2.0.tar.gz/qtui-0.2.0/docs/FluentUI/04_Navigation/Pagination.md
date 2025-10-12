# Fluent UI 페이지네이션 컴포넌트

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluPagination` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 많은 양의 데이터를 여러 페이지로 나누어 표시하고 탐색하는 데 사용됩니다.

## 공통 임포트 방법

Fluent UI 페이지네이션 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
// 필요에 따라 Layouts, Controls 등 추가
import QtQuick.Layouts 1.15 
import QtQuick.Controls 2.15
```

---

## FluPagination

`FluPagination`은 대규모 데이터셋을 페이지 단위로 나누어 보여줄 때 사용되는 탐색 컨트롤입니다. 일반적으로 데이터 테이블이나 목록 하단에 위치하며, 사용자가 페이지 번호를 직접 클릭하거나 '이전'/'다음' 버튼을 사용하여 페이지를 이동할 수 있도록 합니다. 전체 항목 수(`itemCount`)와 페이지당 항목 수(`__itemPerPage`)를 기반으로 전체 페이지 수(`pageCount`)를 계산하고, 현재 페이지(`pageCurrent`)를 중심으로 지정된 개수(`pageButtonCount`)만큼의 페이지 번호 버튼을 표시합니다. 페이지 수가 많을 경우 중간 페이지 번호는 생략 기호(...)로 표시됩니다.

### 기반 클래스

`Item`

### 고유/특징적 프로퍼티

| 이름             | 타입        | 기본값                      | 설명                                                                                                                                                                    |
| :--------------- | :---------- | :-------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pageCurrent`    | `int`       | `0`                         | 현재 선택된 페이지 번호 (1부터 시작). 사용자가 페이지를 이동하면 이 값이 업데이트됩니다.                                                                                        |
| `itemCount`      | `int`       | `0`                         | 페이지네이션할 전체 항목의 개수. 이 값을 기준으로 `pageCount`가 계산됩니다.                                                                                               |
| `pageButtonCount`| `int`       | `5`                         | 표시할 페이지 번호 버튼의 최대 개수 (맨 처음과 맨 마지막 페이지 버튼 제외). 일반적으로 홀수를 사용하는 것이 보기 좋습니다.                                                                    |
| `__itemPerPage`  | `int`       | `10`                        | 페이지당 표시할 항목의 수. **주의**: 현재 버전에서는 이 값이 내부적으로 10으로 고정되어 있으며, 외부에서 직접 변경할 수 없습니다. `requestPage` 시그널의 `count` 파라미터로 이 값이 전달됩니다. |
| `pageCount`      | `readonly int`| (계산됨)                   | `itemCount`와 `__itemPerPage`를 기반으로 계산된 총 페이지 수 (`Math.ceil(itemCount / __itemPerPage)`).                                                                   |
| `previousText`   | `string`    | `qsTr("<Previous")`        | '이전' 페이지 이동 버튼에 표시될 텍스트.                                                                                                                               |
| `nextText`       | `string`    | `qsTr("Next>")`            | '다음' 페이지 이동 버튼에 표시될 텍스트.                                                                                                                               |
| `header`         | `Component` | `null`                      | 페이지네이션 컨트롤의 시작 부분(왼쪽)에 추가될 사용자 정의 QML 컴포넌트.                                                                                                   |
| `footer`         | `Component` | `null`                      | 페이지네이션 컨트롤의 끝 부분(오른쪽)에 추가될 사용자 정의 QML 컴포넌트.                                                                                                     |

### 고유 시그널

| 이름          | 파라미터                      | 반환타입 | 설명                                                                                                                                                              |
| :------------ | :---------------------------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `requestPage` | `int`: `page`, `int`: `count` | -        | 사용자가 다른 페이지 번호 버튼 또는 이전/다음 버튼을 클릭하여 페이지 이동이 필요할 때 발생하는 시그널입니다. 이동해야 할 목표 페이지 번호(`page`, 1부터 시작)와 페이지당 항목 수(`count`, 현재는 10)를 전달합니다. | 

### 고유 메소드

`FluPagination` 자체에 공개적으로 호출하도록 의도된 고유 메소드는 없습니다. 페이지 이동은 버튼 클릭과 `requestPage` 시그널을 통해 처리됩니다.

### 예제

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import FluentUI 1.0

ColumnLayout {
    spacing: 20
    width: 500

    FluPagination {
        id: pagination1
        itemCount: 1234 // 총 1234개의 항목
        pageCurrent: 1    // 초기 페이지는 1
        pageButtonCount: 5  // 최대 5개의 페이지 번호 버튼 표시
        
        // 페이지 이동 요청 시그널 처리 (실제 데이터 로딩 필요)
        onRequestPage: (page, count) => {
            console.log("요청된 페이지:", page, "페이지당 항목 수:", count)
            // 여기에 해당 페이지 데이터를 로드하는 로직 구현
            // 예: tableModel.loadPage(page, count)
            // 로딩 후 pagination1.pageCurrent = page 로 업데이트 필요
        }
    }

    FluPagination {
        itemCount: 88
        pageCurrent: 5
        pageButtonCount: 7
        previousText: "이전"
        nextText: "다음"
        // header/footer 예시 (페이지 정보 표시)
        footer: Component {
            FluText { text: qsTr("총 %1 페이지 중 %2").arg(parent.pageCount).arg(parent.pageCurrent); anchors.verticalCenter: parent.verticalCenter }
        }
        onRequestPage: (page, count) => {
            console.log("페이지 이동 요청:", page)
            // 데이터 로딩 로직...
        }
    }
}
```

### 참고 사항

*   **데이터 로딩**: `FluPagination` 자체는 페이지만 표시하고 이동 요청 시그널만 발생시킵니다. 실제 데이터 로딩 및 표시는 `requestPage` 시그널을 수신하여 애플리케이션 로직에서 구현해야 합니다. 시그널 핸들러 내에서 요청된 `page` 번호에 해당하는 데이터를 로드하고, 관련 뷰(예: `FluTableView`)를 업데이트해야 합니다.
*   **`__itemPerPage` 제한**: 현재 `FluPagination` 컴포넌트는 페이지당 항목 수를 외부에서 설정하는 기능을 제공하지 않으며 내부적으로 10으로 고정되어 있습니다. 따라서 `requestPage` 시그널 핸들러에서 데이터를 로드할 때는 페이지당 10개 항목을 기준으로 로직을 작성해야 합니다.
*   **페이지 버튼 표시**: `pageButtonCount` 값에 따라 표시되는 페이지 번호 버튼의 개수가 달라집니다. 현재 페이지를 중심으로 양옆에 버튼을 배치하며, 전체 페이지 수가 많으면 중간 번호는 생략(...)됩니다.
*   **`header` / `footer`**: 이 프로퍼티들을 사용하면 페이지네이션 컨트롤의 좌우에 추가적인 정보(예: 전체 페이지 수, 페이지당 항목 수 선택 드롭다운 등)를 표시하는 커스텀 UI를 추가할 수 있습니다. 