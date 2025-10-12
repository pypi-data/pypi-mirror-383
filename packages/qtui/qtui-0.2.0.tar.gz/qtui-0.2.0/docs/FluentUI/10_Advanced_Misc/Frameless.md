# Fluent UI 프레임리스 헬퍼 (FluFrameless)

이 문서에서는 `FluentUI` 모듈 내부에서 사용되는 `FluFrameless` Python 클래스에 대해 설명합니다. 이 클래스는 `FluWindow`가 시스템 기본 창 테두리 없이 사용자 정의 UI(앱 바 포함)를 사용할 때, 필요한 창 제어 기능(이동, 크기 조정, 시스템 메뉴 등)을 구현하는 핵심적인 역할을 담당합니다.

**주의:** `FluFrameless`는 `FluWindow`의 내부 구현 세부 사항이며, **일반적으로 QML 개발자가 직접 생성하거나 사용할 필요가 없는 클래스입니다.** 이 문서는 `FluWindow`의 프레임리스 동작 원리를 이해하는 데 도움을 주기 위해 제공됩니다.

## `FluFrameless`의 역할

`FluFrameless` 클래스는 `QQuickItem`을 상속하여 QML 환경과 상호작용하고, `QAbstractNativeEventFilter`를 상속하여 운영체제의 네이티브 윈도우 메시지를 가로채고 처리합니다. 주요 역할은 다음과 같습니다:

*   **프레임리스 창 생성**: `FluWindow`가 프레임리스 모드(`useSystemAppBar: false`)일 때, Windows API (`SetWindowLongPtrW`, `SetWindowPos`, `DwmExtendFrameIntoClientArea` 등)를 호출하여 기본 창 테두리와 제목 표시줄을 제거하고 그림자 효과를 적용합니다.
*   **창 이동**: 사용자가 `FluAppBar`의 빈 공간을 드래그할 때 창 이동(`startSystemMove()`)이 시작되도록 QML 이벤트를 처리합니다.
*   **창 크기 조정**: 창 가장자리(`_margins` 영역)에서 마우스를 드래그할 때 해당 방향으로 창 크기 조정(`startSystemResize()`)이 시작되도록 QML 이벤트를 처리하고, 마우스 위치에 따라 적절한 크기 조정 커서 모양(`SizeVerCursor`, `SizeHorCursor` 등)을 표시합니다.
*   **네이티브 이벤트 처리 (Windows)**: `WM_NCCALCSIZE`, `WM_NCHITTEST`, `WM_GETMINMAXINFO` 등의 Windows 메시지를 가로채어, 프레임리스 상태에서 창이 올바르게 동작하도록(예: 클라이언트 영역 계산, 히트 테스트 영역 반환) 처리합니다.
*   **시스템 메뉴**: Alt+Space 키 조합이나 앱 바 우클릭 시 Windows 시스템 메뉴가 적절한 위치에 표시되고, 현재 창 상태(최대화, 크기 조정 가능 등)에 따라 메뉴 항목이 활성화/비활성화되도록 처리합니다.
*   **Windows 11 스냅 레이아웃 지원**: 최대화 버튼 위에 마우스를 올렸을 때 Windows 11의 스냅 레이아웃 메뉴가 나타나도록 네이티브 메시지를 적절히 처리합니다.
*   **상태 관리 연동**: `FluWindow`의 `fixSize`, `topmost` (항상 위) 등의 프로퍼티 변경에 따라 네이티브 창 속성을 변경하고 관련 동작을 제어합니다.
*   **히트 테스트 예외 처리**: `setHitTestVisible()` 메소드를 통해 앱 바 위의 버튼과 같이 창 이동이나 크기 조정을 시작하면 안 되는 영역을 지정받아 해당 영역에서의 상호작용을 무시합니다.

## 접근 방법

`FluFrameless` 객체는 `FluWindow` 내부에서 필요에 따라 자동으로 생성되고 관리됩니다. QML 개발자는 `FluWindow`의 프로퍼티(예: `fixSize`, `stayTop`, `appBar`, `disabled`)와 메소드(예: `showMaximized`, `setHitTestVisible`)를 통해 `FluFrameless`의 동작을 간접적으로 제어하게 됩니다.

## 기반 클래스

*   `QQuickItem` (from `PySide6.QtQuick`)
*   `QAbstractNativeEventFilter` (from `PySide6.QtCore`)

## 주요 (내부) 프로퍼티

(이 프로퍼티들은 주로 `FluWindow`와의 상호작용 및 내부 로직에 사용되며, 외부에서 직접 접근할 필요는 거의 없습니다.)

| 이름             | 타입             | 설명                                                                                               |
| :--------------- | :--------------- | :------------------------------------------------------------------------------------------------- |
| `appbar`         | `QQuickItem`     | 상호작용할 앱 바 아이템(`FluAppBar` 등)의 참조입니다.                                                    |
| `topmost`        | `bool`           | 창을 항상 위에 표시할지 여부입니다. `FluWindow`의 `stayTop` 프로퍼티와 연동됩니다.                                |
| `maximizeButton` | `QQuickItem`     | 앱 바 내의 최대화/복원 버튼 아이템 참조입니다. Windows 11 스냅 레이아웃 등에 사용됩니다.                                |
| `disabled`       | `bool`           | 프레임리스 기능의 활성화 여부입니다. `FluWindow`의 `useSystemAppBar` 프로퍼티 값에 따라 설정됩니다.                      |
| `fixSize`        | `bool`           | 창 크기 고정 여부입니다. `FluWindow`의 `fixSize` 프로퍼티와 연동됩니다.                                        |
| `_hitTestList`   | `list[QQuickItem]`| 마우스 히트 테스트 시 창 이동/크기 조정 동작을 발생시키지 않아야 할 앱 바 내의 아이템(주로 버튼) 목록입니다.                   |
| `_margins`       | `int`            | 창 가장자리에서 크기 조정을 감지할 영역의 픽셀 너비입니다. (기본값: 8)                                              |

## 주요 (내부) 메소드

(이 메소드들은 내부 로직이나 `FluWindow`로부터 호출되며, 외부에서 직접 호출할 필요는 거의 없습니다.)

*   `nativeEventFilter(eventType, message)`: `QAbstractNativeEventFilter` 인터페이스 구현. Windows 네이티브 메시지를 처리합니다.
*   `eventFilter(watched, event)`: `QObject` 이벤트 필터 인터페이스 구현. QML 마우스 이벤트 등을 처리하여 창 이동/크기 조정을 시작합니다.
*   `setHitTestVisible(val: QQuickItem)`: `_hitTestList`에 아이템을 추가합니다. `FluWindow`의 동명 메소드를 통해 호출됩니다.
*   `showMaximized()`, `showMinimized()`, `showNormal()`: 창 상태를 변경합니다. `FluWindow`의 동명 메소드를 통해 호출됩니다.
*   `_setWindowTopmost(topmost: bool)`: 창의 '항상 위' 속성을 네이티브 API를 통해 설정합니다.
*   `_showSystemMenu(point: QPoint)`: 지정된 위치에 시스템 메뉴를 표시합니다.
*   `_updateCursor(edges: int)`: 마우스 위치에 따라 적절한 커서 모양으로 변경합니다.
*   `onDestruction()`: 컴포넌트가 소멸될 때 필요한 정리 작업(예: 네이티브 이벤트 필터 제거)을 수행합니다. `FluWindow` 소멸 시 호출됩니다.

## 고유 시그널

`appbarChanged`, `topmostChanged` 등 QML 프로퍼티 바인딩 및 상태 동기화를 위한 시그널들이 정의되어 있으나, 주로 내부적으로 사용됩니다.

## 예제

`FluFrameless`는 직접 사용하는 클래스가 아니므로 별도의 사용 예제는 없습니다. `FluWindow`를 프레임리스 모드(기본값)로 사용하는 것이 `FluFrameless`를 사용하는 예시가 됩니다. 관련 예제는 `docs/FluentUI/Window.md` 문서를 참조하십시오.

## 관련 컴포넌트/객체

*   **`FluWindow`**: `FluFrameless`를 내부적으로 사용하여 프레임리스 기능을 구현하는 주 컴포넌트입니다.
*   **`FluAppBar`**: 프레임리스 창의 제목 표시줄 및 제어 버튼 영역을 제공하며, `FluFrameless`와 상호작용하여 창 이동 등을 처리합니다.
*   **`FluApp`**: `useSystemAppBar` 전역 설정을 통해 `FluFrameless`의 활성화 여부에 영향을 줍니다.
*   **`FluTools`**: 운영체제 감지(`isWin`, `isMacos`, `isWindows11OrGreater`) 등 유틸리티 기능을 제공합니다.

## 참고 사항

*   **내부 구현**: 다시 강조하지만, `FluFrameless`는 `FluWindow`의 프레임리스 기능을 위한 내부 구현입니다. QML 개발자는 `FluWindow` 수준에서 제공되는 인터페이스를 사용하면 됩니다.
*   **플랫폼 의존성**: 현재 `FluFrameless.py`의 코드는 Windows 플랫폼에 특화된 네이티브 API 호출(`ctypes` 사용)을 많이 포함하고 있습니다. 다른 운영체제에서는 Qt 자체의 프레임리스 기능이나 해당 플랫폼에 맞는 다른 방식의 처리가 적용될 수 있습니다. 