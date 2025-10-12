# 09: 시각 효과 및 스타일링 (Visual Effects & Styling)

이 카테고리는 Fluent UI의 시각적 디자인 원칙을 구현하고 애플리케이션의 미적 완성도를 높이는 데 사용되는 효과, 스타일 요소, 및 관련 유틸리티에 대한 문서를 포함합니다.

단순한 컨트롤 배치 및 기능을 넘어 사용자 인터페이스에 깊이감, 재질감, 일관된 타이포그래피 등을 적용하는 데 중점을 둡니다.

## 포함된 문서

*   **[Acrylic](./Acrylic.md):**
    *   Fluent Design의 특징적인 아크릴(Acrylic) 재질 효과를 구현합니다.
    *   반투명한 배경에 블러(Blur) 및 노이즈 효과를 적용하여 깊이감과 컨텍스트를 제공합니다. 주로 창 배경이나 플라이아웃(Flyout) 메뉴 등에 사용됩니다.

*   **[Rectangle](./Rectangle.md):**
    *   QML의 기본 `Rectangle` 타입에 Fluent UI 테마(색상, 외곽선 등)를 적용하거나 관련 유틸리티 기능을 추가하여 활용하는 방법을 다룹니다.
    *   단순한 색상 배경, 테두리, 그림자 효과 등 기본적인 시각 요소 구성에 사용됩니다.

*   **[TextStyle](./TextStyle.md):**
    *   Fluent Design의 타이포그래피 시스템에 따라 미리 정의된 텍스트 스타일(글꼴, 크기, 두께 등)을 제공합니다. (`FluTextStyle` 열거형)
    *   애플리케이션 전체에서 일관된 텍스트 스타일을 쉽게 적용할 수 있도록 돕습니다.

## 주요 관계

*   `Acrylic` 효과는 주로 `FluWindow`([창 및 페이지](../02_Window_Page/Window.md))의 배경이나 `FluMenu`([메뉴](../08_Menu_Scrolling/Menu.md)) 등 임시로 나타나는 UI 요소의 배경에 적용됩니다.
*   `TextStyle`은 `FluText`([데이터 표시](../06_Data_Display/Text.md)) 컴포넌트나 다른 텍스트 기반 컨트롤의 `font` 속성에 적용되어 사용됩니다.
*   `FluTheme`([핵심](../01_Core/Theme.md))에서 정의된 색상 값들은 `Rectangle`이나 다른 시각 요소들의 색상 지정에 활용될 수 있습니다. 