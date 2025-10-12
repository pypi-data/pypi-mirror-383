# Fluent UI 내비게이션 뷰 (FluNavigationView)

이 문서에서는 `FluentUI` 모듈의 핵심 내비게이션 컴포넌트인 `FluNavigationView`에 대해 설명합니다. 이 컴포넌트는 일반적으로 애플리케이션의 메인 창(`FluWindow`) 구조를 형성하며, 왼쪽의 접을 수 있는 탐색 메뉴 영역(Pane)과 오른쪽의 주 콘텐츠 표시 영역으로 구성됩니다.

## 공통 임포트 방법

`FluNavigationView` 컴포넌트를 사용하기 전에 QML 파일 상단에 다음 임포트 구문을 추가해야 합니다.

```qml
import QtQuick 2.15
import FluentUI 1.0
```

## 기본 구조

`FluNavigationView`를 사용하는 일반적인 구조는 다음과 같습니다:

1.  **`FluNavigationView` 인스턴스 생성**: 메인 윈도우(`FluWindow`) 내부에 `FluNavigationView` 컴포넌트를 배치합니다.
2.  **탐색 항목 정의**: 별도의 QML 파일에서 `FluObject`를 루트 아이템으로 하고 `pragma Singleton`을 선언하여 탐색 항목 그룹을 정의합니다. 이 파일 내부에 `FluPaneItem`, `FluPaneItemExpander`, `FluPaneItemSeparator`, `FluPaneItemHeader` 등을 사용하여 메뉴 구조를 만듭니다. (예: `ItemsOriginal.qml`, `ItemsFooter.qml`)
3.  **항목 연결**: 생성한 `FluNavigationView` 인스턴스의 `items` 프로퍼티와 `footerItems` 프로퍼티에 위에서 정의한 `FluObject` 싱글톤 객체를 할당합니다.
4.  **페이지 로딩 및 상호작용**: 사용자가 탐색 항목을 클릭하면, 해당 항목에 정의된 `onTap` 핸들러나 `url` 프로퍼티를 통해 `FluNavigationView`의 `push()` 메소드가 호출되어 콘텐츠 영역에 지정된 페이지가 로드됩니다. `pageMode` 설정에 따라 내부적으로 `StackView` 또는 `Loader`가 사용됩니다.
5.  **`displayMode` 설정**: `NavigationView`의 `displayMode` 프로퍼티를 설정하여 탐색 창의 모양을 제어합니다. `Auto` 모드를 사용하거나, 창 크기 변화에 따라 동적으로 `Compact`, `Minimal`, `Open` 모드로 변경하는 로직을 구현할 수 있습니다.

```qml
// MainWindow.qml (예시)
import QtQuick 2.15
import FluentUI 1.0
import "../global" // ItemsOriginal, ItemsFooter 등 싱글톤이 있는 경로

FluWindow {
    id: window
    // ... window properties ...
    
    FluNavigationView {
        id: navView
        anchors.fill: parent
        
        items: ItemsOriginal // 싱글톤 할당
        footerItems: ItemsFooter // 싱글톤 할당
        
        // displayMode를 창 너비에 따라 동적으로 변경 (Auto 모드를 사용하지 않는 경우 예시)
        displayMode: {
            if(window.width <= 700) return FluNavigationViewType.Minimal
            else if (window.width <= 900) return FluNavigationViewType.Compact
            else return FluNavigationViewType.Open
        }
        
        logo: "qrc:/example/res/image/favicon.ico"
        title: "My App"
        
        pageMode: FluNavigationViewType.Stack // 페이지 스택 사용
        
        Component.onCompleted: {
            // 싱글톤 내에서 NavigationView 인스턴스를 참조할 수 있도록 설정
            ItemsOriginal.navigationView = navView 
            ItemsFooter.navigationView = navView
            // 초기 페이지 설정
            setCurrentIndex(0)
        }
    }
}
```

---

## FluNavigationView

`FluNavigationView`는 앱의 주요 탐색 경로를 제공하는 컨테이너 컨트롤입니다. 사용자는 왼쪽의 탐색 창(Pane)을 통해 앱의 여러 섹션이나 페이지로 이동할 수 있습니다. 창 크기에 따라 탐색 창의 모양(완전히 열림, 아이콘만 표시, 숨김)이 자동으로 변경되는 반응형 레이아웃을 지원하며, 계층적인 메뉴 구조, 검색 기능, 페이지 스택 관리 등 다양한 기능을 제공합니다.

### 기반 클래스

`Item`

### 주요 프로퍼티

| 이름                         | 타입                    | 기본값                          | 설명                                                                                                                                                            |
| :--------------------------- | :---------------------- | :------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `items`                      | `FluObject`             | `null`                          | 주 탐색 항목들을 정의하는 `FluObject` 싱글톤 객체입니다. (필수 지정 권장)                                                                                             |
| `footerItems`                | `FluObject`             | `null`                          | 탐색 창 하단에 고정될 항목들을 정의하는 `FluObject` 싱글톤 객체입니다.                                                                                               |
| `displayMode`                | `FluNavigationViewType` | `FluNavigationViewType.Auto`    | 탐색 창의 표시 방식을 제어합니다 (`Auto`, `Minimal`, `Compact`, `Open`). `Auto`는 창 너비에 따라 자동으로 전환됩니다 (<=700: Minimal, <=900: Compact, >900: Open).                      |
| `pageMode`                   | `FluNavigationViewType` | `FluNavigationViewType.Stack`   | 페이지 탐색 방식을 결정합니다 (`Stack`: 내부 `StackView` 사용, `NoStack`: 내부 `Loader` 사용).                                                                       |
| `logo`                       | `url`                   | `undefined`                     | 탐색 창 상단 메뉴 버튼 옆(또는 Minimal 모드 시 상단 바)에 표시될 로고 이미지 URL입니다.                                                                                   |
| `title`                      | `string`                | ""                            | 로고 옆(또는 Minimal 모드 시 상단 바)에 표시될 텍스트입니다.                                                                                                       |
| `autoSuggestBox`             | `Component`             | `null`                          | 탐색 창 상단(Open/Compact 모드)에 표시될 자동 완성 검색 상자 컴포넌트입니다. (예: `FluAutoSuggestBox` 인스턴스)                                                                 |
| `actionItem`                 | `Component`             | `null`                          | `NavigationView` 상단 바의 오른쪽 영역에 표시될 사용자 정의 컴포넌트입니다.                                                                                        |
| `navCompactWidth`            | `int`                   | `50`                            | `Compact` 디스플레이 모드일 때 탐색 창의 너비입니다.                                                                                                              |
| `cellHeight`                 | `int`                   | `38`                            | 탐색 항목(Pane Item)의 기본 높이입니다.                                                                                                                          |
| `cellWidth`                  | `int`                   | `300`                           | `Open` 디스플레이 모드일 때 탐색 창의 너비입니다.                                                                                                                |
| `hideNavAppBar`              | `bool`                  | `false`                         | `NavigationView` 내부에 기본으로 포함된 상단 바 영역(뒤로가기 버튼, 메뉴 버튼, 로고, 타이틀 등 포함)을 숨길지 여부입니다.                                                              |
| `navItemRightMenu`           | `FluMenu`               | `null`                          | `FluPaneItem`에서 우클릭 시 표시될 기본 컨텍스트 메뉴 컴포넌트입니다. 개별 아이템에서 `menuDelegate`로 재정의 가능합니다.                                                               |
| `navItemExpanderRightMenu`   | `FluMenu`               | `null`                          | `FluPaneItemExpander`에서 우클릭 시 표시될 기본 컨텍스트 메뉴 컴포넌트입니다. 개별 아이템에서 `menuDelegate`로 재정의 가능합니다.                                                          |
| `buttonMenu`, `buttonBack`, `imageLogo` | `alias`          | (내부 아이템 참조)               | 내부의 메뉴 버튼, 뒤로가기 버튼, 로고 이미지 아이템에 대한 읽기 전용 별칭입니다. (주로 `FluWindow`에서 히트 테스트 설정 등에 사용)                                                                |
| `topPadding`                 | `int`                   | `0`                             | `NavigationView` 상단과 내부 앱 바 사이의 여백입니다. (예: macOS 환경 대응)                                                                                             |

### 주요 메소드

| 이름              | 파라미터                                    | 반환타입        | 설명                                                                                                                                                              |
| :---------------- | :------------------------------------------ | :-------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `push`            | `url: string`, `argument: var = {}`         | `void`          | 지정된 `url`의 QML 파일을 콘텐츠 영역에 로드합니다. `pageMode`가 `Stack`이면 `StackView`에 푸시하고, `NoStack`이면 `Loader`의 소스를 변경합니다. `argument`를 통해 페이지에 파라미터를 전달할 수 있습니다. |
| `collapseAll`     | -                                           | `void`          | 탐색 창 내의 모든 `FluPaneItemExpander` 항목을 접습니다.                                                                                                             |
| `setCurrentIndex` | `index: int`                                | `void`          | 프로그래밍 방식으로 `index`에 해당하는 탐색 항목을 선택하고, 해당 항목에 `url`이 정의되어 있으면 `push()`를 호출하여 페이지를 로드합니다.                                                              |
| `getItems`        | -                                           | `var` (array)   | 현재 `NavigationView`에 로드되어 처리된 모든 탐색 항목(내부 모델 데이터)의 리스트를 반환합니다.                                                                                   |
| `getCurrentIndex` | -                                           | `int`           | 현재 선택된 탐색 항목의 인덱스를 반환합니다.                                                                                                                     |
| `getCurrentUrl`   | -                                           | `string`        | 현재 콘텐츠 영역에 표시된 페이지의 URL을 반환합니다 (`pageMode`가 `Stack`일 경우 스택 최상단 항목의 URL).                                                                        |
| `startPageByItem` | `data: var` (e.g., `{ key: "itemKey" }`) | `void`          | 전달된 `data` 객체의 `key` 값과 일치하는 `key` 프로퍼티를 가진 `FluPaneItem`을 찾아 해당 항목을 선택하고 페이지를 로드합니다. (`autoSuggestBox` 등에서 활용)                                |

### 주요 시그널

| 이름         | 파라미터 | 반환타입 | 설명                             |
| :----------- | :------- | :------- | :------------------------------- |
| `logoClicked`| -        | -        | `logo` 이미지 클릭 시 발생합니다. | 

---

## 탐색 항목 정의 (FluPaneItem 등)

`FluNavigationView`의 탐색 메뉴는 `items` 및 `footerItems` 프로퍼티에 할당된 `FluObject` 싱글톤 객체 내부에 계층적으로 정의된 항목들로 구성됩니다. 이 항목들은 시각적 요소가 아닌 데이터 객체이며, `FluNavigationView` 내부의 `ListView` 델리게이트가 이 객체들의 프로퍼티를 읽어 실제 UI를 생성합니다.

*   **`FluObject` 싱글톤**: 탐색 항목들을 그룹화하고 전역적으로 접근 가능하도록 `pragma Singleton` 지시자와 함께 `FluObject`를 루트로 사용하는 QML 파일을 생성합니다. (예: `ItemsOriginal.qml`, `ItemsFooter.qml`)
    ```qml
    // ItemsOriginal.qml
    pragma Singleton
    import QtQuick 2.15
    import FluentUI 1.0
    
    FluObject {
        property var navigationView // NavigationView 인스턴스 참조 저장용
        property var paneItemMenu // 공용 컨텍스트 메뉴 참조 저장용
        
        FluPaneItem { /* ... */ }
        FluPaneItemExpander { /* ... */ }
        FluPaneItemSeparator{}
        FluPaneItemHeader{}
        // ... more items ...
    }
    ```

### FluPaneItem

`FluPaneItem`은 `FluNavigationView` 내에서 클릭 가능하며, 일반적으로 특정 페이지나 기능으로 사용자를 안내하는 데 사용되는 가장 기본적인 탐색 단위입니다. `QtObject`를 기반으로 하며, 아이콘, 텍스트, 뱃지 등을 표시하고 클릭 시 동작을 정의할 수 있습니다.

**주요 프로퍼티:**

| 이름           | 타입        | 기본값    | 설명                                                                                                                   |
| :------------- | :---------- | :-------- | :--------------------------------------------------------------------------------------------------------------------- |
| `key`          | `string`    | (자동생성) | 항목의 고유 식별자입니다. UUID로 자동 생성되며, `startPageByItem` 메소드 등을 통해 특정 항목을 식별하는 데 사용됩니다.                                |
| `visible`      | `bool`      | `true`    | 항목의 표시 여부입니다. `false`로 설정하면 `NavigationView`의 항목 목록에서 제외됩니다.                                                |
| `title`        | `string`    | `""`      | 항목에 표시될 주 텍스트입니다.                                                                                             |
| `url`          | `var`       | `undefined` | 항목 클릭 시 `push()` 메소드를 통해 로드할 페이지의 URL입니다. (예: `"qrc:/pages/MyPage.qml"`)                                         |
| `disabled`     | `bool`      | `false`   | 항목을 비활성화할지 여부입니다. 비활성화된 항목은 시각적으로 흐리게 표시되며 클릭할 수 없습니다.                                                     |
| `icon`         | `int`       | `undefined` | 항목 왼쪽에 표시될 아이콘입니다. `FluentIcons` 열거형의 값을 사용합니다. (예: `FluentIcons.Home`)                                        |
| `iconVisible`  | `bool`      | `true`    | 아이콘 영역의 표시 여부입니다. `false`로 설정하면 아이콘이 표시되지 않고 텍스트가 왼쪽으로 정렬됩니다.                                       |
| `infoBadge`    | `Component` | `null`    | 항목 오른쪽에 표시될 뱃지(Badge) 컴포넌트입니다. 일반적으로 `FluBadge` 인스턴스를 지정합니다.                                          |
| `count`        | `int`       | `0`       | `infoBadge`에서 참조할 수 있는 숫자 값입니다. `infoBadge` 내에서 `count` 프로퍼티를 바인딩하여 사용할 수 있습니다. (예: `FluBadge { count: item.count }`) |
| `onTapListener`| `var`       | `undefined` | 항목 클릭 시 실행될 JavaScript 함수입니다. 이 프로퍼티에 유효한 함수가 할당되면, `url` 프로퍼티나 `tap` 시그널을 통한 기본 동작(`push(url)`)은 무시되고 이 함수만 실행됩니다. |
| `iconDelegate` | `Component` | `null`    | 기본 `FluIcon` 대신 아이콘 영역에 표시될 사용자 정의 컴포넌트입니다. 더 복잡한 아이콘 표현이 필요할 때 사용합니다.                                  |
| `menuDelegate` | `Component` | `null`    | 항목 위에서 마우스 오른쪽 버튼 클릭 시 표시될 컨텍스트 메뉴 컴포넌트입니다. 일반적으로 `FluMenu` 인스턴스를 지정합니다. `NavigationView`의 `navItemRightMenu`보다 우선순위가 높습니다. |
| `editDelegate` | `Component` | `null`    | `showEdit` 프로퍼티가 `true`일 때 항목의 텍스트 영역에 표시될 편집용 컴포넌트입니다. 일반적으로 인라인 편집을 위해 `FluTextBox` 등을 지정합니다.    |
| `extra`        | `var`       | `undefined` | 항목과 관련된 추가적인 사용자 정의 데이터를 저장하기 위한 variant 타입 프로퍼티입니다. 객체 리터럴 등을 사용하여 다양한 정보를 저장할 수 있습니다.                |
| `showEdit`     | `bool`      | `false`   | `editDelegate` 컴포넌트를 표시하여 인라인 편집 모드로 전환할지 여부입니다.                                                             |

**고유 메소드:**

`FluPaneItem`에는 QML에서 직접 호출할 수 있는 고유 메소드가 없습니다.

**고유 시그널:**

| 이름   | 파라미터 | 반환타입 | 설명                                                                                             |
| :----- | :------- | :------- | :----------------------------------------------------------------------------------------------- |
| `tap`  | -        | -        | `onTapListener` 프로퍼티가 설정되지 **않았을 때**, 항목이 클릭되면 발생하는 시그널입니다. `FluNavigationView`는 내부적으로 이 시그널을 받아 `push(item.url)`를 호출합니다. |

### FluPaneItemExpander

`FluPaneItemExpander`는 내부에 다른 탐색 항목들(자식 항목)을 포함할 수 있으며, 사용자가 클릭하여 자식 항목들을 펼치거나 접을 수 있는 그룹핑 항목입니다. `FluObject`를 기반으로 하므로, QML 파일에서 `FluPaneItem`, `FluPaneItemSeparator` 등을 자식으로 직접 정의할 수 있습니다.

**주요 프로퍼티:**

| 이름           | 타입        | 기본값    | 설명                                                                                                                  |
| :------------- | :---------- | :-------- | :-------------------------------------------------------------------------------------------------------------------- |
| `key`          | `string`    | (자동생성) | 항목의 고유 식별자입니다. UUID로 자동 생성됩니다.                                                                            |
| `visible`      | `bool`      | `true`    | 항목의 표시 여부입니다. `false`로 설정하면 해당 Expander와 그 하위 항목들이 모두 표시되지 않습니다.                                     |
| `title`        | `string`    | `""`      | 항목에 표시될 주 텍스트입니다.                                                                                              |
| `icon`         | `var`       | `undefined` | 항목 왼쪽에 표시될 아이콘입니다. `FluentIcons` 열거형의 값을 사용합니다.                                                         |
| `disabled`     | `bool`      | `false`   | 항목을 비활성화할지 여부입니다. 비활성화된 항목은 시각적으로 흐리게 표시되며 확장/축소할 수 없습니다.                                            |
| `iconVisible`  | `bool`      | `true`    | 아이콘 영역의 표시 여부입니다.                                                                                             |
| `isExpand`     | `bool`      | `false`   | 현재 항목이 확장(펼쳐진) 상태인지 여부를 나타냅니다. 이 값을 변경하여 프로그래밍 방식으로 항목을 확장하거나 축소할 수 있습니다.                            |
| `showEdit`     | `bool`      | `false`   | `editDelegate` 컴포넌트를 표시하여 인라인 편집 모드로 전환할지 여부입니다.                                                            |
| `iconDelegate` | `Component` | `null`    | 기본 `FluIcon` 대신 아이콘 영역에 표시될 사용자 정의 컴포넌트입니다.                                                               |
| `menuDelegate` | `Component` | `null`    | 항목 위에서 마우스 오른쪽 버튼 클릭 시 표시될 컨텍스트 메뉴 컴포넌트입니다. (`FluMenu`) `NavigationView`의 `navItemExpanderRightMenu`보다 우선합니다. |
| `editDelegate` | `Component` | `null`    | `showEdit`가 `true`일 때 항목의 텍스트 영역에 표시될 편집용 컴포넌트입니다. (`FluTextBox` 등)                                         |

**고유 메소드:**

`FluPaneItemExpander`에는 QML에서 직접 호출할 수 있는 고유 메소드가 없습니다.

**고유 시그널:**

`FluPaneItemExpander`에는 QML에서 직접 연결하여 사용할 수 있는 고유 시그널이 없습니다.

### FluPaneItemSeparator

`FluPaneItemSeparator`는 탐색 항목 목록 내에서 시각적인 구분선을 표시하는 데 사용되는 비-상호작용 항목입니다. `QtObject`를 기반으로 합니다.

**주요 프로퍼티:**

| 이름      | 타입   | 기본값    | 설명                                                              |
| :-------- | :----- | :-------- | :---------------------------------------------------------------- |
| `key`     | `string`| (자동생성) | 항목의 고유 식별자입니다. UUID로 자동 생성됩니다.                        |
| `visible` | `bool`  | `true`    | 구분선의 표시 여부입니다. `false`로 설정하면 구분선이 그려지지 않습니다.         |
| `spacing` | `real`  | `undefined` | 구분선 위아래에 적용될 여백 값입니다. `NavigationView`의 델리게이트에서 사용됩니다. |
| `size`    | `int`   | `1`       | 구분선의 두께(픽셀 단위)입니다.                                            |

**고유 메소드:**

`FluPaneItemSeparator`에는 QML에서 직접 호출할 수 있는 고유 메소드가 없습니다.

**고유 시그널:**

`FluPaneItemSeparator`에는 QML에서 직접 연결하여 사용할 수 있는 고유 시그널이 없습니다.

### `FluPaneItemHeader`

`FluPaneItemHeader`는 탐색 항목 목록 내에서 섹션 제목이나 그룹 이름을 표시하는 데 사용되는 비-상호작용 헤더 아이템입니다. `QtObject`를 기반으로 합니다.

**주요 프로퍼티:**

| 이름      | 타입   | 기본값    | 설명                                                                     |
| :-------- | :----- | :-------- | :----------------------------------------------------------------------- |
| `key`     | `string`| (자동생성) | 항목의 고유 식별자입니다. UUID로 자동 생성됩니다.                               |
| `visible` | `bool`  | `true`    | 헤더의 표시 여부입니다. `false`로 설정하면 헤더 텍스트가 표시되지 않습니다.             |
| `title`   | `string`| `""`      | 헤더에 표시될 텍스트입니다. `NavigationView`의 델리게이트에서 이 텍스트를 표시합니다. |

**고유 메소드:**

`FluPaneItemHeader`에는 QML에서 직접 호출할 수 있는 고유 메소드가 없습니다.

**고유 시그널:**

`FluPaneItemHeader`에는 QML에서 직접 연결하여 사용할 수 있는 고유 시그널이 없습니다.

### `FluPaneItemEmpty` (내부 사용)

`FluPaneItemEmpty`는 주로 `FluNavigationView` 내부 구현에서 `footerItems` 영역과 `items` 영역 사이의 간격을 만들기 위해 사용되는 특수한 빈 항목입니다. `QtObject`를 기반으로 하며, 일반적인 애플리케이션 개발 시 **직접 사용할 필요는 없습니다.**

**주요 프로퍼티:**

| 이름      | 타입   | 기본값    | 설명                                        |
| :-------- | :----- | :-------- | :------------------------------------------ |
| `key`     | `string`| (자동생성) | 항목의 고유 식별자입니다. UUID로 자동 생성됩니다. |
| `visible` | `bool`  | `true`    | 항목의 공간 차지 여부를 결정합니다.             |

**고유 메소드:**

`FluPaneItemEmpty`에는 QML에서 직접 호출할 수 있는 고유 메소드가 없습니다.

**고유 시그널:**

`FluPaneItemEmpty`에는 QML에서 직접 연결하여 사용할 수 있는 고유 시그널이 없습니다.

---

## Display Modes

`displayMode` 프로퍼티는 탐색 창의 모양과 동작을 결정합니다.

*   **`Open`**: 탐색 창이 완전히 확장되어 아이콘과 텍스트 레이블이 모두 표시됩니다. 기본 너비는 `cellWidth`입니다.
*   **`Compact`**: 탐색 창이 좁게 표시되어 아이콘만 보입니다(`navCompactWidth`). 항목 위에 마우스를 올리면 툴팁이 나타납니다. `FluPaneItemExpander`를 클릭하면 하위 항목 목록이 팝업 메뉴 형태로 나타납니다.
*   **`Minimal`**: 탐색 창이 기본적으로 숨겨져 있습니다. 상단 바의 메뉴 버튼(햄버거 버튼)을 클릭하면 탐색 창이 콘텐츠 영역 위로 오버레이 형태로 나타납니다.
*   **`Auto` (기본값)**: `FluNavigationView`의 너비에 따라 자동으로 `Minimal` (너비 <= 700), `Compact` (700 < 너비 <= 900), `Open` (너비 > 900) 모드 사이를 전환합니다.

---

## Page Navigation (`pageMode`)

`pageMode` 프로퍼티는 사용자가 탐색 항목을 클릭했을 때 콘텐츠 영역에서 페이지가 어떻게 전환되는지를 결정합니다.

*   **`Stack` (기본값)**: 내부적으로 `StackView`를 사용합니다. `push(url)` 메소드는 새 페이지를 스택에 쌓습니다. 내비게이션 뷰 상단에 '뒤로가기' 버튼이 자동으로 활성화/비활성화되며, 사용자는 이를 통해 이전 페이지로 돌아갈 수 있습니다. 페이지 컴포넌트(`FluPage` 등)에 정의된 `launchMode` (`SingleInstance`, `SingleTask` 등 `FluPageType` 값)를 존중하여 복잡한 탐색 히스토리 관리가 가능합니다.
*   **`NoStack`**: 내부적으로 `Loader`를 사용합니다. `push(url)` 메소드는 단순히 `Loader`의 `source` 또는 `sourceComponent`를 교체합니다. 페이지 스택이나 히스토리 관리가 이루어지지 않으며, '뒤로가기' 버튼은 항상 비활성화됩니다. 각 탐색 항목 클릭 시 항상 새로운 페이지 인스턴스가 로드(또는 기존 인스턴스가 교체)됩니다.

---

## 예제

**1. `FluNavigationView` 기본 설정 (MainWindow.qml 내):**

```qml
FluNavigationView {
    id: navView
    anchors.fill: parent
    items: ItemsOriginal       // 항목 정의 싱글톤
    footerItems: ItemsFooter // 푸터 항목 정의 싱글톤
    logo: "qrc:/res/logo.png"
    title: "My Application"
    displayMode: FluNavigationViewType.Auto // 자동 모드 사용
    pageMode: FluNavigationViewType.Stack
    
    Component.onCompleted: {
        ItemsOriginal.navigationView = navView
        ItemsFooter.navigationView = navView
        setCurrentIndex(0) // 첫 번째 항목을 초기 페이지로 설정
    }
}
```

**2. 탐색 항목 정의 (ItemsOriginal.qml):**

```qml
pragma Singleton
import FluentUI 1.0

FluObject {
    property var navigationView
    
    FluPaneItem {
        key: "home"
        title: qsTr("Home")
        icon: FluentIcons.Home
        url: "qrc:/pages/HomePage.qml"
        onTap: navigationView.push(url) // 클릭 시 페이지 푸시
    }
    
    FluPaneItemSeparator{}

    FluPaneItemHeader{
        title: qsTr("INPUT")
    }

    FluPaneItemExpander {
        title: qsTr("Input Controls")
        icon: FluentIcons.CheckboxComposite
        
        FluPaneItem {
            key: "buttons"
            title: qsTr("Buttons")
            icon: FluentIcons.ButtonA
            url: "qrc:/pages/ButtonPage.qml"
            onTap: navigationView.push(url)
        }
        FluPaneItem {
            key: "textbox"
            title: qsTr("TextBox")
            icon: FluentIcons.TextField
            url: "qrc:/pages/TextBoxPage.qml"
            onTap: navigationView.push(url)
        }
    }
    // ... other items ...
}
```

**3. 검색 상자 연동:**

```qml
FluNavigationView {
    // ... other properties ...
    items: ItemsOriginal
    
    autoSuggestBox: FluAutoSuggestBox {
        placeholderText: qsTr("Search pages...")
        items: ItemsOriginal.getSearchData() // 싱글톤에서 검색 데이터 가져오기
        onItemClicked: (data) => {
            // 검색 결과 클릭 시 해당 key를 가진 페이지로 이동
            startPageByItem(data) 
        }
    }
}

// ItemsOriginal.qml 내부에 추가 (예시)
function getSearchData(){
    var arr = []
    var items = navigationView.getItems(); // NavigationView의 모든 항목 가져오기
    for(var i=0; i<items.length; i++){
        var item = items[i]
        if(item instanceof FluPaneItem && item.key){ // FluPaneItem이고 key가 있는 경우
            if (item.parent instanceof FluPaneItemExpander){
                arr.push({title: `${item.parent.title} -> ${item.title}`, key: item.key})
            } else {
                arr.push({title: item.title, key: item.key})
            }
        }
    }
    return arr
}
```

(더 자세한 사용 예시는 `example/FluentUI/full/` 내의 `MainWindow.qml`, `ItemsOriginal.qml`, `ItemsFooter.qml` 등을 참고하십시오.)

---

## 관련 컴포넌트/객체

*   **`FluWindow`**: `FluNavigationView`를 포함하는 주 창입니다.
*   **`FluObject`**: 탐색 항목들을 그룹화하는 데 사용되는 기본 QML 타입입니다.
*   **`FluPaneItem`**, **`FluPaneItemExpander`**, **`FluPaneItemSeparator`**, **`FluPaneItemHeader`**: 탐색 메뉴 구조를 정의하는 컴포넌트들입니다.
*   **`FluBadge`**: 탐색 항목 옆에 알림 개수 등을 표시하는 뱃지 컴포넌트입니다.
*   **`FluMenu`**: 탐색 항목 우클릭 시 표시될 컨텍스트 메뉴입니다.
*   **`FluAutoSuggestBox`**: 검색 기능 구현에 사용될 수 있는 자동 완성 입력 상자입니다.
*   **`FluPageType`**: `pageMode: Stack`일 때 페이지의 실행 모드(Launch Mode)를 정의하는 데 사용됩니다.
*   **`FluRouter`**: `NavigationView` 내의 페이지에서 다른 `FluWindow`를 열 때 사용될 수 있습니다.

## 참고 사항

*   `items` 또는 `footerItems`에 할당된 `FluObject` 싱글톤 QML 파일 내에서 `navigationView` 프로퍼티를 정의하고, `Component.onCompleted` 등에서 실제 `FluNavigationView` 인스턴스를 할당해주어야 각 항목의 `onTap` 등에서 `navigationView.push()`와 같은 메소드를 올바르게 호출할 수 있습니다.
*   `Auto` 디스플레이 모드는 반응형 UI를 쉽게 구현할 수 있도록 도와줍니다. 창 크기를 조절하면 탐색 창의 모양이 자동으로 변경됩니다.
*   `pageMode` 설정은 애플리케이션의 전체적인 탐색 경험(뒤로가기 버튼, 페이지 인스턴스 관리 등)에 큰 영향을 미치므로 신중하게 선택해야 합니다. 