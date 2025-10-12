# Fluent UI 자동 제안 상자 (FluAutoSuggestBox)

이 문서에서는 `FluentUI` 모듈에서 제공하는 `FluAutoSuggestBox` 컴포넌트에 대해 설명합니다. 이 컴포넌트는 사용자가 텍스트를 입력할 때 관련 제안 목록을 드롭다운 형태로 표시하여 빠르고 정확한 입력을 돕는 텍스트 입력 컨트롤입니다.

`FluAutoSuggestBox`는 `FluTextBox`를 기반으로 구현되어 텍스트 입력 기능과 함께 실시간 제안 기능을 제공합니다.

## 공통 임포트 방법

`FluAutoSuggestBox` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

---

## FluAutoSuggestBox

`FluAutoSuggestBox`는 사용자가 입력을 시작하면, 제공된 데이터 소스(`items`)를 바탕으로 입력 내용과 일치하는 항목들을 필터링하여 드롭다운 팝업 목록으로 보여줍니다. 사용자는 목록에서 원하는 항목을 클릭하여 선택할 수 있으며, 선택된 항목의 텍스트가 입력 상자에 자동으로 채워집니다. 이 기능은 검색창, 태그 입력, 사용자 이름 자동 완성 등 다양한 UI 시나리오에서 유용하게 사용될 수 있습니다.

### 기반 클래스

`FluTextBox` (from `FluentUI`)

`FluAutoSuggestBox`는 `FluTextBox`를 상속하므로, `FluTextBox`가 가진 모든 프로퍼티(예: `text`, `placeholderText`, `iconSource`), 메소드, 시그널을 그대로 사용할 수 있습니다.

### 고유/특징적 프로퍼티

| 이름        | 타입       | 기본값               | 설명                                                                                                                                                                                             |
| :---------- | :--------- | :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `items`     | `var`      | `[]`                 | 제안 목록을 구성하는 데이터 소스입니다. JavaScript 객체들의 배열이어야 합니다.                                                                                                                       |
| `emptyText` | `string`   | `qsTr("No results found")` | 필터링 결과 일치하는 제안 항목이 없을 경우, 드롭다운 팝업에 표시될 텍스트입니다.                                                                                                                   |
| `textRole`  | `string`   | `"title"`            | `items` 배열 내 각 객체에서 제안 목록의 각 항목에 표시될 텍스트 값을 가져올 때 사용할 프로퍼티(키)의 이름입니다.                                                                                              |
| `filter`    | `function` | (기본 필터 함수 제공)  | 사용자가 입력한 텍스트(`control.text`)를 기준으로 `items` 배열의 각 항목을 필터링하는 JavaScript 함수입니다. 함수는 `item` 객체를 인자로 받고, 해당 항목을 제안 목록에 포함시키려면 `true`를, 아니면 `false`를 반환해야 합니다. |

**기본 `filter` 함수 로직:**

```javascript
function(item) {
    // item 객체의 textRole 프로퍼티 값이 현재 입력된 텍스트(control.text)를 포함하는지 확인 (대소문자 구분)
    if (item[textRole].indexOf(control.text) !== -1) {
        return true;
    }
    return false;
}
```

### 고유 메소드

`FluAutoSuggestBox`에는 사용자가 직접 호출할 만한 고유 메소드가 없습니다. (내부적으로 `updateText(text)` 함수가 사용되지만, 이는 사용자가 제안 항목을 클릭했을 때 텍스트를 업데이트하면서 불필요한 팝업 재표시를 방지하기 위한 용도입니다.)

### 고유 시그널

| 이름          | 파라미터     | 반환타입 | 설명                                                                         |
| :------------ | :----------- | :------- | :--------------------------------------------------------------------------- |
| `itemClicked` | `data: var`  | -        | 사용자가 드롭다운 제안 목록에서 특정 항목을 마우스로 클릭했을 때 발생하는 시그널입니다. | `data` 파라미터는 선택된 항목에 해당하는 `items` 배열의 원본 JavaScript 객체입니다. |

---

## 예제

다음은 `FluNavigationView`의 검색 기능으로 `FluAutoSuggestBox`를 사용하는 예제입니다 (`MainWindow.qml`의 일부).

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import FluentUI 1.0
import "../global" // ItemsOriginal 모델 사용을 위함

// ...

FluNavigationView {
    id: nav_view
    // ... 다른 NavigationView 설정 ...

    // 네비게이션 뷰 상단에 위치할 자동 제안 상자 정의
    autoSuggestBox: FluAutoSuggestBox {
        // 검색 아이콘 설정 (FluTextBox 로부터 상속)
        iconSource: FluentIcons.Search 
        
        // 제안 목록 데이터 설정 (ItemsOriginal 모델에서 검색 가능한 데이터 가져오기)
        items: ItemsOriginal.getSearchData() 
        
        // 입력 상자에 표시될 플레이스홀더 텍스트 (FluTextBox 로부터 상속)
        placeholderText: qsTr("Search") 
        
        // 사용자가 제안 목록에서 항목을 클릭했을 때의 동작 정의
        onItemClicked: (data) => {
            // ItemsOriginal 모델의 함수를 호출하여 해당 페이지로 이동
            ItemsOriginal.startPageByItem(data)
        }
    }
    
    // ...
}
```

이 예제에서:
*   `FluAutoSuggestBox`는 `FluNavigationView`의 `autoSuggestBox` 프로퍼티에 할당되어 네비게이션 UI의 일부로 통합됩니다.
*   `iconSource`와 `placeholderText`는 기반 클래스인 `FluTextBox`의 프로퍼티를 사용하여 설정됩니다.
*   `items` 프로퍼티에는 `ItemsOriginal.getSearchData()` 함수의 반환값(페이지 정보 객체 배열)이 할당됩니다. 이 배열의 각 객체에는 `title` 프로퍼티가 포함되어 있어야 합니다 (기본 `textRole`이 `"title"`이므로).
*   사용자가 입력하면 `items` 배열이 기본 `filter` 함수에 의해 필터링되어 `title`에 입력 내용이 포함된 페이지만 제안 목록으로 표시됩니다.
*   사용자가 제안 목록에서 특정 페이지 항목을 클릭하면 `itemClicked` 시그널이 발생하고, 연결된 핸들러에서 `ItemsOriginal.startPageByItem(data)` 함수가 호출되어 해당 페이지로 네비게이션을 수행합니다. `data` 파라미터는 클릭된 항목에 대한 전체 페이지 정보 객체입니다.

---

## 참고 사항

*   **데이터 소스 (`items`)**: `items` 프로퍼티에는 JavaScript 객체들로 이루어진 배열을 제공해야 합니다. 각 객체는 최소한 `textRole` 프로퍼티로 지정된 이름의 키(기본값: `"title"`)를 가지고 있어야 하며, 이 키에 해당하는 값이 제안 목록에 표시됩니다. `itemClicked` 시그널 핸들러에서는 이 원본 객체 전체에 접근할 수 있으므로, 표시 텍스트 외에 필요한 다른 정보(예: 페이지 URL, ID 등)도 객체에 포함시켜 활용할 수 있습니다.
*   **필터링 사용자 정의 (`filter`)**: 기본 제공되는 `filter` 함수는 단순한 포함 여부(case-sensitive)만 확인합니다. 대소문자를 구분하지 않거나, 여러 필드를 조합하여 검색하거나, 더 복잡한 매칭 로직이 필요한 경우, 사용자 정의 JavaScript 함수를 `filter` 프로퍼티에 할당하여 구현할 수 있습니다.
*   **팝업 동작 및 스타일**: 사용자가 텍스트를 입력하면 자동으로 제안 목록 팝업이 나타납니다. 팝업의 최대 높이는 기본적으로 8개 항목 분량으로 제한되며, 내용이 넘칠 경우 수직 스크롤바(`FluScrollBar`)가 표시됩니다. 항목이 없을 경우 `emptyText`가 표시됩니다. 팝업은 사용자가 입력 영역 외 다른 곳을 클릭하거나, 포커스를 잃거나, 제안 항목을 선택하면 자동으로 닫힙니다. 팝업의 위치는 입력 상자 아래 또는 위 중 공간이 충분한 곳으로 자동 조정됩니다. 배경, 그림자, 항목의 호버/클릭 효과 등은 `FluentUI` 테마(`FluTheme`)를 따릅니다.
*   **`FluTextBox` 기능 활용**: `FluAutoSuggestBox`는 `FluTextBox`를 상속하므로, `FluTextBox`의 아이콘 표시 기능(`iconSource`), 텍스트 정렬, 패딩 등 다양한 프로퍼티와 기능을 그대로 사용할 수 있습니다. 