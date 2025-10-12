# 05: 입력 (Inputs)

이 카테고리는 사용자로부터 텍스트, 선택, 값, 날짜/시간 등 다양한 형태의 입력을 받기 위한 컨트롤들에 대한 문서를 포함합니다.

폼(Form) 구성, 설정 변경, 데이터 입력 등 사용자와 애플리케이션 간의 상호작용에 필수적인 요소들입니다.

## 포함된 문서

*   **[Buttons](./Buttons.md):** 클릭 가능한 다양한 스타일의 버튼 (기본, 강조, 하이퍼링크 등).
*   **[CheckBox](./CheckBox.md):** 하나 이상의 옵션을 선택/해제하는 체크 박스.
*   **[ComboBox](./ComboBox.md):** 드롭다운 목록에서 항목을 선택하는 콤보 박스.
*   **[RadioButton](./RadioButton.md):** 여러 옵션 중 하나만 선택하는 라디오 버튼.
*   **[Slider](./Slider.md):** 특정 범위 내의 값을 선택하는 슬라이더.
*   **[ToggleSwitch](./ToggleSwitch.md):** 켜기/끄기 상태를 전환하는 스위치.
*   **[TimePicker](./TimePicker.md):** 시간을 선택하는 컨트롤.
*   **[DatePicker](./DatePicker.md):** 날짜를 선택하는 컨트롤.
*   **[CalendarPicker](./CalendarPicker.md):** 달력 UI를 통해 날짜를 선택하는 컨트롤.
*   **[ColorPicker](./ColorPicker.md):** 색상을 선택하는 컨트롤.
*   **[RatingControl](./RatingControl.md):** 별점 등으로 등급을 매기는 컨트롤.
*   **[ShortcutPicker](./ShortcutPicker.md):** 키보드 단축키를 입력받는 컨트롤.
*   **[AutoSuggestBox](./AutoSuggestBox.md):** 입력 중 제안 목록을 보여주는 자동 완성 텍스트 상자.
*   **[Watermark](./Watermark.md):** `TextField`, `TextArea` 등 텍스트 입력 컨트롤에 플레이스홀더(안내 문구)를 표시하는 기능.
*   **[Captcha](./Captcha.md):** 스팸 방지 등을 위한 보안 문자 입력 컨트롤.

## 주요 관계

*   입력 컨트롤들은 주로 폼(Form) 내에서 사용되며, 사용자가 입력한 값은 상태 관리나 백엔드 로직으로 전달되어 처리됩니다.
*   `Watermark`는 다른 텍스트 기반 입력 컨트롤과 함께 사용되어 사용자 경험을 향상시킵니다. 