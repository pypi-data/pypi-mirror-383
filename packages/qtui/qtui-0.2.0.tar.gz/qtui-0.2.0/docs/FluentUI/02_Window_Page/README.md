# 02: 창 및 페이지 (Window & Page)

이 카테고리는 Fluent UI 애플리케이션의 기본 골격이 되는 창(Window)과 페이지(Page), 그리고 창과 관련된 주요 UI 요소들에 대한 문서를 포함합니다.

애플리케이션의 최상위 컨테이너를 정의하고, 기본적인 화면 구조를 구성하며, 창 간의 상호작용을 구현하는 데 필요한 컴포넌트들입니다.

## 포함된 문서

*   **[Window](./Window.md):**
    *   애플리케이션의 기본 최상위 창(`FluWindow`)입니다.
    *   프레임리스 스타일, 사용자 정의 앱 바, 테마 연동, 라우터 통합(실행 모드, 생명 주기 관리 등) 기능을 제공합니다.

*   **[Page](./Page.md):**
    *   주로 `NavigationView` 내부에 사용되어 개별 화면 콘텐츠를 담는 컨테이너입니다.
    *   페이지 단위의 UI 구성 및 관리에 사용됩니다.

*   **[AppBar](./AppBar.md):**
    *   `FluWindow` 상단 또는 하단에 표시되는 앱 바(`FluAppBar`)입니다.
    *   창 제어 버튼(닫기, 최소화, 최대화), 제목 표시, 사용자 정의 액션 등을 포함할 수 있습니다.

*   **[WindowResultLauncher](./WindowResultLauncher.md):**
    *   다른 창을 열고 해당 창으로부터 결과(데이터)를 받아 처리하는 데 사용되는 유틸리티 컴포넌트입니다.
    *   로그인 창, 파일 선택 창 등 결과 반환이 필요한 시나리오에 유용합니다.

## 주요 관계

*   `FluWindow`는 애플리케이션의 루트 요소로 사용되며, 내부에 `FluAppBar`나 페이지(`Page` 또는 `NavigationView`를 통한 `Page` 로딩)를 포함하는 경우가 많습니다.
*   `FluRouter`([핵심](../01_Core/Router.md))는 `FluWindow`의 생성, 탐색, 파라미터 전달 및 결과 처리를 관리하는 데 핵심적인 역할을 합니다.
*   `WindowResultLauncher`는 특정 `FluWindow`를 호출하고 `setResult()` 메소드를 통해 반환된 값을 처리합니다. 